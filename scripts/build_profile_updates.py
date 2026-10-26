#!/usr/bin/env python3
"""Generate profile-setup/linkedin.md and profile-setup/orcid-update.md from
canonical data. Neither LinkedIn nor ORCID is touched automatically -- these
are just up-to-date drafts/checklists for Brian to apply by hand.
"""
from __future__ import annotations

import re
from pathlib import Path

from lib import dataio as D


def html_to_md(text: str) -> str:
    text = re.sub(r'<a href="([^"]+)">(.*?)</a>', r"[\2](\1)", text)
    return text.replace("&amp;", "&").replace("&#x27;", "'")

ROOT = Path(__file__).resolve().parents[1]
LINKEDIN_PATH = ROOT / "profile-setup" / "linkedin.md"
ORCID_PATH = ROOT / "profile-setup" / "orcid-update.md"


def primary_appointment(employment: dict) -> dict:
    for a in employment["appointments"]:
        if a.get("is_primary_current"):
            return a
    raise ValueError("no primary current appointment")


# ------------------------------------------------------------------ LinkedIn --

def render_linkedin(profile: dict, employment: dict, projects: dict, funding: dict) -> str:
    primary = primary_appointment(employment)
    ospo = primary.get("ospo")
    date_range = D.format_date_range(primary["start"], primary["end"], style="prose")

    headline = (
        f"{primary['title']} at {profile['institution']} · "
        f"{profile['tagline']}"
    )

    featured = sorted((p for p in projects["projects"] if p.get("featured")), key=lambda p: p["order"])
    project_lines = []
    for p in featured:
        link = p.get("website") or p["github"]
        project_lines.append(f"**{p['name']}** ({link})\n{p['blurb_cv']}")

    fund = funding["funded_projects"][0]

    experience_bullets = "\n".join(f"- {html_to_md(b)}" for b in primary["bullets"])

    ospo_block = ""
    if ospo:
        ospo_block = "\n\n" + html_to_md(ospo.get("current_description", ""))
        ospo_block += "\n\n" + html_to_md(ospo.get("cv_description", ""))


    return f"""# LinkedIn update draft

Generated from canonical data ({D.parse_ym(primary['start'])[0]}-current). Review before pasting into
LinkedIn -- this is a draft, not an automated update (LinkedIn is never
edited automatically).

## Headline

{headline}

## About

{profile['research_identity_summary']}

Current focus: {fund['project_title']} ({fund['years']}, {fund['role']} with {fund['pi']} and {fund['co_pi']}).

## Experience -- current

**{primary['title']}**
{primary['institution']} · {primary['unit']}
{date_range}
{experience_bullets}{ospo_block}

## Featured projects

{chr(10).join(project_lines)}

## Needs manual attention

- [ ] Confirm headline fits LinkedIn's character limit and trim if needed.
- [ ] Attach/update the CryoStack and ICESEE links as LinkedIn "Featured" media.
- [ ] Update past-position dates only if LinkedIn's existing entries drifted from data/employment.yml.
- [ ] Describe OSPO Research Software Engineer responsibilities within the Georgia Tech appointment; do not imply a second full-time appointment.
"""


# -------------------------------------------------------------------- ORCID --

def render_orcid(profile: dict, employment: dict, education: dict, publications: list[dict],
                  funding: dict, service: dict) -> str:
    primary = primary_appointment(employment)
    ospo = primary.get("ospo")

    lines = ["# ORCID update checklist", "",
             "Generated from canonical data. ORCID is never edited automatically -- "
             "use this as a checklist for https://orcid.org/0000-0002-0995-1051.", "",
             "## Employment", ""]

    for a in employment["appointments"]:
        date_range = D.format_date_range(a["start"], a["end"], a.get("display_date"), style="prose")
        status = "Needs update" if a.get("is_primary_current") or a.get("end") is None else "Already represented"
        lines.append(f"- [{'x' if status == 'Already represented' else ' '}] **{status}** — "
                     f"{a['title']}, {a['institution']} ({date_range})")

    if ospo:
        lines += ["", "### OSPO research software work", ospo.get("current_description", "")]


    lines += ["", "## Education / Qualifications", ""]
    for d in education["degrees"]:
        lines.append(f"- [x] Already represented — {d['degree']}, {d['institution']} ({d['year']})")

    lines += ["", "## Works", ""]
    for pub in publications:
        authors = D.join_authors(pub["authors"])
        if pub["status"] == "published":
            marker, status_label = "x", "Already represented (published)"
        elif pub["status"] == "submitted":
            marker, status_label = " ", "Needs update -- list as submitted/preprint, not published"
        else:
            marker, status_label = " ", "Needs update -- list as work-in-progress, not published"
        lines.append(f"- [{marker}] **{status_label}** — {authors}, “{html_to_md(pub['title'])}”")
    lines.append("")
    lines.append("**Do not mark any \"submitted\" or \"in-preparation\" entry above as published "
                 "until data/publications.bib says status: published.**")

    lines += ["", "## Funding", ""]
    for f in funding["funded_projects"]:
        lines.append(f"- [ ] Needs update — {f['title']} ({f['years']}), {f['role']}, "
                     f"PI {f['pi']}, award ${f['amount_usd']:,}")

    lines += ["", "## Professional activities / service", ""]
    for item in service["activities_associations_awards"]:
        if item["type"] in ("service", "membership"):
            plain = html_to_md(item["html"]).replace("<em>", "").replace("</em>", "")
            lines.append(f"- [ ] Needs update — {plain}")

    return "\n".join(lines) + "\n"


def main() -> None:
    profile = D.load_yaml("profile")
    employment = D.load_yaml("employment")
    education = D.load_yaml("education")
    projects = D.load_yaml("projects")
    publications = D.load_bib()
    funding = D.load_yaml("funding")
    service = D.load_yaml("service")

    linkedin = render_linkedin(profile, employment, projects, funding)
    changed = linkedin != (LINKEDIN_PATH.read_text(encoding="utf-8") if LINKEDIN_PATH.exists() else None)
    LINKEDIN_PATH.write_text(linkedin, encoding="utf-8")
    print(f"{'updated' if changed else 'unchanged'}: profile-setup/linkedin.md")

    orcid = render_orcid(profile, employment, education, publications, funding, service)
    changed = orcid != (ORCID_PATH.read_text(encoding="utf-8") if ORCID_PATH.exists() else None)
    ORCID_PATH.write_text(orcid, encoding="utf-8")
    print(f"{'updated' if changed else 'unchanged'}: profile-setup/orcid-update.md")


if __name__ == "__main__":
    main()
