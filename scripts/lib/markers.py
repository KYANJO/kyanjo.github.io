"""Utility for regenerating marked regions inside otherwise hand-authored
HTML/LaTeX files.

Each generated region is wrapped in a pair of comments:
    HTML:  <!--gen:NAME-->...content...<!--/gen:NAME-->
    TeX:   %gen:NAME ...content... %/gen:NAME

`insert_marker` is used once, by scripts/migrate_insert_markers.py, to wrap
the existing hand-authored content in place (so the first `replace_regions`
run is a byte-for-byte no-op). After that, only `replace_regions` is used.
"""
from __future__ import annotations

import re
from pathlib import Path


def html_open(name: str) -> str:
    return f"<!--gen:{name}-->"


def html_close(name: str) -> str:
    return f"<!--/gen:{name}-->"


def tex_open(name: str) -> str:
    return f"%gen:{name}\n"


def tex_close(name: str) -> str:
    return f"%/gen:{name}"


def insert_marker(text: str, name: str, exact_substring: str, kind: str = "html") -> str:
    """Wrap the first (and required-unique) occurrence of exact_substring in
    markers. Raises if it is missing or not unique. A no-op if this marker
    has already been inserted (safe to re-run)."""
    open_tag = html_open(name) if kind == "html" else tex_open(name)
    close_tag = html_close(name) if kind == "html" else tex_close(name)
    if open_tag in text:
        return text
    count = text.count(exact_substring)
    if count != 1:
        raise ValueError(f"marker {name!r}: expected exactly 1 occurrence, found {count}")
    return text.replace(exact_substring, open_tag + exact_substring + close_tag, 1)


def insert_marker_between(text: str, name: str, start_anchor: str, end_anchor: str,
                           kind: str = "html") -> str:
    """Insert markers around the content strictly between the end of
    start_anchor and the start of end_anchor (both excluded from the marked
    region, both must be unique in the file). No-op if already migrated."""
    open_tag = html_open(name) if kind == "html" else tex_open(name)
    close_tag = html_close(name) if kind == "html" else tex_close(name)
    if open_tag in text:
        return text
    if text.count(start_anchor) != 1:
        raise ValueError(f"marker {name!r}: start_anchor not unique ({text.count(start_anchor)} matches)")
    start_idx = text.index(start_anchor) + len(start_anchor)
    rest = text[start_idx:]
    if rest.count(end_anchor) != 1:
        raise ValueError(f"marker {name!r}: end_anchor not unique after start_anchor ({rest.count(end_anchor)} matches)")
    end_idx = start_idx + rest.index(end_anchor)
    return text[:start_idx] + open_tag + text[start_idx:end_idx] + close_tag + text[end_idx:]


def replace_regions(text: str, replacements: dict[str, str], kind: str = "html") -> tuple[str, set[str]]:
    """Replace the content between each marker pair with new content.
    Returns (new_text, names_found)."""
    found: set[str] = set()

    def _sub_html(m: re.Match) -> str:
        name = m.group("name")
        found.add(name)
        if name not in replacements:
            return m.group(0)
        return f"<!--gen:{name}-->{replacements[name]}<!--/gen:{name}-->"

    def _sub_tex(m: re.Match) -> str:
        name = m.group("name")
        found.add(name)
        if name not in replacements:
            return m.group(0)
        return f"%gen:{name}\n{replacements[name]}\n%/gen:{name}"

    if kind == "html":
        pattern = re.compile(r"<!--gen:(?P<name>[\w.-]+)-->.*?<!--/gen:(?P=name)-->", re.DOTALL)
        new_text = pattern.sub(_sub_html, text)
    else:
        pattern = re.compile(r"%gen:(?P<name>[\w.-]+)\n.*?%/gen:(?P=name)", re.DOTALL)
        new_text = pattern.sub(_sub_tex, text)
    return new_text, found


def all_marker_names(text: str, kind: str = "html") -> set[str]:
    if kind == "html":
        pattern = re.compile(r"<!--gen:([\w.-]+)-->")
    else:
        pattern = re.compile(r"%gen:([\w.-]+)\n")
    return set(pattern.findall(text))


def apply_to_file(path: Path, replacements: dict[str, str], kind: str = "html") -> bool:
    """Returns True if the file's content changed."""
    original = path.read_text(encoding="utf-8")
    new_text, found = replace_regions(original, replacements, kind=kind)
    missing = set(replacements) - found
    if missing:
        raise ValueError(f"{path}: markers not found for {sorted(missing)}")
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False
