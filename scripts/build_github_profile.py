#!/usr/bin/env python3
"""Regenerate profile-setup/README-for-KYANJO.md (the KYANJO/KYANJO GitHub
profile README) from canonical data. Kept concise and GitHub-appropriate --
not a copy of the CV.
"""
from __future__ import annotations

from pathlib import Path

from lib import dataio as D

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "profile-setup" / "README-for-KYANJO.md"


def primary_appointment(employment: dict) -> dict:
    for a in employment["appointments"]:
        if a.get("is_primary_current"):
            return a
    raise ValueError("no primary current appointment")


def render(profile: dict, employment: dict, projects: dict) -> str:
    primary = primary_appointment(employment)
    date_range = D.format_date_range(primary["start"], primary["end"], style="prose")

    software_lines = []
    readme_projects = [p for p in projects["projects"] if p.get("show_in_github_readme")]
    for p in sorted(readme_projects, key=lambda x: x["github_readme_order"]):
        if p.get("website"):
            link = f'[{p["name"]}]({p["website"]}) ([GitHub]({p["github"]}))'
        else:
            link = f'[{p["name"]}]({p["github"]})'
        software_lines.append(f'- {link}: {p["blurb_github"]}')

    nav = " · ".join(
        f"[{label}]({profile['website']}{path})"
        for label, path in [
            ("Research", "research/"), ("Software", "software/"),
            ("Publications", "publications/"), ("CV", "cv/"), ("Contact", "contact/"),
        ]
    )

    return f"""# {profile['name']}

**{primary['title']} · {primary['unit']} · {primary['institution']}**

{date_range}

## [Visit my research website →]({profile['website']})

{profile['research_identity_summary']}

{nav}

### Scientific software

{chr(10).join(software_lines)}

[Browse my repositories →]({profile['github_url']}?tab=repositories) · [Website source →]({profile['github_repo_url']})
"""


def main() -> bool:
    profile = D.load_yaml("profile")
    employment = D.load_yaml("employment")
    projects = D.load_yaml("projects")
    new_content = render(profile, employment, projects)
    old_content = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else None
    if new_content == old_content:
        print("unchanged: profile-setup/README-for-KYANJO.md")
        return False
    OUT_PATH.write_text(new_content, encoding="utf-8")
    print("updated: profile-setup/README-for-KYANJO.md")
    return True


if __name__ == "__main__":
    main()
