"""Renders each marked LaTeX region (cv/brian-kyanjo-cv.tex) from the same
canonical data used for the website. Reuses the \\entry / \\cvitem /
\\githublink macros already defined in the document's preamble -- this
module only ever emits macro calls and itemize bodies, never new preamble.

Unlike scripts/lib/render_html.py, the goal here is not byte-identical
reproduction of the pre-existing .tex (which was a known-stale snapshot --
see cv/index.html's former "PDF/LaTeX are an earlier snapshot" note, now
removed since this generator keeps them in sync). The goal is a compilable,
content-correct document that matches the web CV's facts.
"""
from __future__ import annotations

import re

from . import dataio as D
from . import render_html as RH

_ACCENTS = {"\u00ea": r"\^e"}


_GITHUB_PREFIX = "https://github.com/"


def _link_to_tex(m: re.Match) -> str:
    url, text = m.group(1), m.group(2)
    if url.startswith(_GITHUB_PREFIX) and text == "github.com/" + url[len(_GITHUB_PREFIX):]:
        path = url[len(_GITHUB_PREFIX):].replace("_", r"\_")
        return f"\\githublink{{{path}}}"
    return f"\\href{{{url}}}{{{text}}}"


def esc(text: str) -> str:
    """Convert an HTML-ish canonical-data fragment (as used by
    render_html.py: <em>, <strong>, <a href>, HTML entities, unicode
    dashes) into LaTeX source."""
    out = text
    out = out.replace("&#x27;", "'").replace("&amp;", r"\&")
    out = re.sub(r'<a href="([^"]+)">(.*?)</a>', _link_to_tex, out)
    out = re.sub(r"<em>(.*?)</em>", r"\\textit{\1}", out)
    out = re.sub(r"<strong>(.*?)</strong>", r"\\textbf{\1}", out)
    out = out.replace("<br>", r"\\")
    # This document uses "--" (never unicode en/em dash or "---") for every
    # such separator -- see the 21 existing " -- " occurrences in the
    # original source.
    out = out.replace("\u2013", "--").replace("\u2014", "--")
    for ch, repl in _ACCENTS.items():
        out = out.replace(ch, repl)
    out = out.replace("%", r"\%")
    return out


def prof_tie(name: str) -> str:
    """Add LaTeX non-breaking ties after title/initial abbreviations, e.g.
    'Prof. Babatunde J. Aboidun' -> 'Prof.\\ Babatunde J.\\ Aboidun', matching
    the original document's convention of tying every abbreviation period."""
    out = re.sub(r"^(Prof|Dr|Mr|Mrs|Ms)\. ", r"\1.\\ ", name)
    out = re.sub(r"\b([A-Z])\. ", r"\1.\\ ", out)
    return out


def itemize(items: list[str], itemsep: str = "2pt") -> str:
    body = "\n\n".join(f"\\item {esc(item)}" for item in items)
    return f"\\begin{{itemize}}[leftmargin=1.2em, itemsep={itemsep}, topsep=2pt]\n\n{body}\n\n\\end{{itemize}}"


# --------------------------------------------------------------- sections --

def professional_summary(profile: dict) -> str:
    return esc(profile["professional_summary"].strip())


def education(education_data: dict) -> str:
    entries = []
    for d in education_data["degrees"]:
        entries.append(
            f'\\entry{{{d["institution"]}}}{{{d["year"]}}}\n'
            f'{{{d["degree"]}}}\n'
            "{\n"
            f'\\textbf{{{d["detail_label"]}:}}\n'
            f'\\textit{{{esc(d["detail_title"])}}}\\\\\n'
            f'\\textbf{{Advisor:}} {prof_tie(d["advisor"])}\n'
            "}"
        )
    return "\n\n".join(entries)


def technical_skills(profile: dict) -> str:
    lines = []
    for row in profile["technical_skills"]:
        items = row["items"]
        if row["label"] == "Additional":
            # This document renders the LaTeX logo, not the literal word.
            items = re.sub(r"\bLaTeX\b", r"\\LaTeX", items)
        lines.append(f'\\cvitem{{{row["label"]}}}{{{esc(items)}}}')
    return "\n\n".join(lines)


def _experience_entry(profile: dict, appointment: dict) -> str:
    date_range = D.format_date_range(
        appointment["start"], appointment["end"], appointment.get("display_date"), style="tex"
    )
    body_parts = []
    if appointment.get("ospo"):
        description = appointment["ospo"].get("cv_description")
        if description:
            body_parts.append(esc(description))
        else:
            intro = RH.ospo_intro_sentences(profile, appointment)
            tail = appointment["ospo"]["cv_activities_sentence"]
            body_parts.append(esc(f"{intro} {tail}"))
    if appointment.get("previous_role_note"):
        body_parts.append(f'\\textbf{{Previous appointment:}} {esc(appointment["previous_role_note"])}')
    bullets = appointment.get("bullets") or []
    if bullets:
        body_parts.append(itemize(bullets, itemsep="2pt"))
    body = "\n\n".join(body_parts)
    return (
        f'\\entry{{{appointment["institution"]}}}{{{date_range}}}\n'
        f'{{{appointment["title"]}}}\n'
        "{\n"
        f"{body}\n"
        "}"
    )


def professional_experience(profile: dict, employment: dict) -> str:
    return "\n\n\n".join(_experience_entry(profile, a) for a in employment["appointments"])


def funded_projects(funding: dict) -> str:
    items = []
    for p in funding["funded_projects"]:
        amount = f'\\${p["amount_usd"]:,}'
        items.append(
            f'\\textbf{{{esc(p["title"])}}},\n'
            f'\\textit{{{esc(p["project_title"])}}}, {esc(p["years"])}.\\\\\n'
            f'Award: {amount}. PI: {p["pi"]}; Co-PI: {p["co_pi"]};\n'
            f'Co-Investigator: {p["co_investigator"]}. {esc(p["description"])}'
        )
    return itemize(items, itemsep="3pt")


def scientific_software(projects: dict) -> str:
    ordered = sorted(projects["projects"], key=lambda p: p["cv_order"])
    items = []
    for p in ordered:
        name = p.get("cv_display_name", p["name"])
        link = (
            f'\\href{{{p["website"]}}}{{Visit {p["name"]}}} \\textbar\\ \\githublink{{{p["github"].replace("https://github.com/", "")}}}'
            if p.get("website")
            else f'\\githublink{{{p["github"].replace("https://github.com/", "")}}}'
        )
        items.append(f'\\textbf{{{name}}} --\n{esc(p["blurb_cv"])}\\\\\n{link}')
    return itemize(items, itemsep="4pt")


def publications(pubs: list[dict]) -> str:
    items = []
    for pub in pubs:
        authors = D.join_authors(pub["authors"])
        status = pub.get("status")
        if status == "submitted":
            middle = f'Submitted to {esc(pub["venue"])}.' if pub.get("venue") else "Submitted."
        elif status == "in-preparation":
            middle = "In preparation."
        elif status == "published":
            middle = f'{esc(pub.get("venue") or pub.get("year") or "Published")}.'
        else:
            raise ValueError(f"{pub['key']}: unknown status {status!r}")
        line = f'{authors}.\n\\textit{{{esc(pub["title"])}}}.\n{middle}'
        if pub.get("url") and pub.get("doi"):
            line += f'\n\\doilink{{{pub["doi"]}}}.'
        elif pub.get("url"):
            line += f'\n\\href{{{pub["url"]}}}{{Read manuscript}}.'
        items.append(line)
    return itemize(items, itemsep="4pt")


def simple_list(items: list[dict], itemsep: str = "2pt") -> str:
    return itemize([item["html"] for item in items], itemsep=itemsep)


def references(refs: dict) -> str:
    items = [
        f'{prof_tie(r["name"])},\n{esc(r["institution"])} --\n\\emaillink{{{r["email"]}}}'
        for r in refs["references"]
    ]
    return itemize(items, itemsep="3pt")
