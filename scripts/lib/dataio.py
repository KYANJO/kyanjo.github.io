"""Loading and light parsing of the canonical data/ files.

No external deps besides PyYAML. The BibTeX reader below is intentionally
minimal: it only understands the flat, single-line-field style used in
data/publications.bib (see the comment at the top of that file). It is not
a general BibTeX parser.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

MONTH_ABBREV = {
    1: "Jan.", 2: "Feb.", 3: "Mar.", 4: "Apr.", 5: "May", 6: "June",
    7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.", 11: "Nov.", 12: "Dec.",
}

MONTH_FULL = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
}


def load_yaml(name: str) -> dict:
    path = DATA_DIR / f"{name}.yml"
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


_BIB_ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,(?P<body>.*?)\n\}", re.DOTALL)
_BIB_FIELD_RE = re.compile(r"(?P<field>\w+)\s*=\s*\{(?P<value>.*?)\}\s*,?\s*$", re.MULTILINE)


def load_bib(path: Path | None = None) -> list[dict]:
    path = path or (DATA_DIR / "publications.bib")
    text = path.read_text(encoding="utf-8")
    entries = []
    for m in _BIB_ENTRY_RE.finditer(text):
        fields: dict[str, Any] = {"key": m.group("key"), "bibtype": m.group("type")}
        for fm in _BIB_FIELD_RE.finditer(m.group("body")):
            value = fm.group("value").strip()
            fields[fm.group("field").lower()] = value
        if "author" in fields:
            fields["authors"] = [a.strip() for a in fields["author"].split(" and ")]
        entries.append(fields)
    entries.sort(key=lambda e: (int(e.get("order", 10_000)), e["key"]))
    return entries


def join_authors(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def parse_ym(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    year, month = value.split("-")
    return int(year), int(month)


def format_month_year(value: str, style: str = "html") -> str:
    """value: 'YYYY-MM'. style: 'html' (abbreviated month, real en dash with
    spaces), 'tex' (abbreviated month, LaTeX tie, '--' range dash), or
    'prose' (full month name, e.g. for a sentence like "September 2026")."""
    year, month = parse_ym(value)
    if style == "prose":
        return f"{MONTH_FULL[month]} {year}"
    month_str = MONTH_ABBREV[month]
    if style == "tex":
        return f"{month_str}\\ {year}"
    return f"{month_str} {year}"


def format_date_range(start: str, end: str | None, display_date: str | None = None,
                       style: str = "html") -> str:
    if display_date:
        return display_date
    if style == "tex":
        dash = " -- "
    elif style == "prose":
        dash = "–"
    else:
        dash = " – "
    start_str = format_month_year(start, style)
    end_str = "Present" if end is None else format_month_year(end, style)
    return f"{start_str}{dash}{end_str}"
