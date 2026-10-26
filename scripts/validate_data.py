#!/usr/bin/env python3
"""Validate data/*.yml and data/publications.bib for obvious profile
mistakes before anything is generated from them.

Exits non-zero (and prints every problem found, not just the first) if
anything is invalid. Intentionally small and dependency-free beyond PyYAML.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import dataio as D

URL_RE = re.compile(r"^https?://[^\s]+$")
YM_RE = re.compile(r"^\d{4}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Problems:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, msg: str) -> None:
        self.items.append(msg)

    def check(self, ok: bool, msg: str) -> None:
        if not ok:
            self.add(msg)


def is_valid_ym(value) -> bool:
    if not isinstance(value, str) or not YM_RE.match(value):
        return False
    month = int(value.split("-")[1])
    return 1 <= month <= 12


def validate_profile(profile: dict, p: Problems) -> None:
    required = ["name", "current_title", "institution", "unit", "email", "website",
                "github_url", "orcid_url", "linkedin_url"]
    for field in required:
        p.check(bool(profile.get(field)), f"profile.yml: missing required field '{field}'")
    for field in ["website", "github_url", "github_repo_url", "orcid_url", "linkedin_url"]:
        val = profile.get(field)
        if val:
            p.check(bool(URL_RE.match(val)), f"profile.yml: '{field}' is not a valid URL: {val!r}")
    if profile.get("email"):
        p.check(bool(EMAIL_RE.match(profile["email"])), f"profile.yml: invalid email {profile['email']!r}")


def validate_employment(employment: dict, p: Problems) -> None:
    appointments = employment.get("appointments", [])
    ids = [a.get("id") for a in appointments]
    dupes = {i for i in ids if ids.count(i) > 1}
    p.check(not dupes, f"employment.yml: duplicate appointment id(s): {sorted(dupes)}")

    primary = [a for a in appointments if a.get("is_primary_current")]
    if not employment.get("allow_multiple_primary_current"):
        p.check(len(primary) == 1,
                 f"employment.yml: expected exactly one is_primary_current appointment, found {len(primary)}")

    for a in appointments:
        aid = a.get("id", "<no id>")
        for field in ["title", "institution", "start"]:
            p.check(bool(a.get(field)), f"employment.yml[{aid}]: missing required field '{field}'")
        if a.get("start") and not a.get("display_date"):
            p.check(is_valid_ym(a["start"]), f"employment.yml[{aid}]: invalid start date {a.get('start')!r} (want YYYY-MM)")
        end = a.get("end")
        if end is not None and not a.get("display_date"):
            p.check(is_valid_ym(end), f"employment.yml[{aid}]: invalid end date {end!r} (want YYYY-MM or null)")
        if end is not None and is_valid_ym(a.get("start")) and is_valid_ym(end):
            p.check(a["start"] <= end, f"employment.yml[{aid}]: start {a['start']!r} is after end {end!r}")
        ospo = a.get("ospo")
        if ospo:
            for field in ["program", "effort_pct", "start", "end", "continuation_clause",
                          "activities", "talks_activities_sentence", "cv_activities_sentence"]:
                p.check(field in ospo, f"employment.yml[{aid}].ospo: missing required field '{field}'")
            if "effort_pct" in ospo:
                p.check(0 < ospo["effort_pct"] <= 100,
                         f"employment.yml[{aid}].ospo: effort_pct {ospo['effort_pct']!r} out of range")
            for f in ("start", "end"):
                if f in ospo:
                    p.check(is_valid_ym(ospo[f]), f"employment.yml[{aid}].ospo: invalid {f} {ospo[f]!r}")


def validate_education(education: dict, p: Problems) -> None:
    for d in education.get("degrees", []):
        for field in ["institution", "year", "degree", "advisor"]:
            p.check(bool(d.get(field)), f"education.yml[{d.get('institution', '?')}]: missing '{field}'")


def validate_projects(projects: dict, p: Problems) -> None:
    items = projects.get("projects", [])
    ids = [x.get("id") for x in items]
    dupes = {i for i in ids if ids.count(i) > 1}
    p.check(not dupes, f"projects.yml: duplicate project id(s): {sorted(dupes)}")

    orders = [x.get("order") for x in items]
    p.check(len(orders) == len(set(orders)), "projects.yml: duplicate 'order' values")
    cv_orders = [x.get("cv_order") for x in items]
    p.check(len(cv_orders) == len(set(cv_orders)), "projects.yml: duplicate 'cv_order' values")

    readme_items = [x for x in items if x.get("show_in_github_readme")]
    for x in readme_items:
        p.check("github_readme_order" in x,
                 f"projects.yml[{x.get('id')}]: show_in_github_readme is true but 'github_readme_order' is missing")
    readme_orders = [x.get("github_readme_order") for x in readme_items]
    p.check(len(readme_orders) == len(set(readme_orders)), "projects.yml: duplicate 'github_readme_order' values")

    for proj in items:
        pid = proj.get("id", "<no id>")
        p.check(bool(proj.get("github") or proj.get("website")),
                 f"projects.yml[{pid}]: needs at least one of 'github' or 'website'")
        for field in ("github", "website", "docs_url"):
            val = proj.get(field)
            if val:
                p.check(bool(URL_RE.match(val)), f"projects.yml[{pid}].{field}: invalid URL {val!r}")
        for app in proj.get("applications", []):
            aid = app.get("id", "<no id>")
            p.check(bool(URL_RE.match(app.get("url", ""))),
                     f"projects.yml[{pid}].applications[{aid}]: invalid URL {app.get('url')!r}")


ALLOWED_STATUS = {"submitted", "in-preparation", "published"}


def validate_publications(pubs: list[dict], p: Problems) -> None:
    keys = [x["key"] for x in pubs]
    dupes = {k for k in keys if keys.count(k) > 1}
    p.check(not dupes, f"publications.bib: duplicate citation key(s): {sorted(dupes)}")

    seen_titles: dict[str, str] = {}
    for pub in pubs:
        key = pub["key"]
        status = pub.get("status")
        p.check(status in ALLOWED_STATUS,
                 f"publications.bib[{key}]: status must be one of {sorted(ALLOWED_STATUS)}, got {status!r}")
        p.check(bool(pub.get("title")), f"publications.bib[{key}]: missing title")
        p.check(bool(pub.get("authors")), f"publications.bib[{key}]: missing author(s)")
        if status == "published":
            p.check(bool(pub.get("venue") or pub.get("year")),
                     f"publications.bib[{key}]: status=published but no 'venue' or 'year' to display")
        # Guard against exactly the mistake this repo was warned about: a
        # manuscript/preprint (e.g. a JOSS submission) marked as published
        # before it actually is.
        if "joss" in pub.get("title", "").lower() or "joss" in key.lower():
            p.check(status != "published",
                     f"publications.bib[{key}]: looks like a JOSS submission but status=published -- "
                     "only set this once it is actually accepted/published")
        title_norm = re.sub(r"\W+", " ", pub.get("title", "")).strip().lower()
        if title_norm:
            if title_norm in seen_titles:
                p.add(f"publications.bib: possible duplicate publication -- "
                      f"'{key}' and '{seen_titles[title_norm]}' have the same title")
            else:
                seen_titles[title_norm] = key


def validate_talks_and_service(talks: dict, service: dict, p: Problems) -> None:
    for list_name in ["invited_talks", "conference_posters", "conferences_and_short_courses"]:
        for i, item in enumerate(talks.get(list_name, [])):
            p.check(bool(item.get("html")), f"talks.yml[{list_name}][{i}]: missing 'html'")
    for i, item in enumerate(service.get("activities_associations_awards", [])):
        p.check(bool(item.get("html")), f"service.yml[activities_associations_awards][{i}]: missing 'html'")


def validate_funding(funding: dict, p: Problems) -> None:
    for proj in funding.get("funded_projects", []):
        fid = proj.get("id", "<no id>")
        for field in ["title", "project_title", "years", "amount_usd", "pi", "description"]:
            p.check(bool(proj.get(field)) or proj.get(field) == 0,
                     f"funding.yml[{fid}]: missing '{field}'")
        if "amount_usd" in proj:
            p.check(isinstance(proj["amount_usd"], (int, float)) and proj["amount_usd"] > 0,
                     f"funding.yml[{fid}]: amount_usd must be a positive number")


def validate_references(references: dict, p: Problems) -> None:
    for ref in references.get("references", []):
        p.check(bool(EMAIL_RE.match(ref.get("email", ""))),
                 f"references.yml[{ref.get('name', '?')}]: invalid email {ref.get('email')!r}")


def main() -> int:
    p = Problems()
    try:
        profile = D.load_yaml("profile")
        employment = D.load_yaml("employment")
        education = D.load_yaml("education")
        projects = D.load_yaml("projects")
        publications = D.load_bib()
        talks = D.load_yaml("talks")
        service = D.load_yaml("service")
        funding = D.load_yaml("funding")
        references = D.load_yaml("references")
    except Exception as exc:  # noqa: BLE001 - want a clean top-level failure
        print(f"FAILED TO LOAD DATA: {exc}")
        return 1

    validate_profile(profile, p)
    validate_employment(employment, p)
    validate_education(education, p)
    validate_projects(projects, p)
    validate_publications(publications, p)
    validate_talks_and_service(talks, service, p)
    validate_funding(funding, p)
    validate_references(references, p)

    if p.items:
        print(f"validate_data: {len(p.items)} problem(s) found:")
        for item in p.items:
            print(f"  - {item}")
        return 1

    print("validate_data: OK "
          f"({len(employment['appointments'])} appointments, {len(education['degrees'])} degrees, "
          f"{len(projects['projects'])} projects, {len(publications)} publications)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
