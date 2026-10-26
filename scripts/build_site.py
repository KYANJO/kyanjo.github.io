#!/usr/bin/env python3
"""Regenerate the marked (<!--gen:NAME-->) regions of the website's HTML
pages from data/*.yml and data/publications.bib.

Safe to run repeatedly: if canonical data hasn't changed, output is
byte-identical (idempotent). Only the content between marker comments is
touched; everything else (layout, CSS, JS, images, nav, page-specific
narrative) is left exactly as hand-authored.
"""
from __future__ import annotations

from pathlib import Path

from lib import dataio as D
from lib import render_html as R
from lib.markers import apply_to_file

ROOT = Path(__file__).resolve().parents[1]


def load_all() -> dict:
    return {
        "profile": D.load_yaml("profile"),
        "employment": D.load_yaml("employment"),
        "education": D.load_yaml("education"),
        "projects": D.load_yaml("projects"),
        "publications": D.load_bib(),
        "talks": D.load_yaml("talks"),
        "service": D.load_yaml("service"),
        "funding": D.load_yaml("funding"),
        "references": D.load_yaml("references"),
    }


def build(data: dict) -> dict[str, bool]:
    profile, employment, education = data["profile"], data["employment"], data["education"]
    projects, publications = data["projects"], data["publications"]
    talks, service, funding, references = data["talks"], data["service"], data["funding"], data["references"]

    common = {
        "json-ld": R.json_ld(profile),
        "footer-links": R.footer_links(profile),
    }

    changed: dict[str, bool] = {}

    def apply(rel_path: str, extra: dict[str, str]) -> None:
        changed[rel_path] = apply_to_file(ROOT / rel_path, {**common, **extra})

    apply("index.html", {
        "home-project-grid": R.home_project_grid(projects),
    })

    apply("research/index.html", {
        "research-education": R.education_section(education),
        "research-funded-project": R.funded_projects_list(funding),
    })

    apply("software/index.html", {
        "sw-cryostack-detail": R.sw_cryostack_detail(projects),
        "sw-cryostack-applications": R.sw_cryostack_applications(projects),
        "sw-icesee-detail": R.sw_icesee_detail(projects),
        "sw-geoflood-detail": R.sw_geoflood_detail(projects),
        "sw-gt-dare-detail": R.sw_gt_dare_detail(projects),
        "sw-supporting-software": R.sw_supporting_software(projects),
    })

    apply("publications/index.html", {
        "publications-list": R.publications_list(publications),
    })

    apply("talks/index.html", {
        "talks-invited": R.simple_html_list(talks["invited_talks"]),
        "talks-posters": R.simple_html_list(talks["conference_posters"]),
        "talks-conferences": R.simple_html_list(talks["conferences_and_short_courses"]),
        "talks-activities": R.simple_html_list(service["activities_associations_awards"]),
        "talks-ospo": R.talks_ospo_section(profile, employment),
    })

    apply("cv/index.html", {
        "cv-page-intro-lead": R.cv_page_intro_lead(profile, employment),
        "cv-contact-line": R.cv_contact_line(profile),
        "cv-professional-summary": R.cv_professional_summary(profile),
        "cv-education": R.education_section(education),
        "cv-technical-skills": R.cv_technical_skills(profile),
        "cv-professional-experience": R.cv_professional_experience(profile, employment),
        "cv-funded-projects": R.funded_projects_list(funding),
        "cv-scientific-software": R.cv_scientific_software_list(projects),
        "cv-publications": R.publications_list(publications),
        "cv-conferences": R.simple_html_list(talks["conferences_and_short_courses"]),
        "cv-posters": R.simple_html_list(talks["conference_posters"]),
        "cv-invited-talks": R.simple_html_list(talks["invited_talks"]),
        "cv-activities": R.simple_html_list(service["activities_associations_awards"]),
        "cv-references": R.references_list(references),
    })

    apply("contact/index.html", {
        "contact-appointment": R.contact_appointment(profile, employment),
    })

    apply("404.html", {})

    return changed


def main() -> None:
    data = load_all()
    changed = build(data)
    any_changed = any(changed.values())
    for path, was_changed in changed.items():
        print(f"{'updated' if was_changed else 'unchanged'}: {path}")
    if not any_changed:
        print("build_site: no changes (already up to date)")


if __name__ == "__main__":
    main()
