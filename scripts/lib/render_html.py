"""Renders each marked HTML region from canonical data.

Every function returns exactly the HTML that belongs *between* a marker
pair (see scripts/lib/markers.py) -- never the marker comments themselves.
Formatting (spacing, tag order) intentionally matches the site's existing
hand-authored, unindented style so that regenerating from data that hasn't
substantively changed reproduces byte-identical output.
"""
from __future__ import annotations

import json

from . import dataio as D

EN_DASH = "–"


def record_list(items_html: list[str]) -> str:
    """The `<ul class="record-list"> <li> ... </li>...</ul>` pattern used
    throughout the site and CV for every simple record list."""
    lis = "".join(f"<li> {html} </li>" for html in items_html)
    return f'<ul class="record-list"> {lis}</ul>'


# ---------------------------------------------------------------- profile --

def json_ld(profile: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile["name"],
        "url": profile["website"],
        "jobTitle": [profile["current_title"], profile["secondary_title"]] if profile.get("secondary_title") else profile["current_title"],
        "affiliation": {
            "@type": "Organization",
            "name": profile["unit"],
            "parentOrganization": {
                "@type": "Organization",
                "name": profile["institution"],
            },
        },
        "sameAs": [
            profile["github_url"],
            profile["orcid_url"],
            profile["linkedin_url"],
        ],
    }
    return json.dumps(data)


def footer_links(profile: dict) -> str:
    return (
        f'<a href="{profile["github_repo_url"]}">Website repository ↗</a>'
        f'<a href="{profile["github_url"]}">GitHub ↗</a>'
        f'<a href="{profile["linkedin_url"]}">LinkedIn ↗</a>'
        f'<a href="{profile["orcid_url"]}">ORCID ↗</a>'
        f'<a href="mailto:{profile["email"]}">Email ↗</a>'
    )


def contact_appointment(profile: dict, employment: dict) -> str:
    primary = primary_appointment(employment)
    date_range = D.format_date_range(primary["start"], primary["end"], style="prose")
    out = f'{primary["title"]}<br>{primary["unit"]}<br>{primary["institution"]}<br>{date_range}'
    if profile.get("secondary_title"):
        out += f'<br><br>{profile["secondary_title"]}<br>{profile["secondary_unit"]}'
    return out


def cv_page_intro_lead(profile: dict, employment: dict) -> str:
    primary = primary_appointment(employment)
    lead = f'{primary["title"]} · {primary["unit"]} · {primary["institution"]}'
    if profile.get("secondary_title"):
        lead += f'<br>{profile["secondary_title"]} · {profile["secondary_unit"]}'
    return lead


def cv_contact_line(profile: dict) -> str:
    return (
        f'<a href="mailto:{profile["email"]}">{profile["email"]}</a> · '
        f'<a href="tel:{profile["phone_tel"]}">{profile["phone"]}</a> · '
        f'<a href="{profile["github_url"]}">GitHub</a> · '
        f'<a href="{profile["linkedin_url"]}">LinkedIn</a> · '
        f'<a href="{profile["orcid_url"]}">ORCID: {profile["orcid"]}</a>'
    )


def cv_professional_summary(profile: dict) -> str:
    return profile["professional_summary"].strip()


def cv_technical_skills(profile: dict) -> str:
    parts = [
        f'<p><strong>{row["label"]}:</strong> {row["items"]}</p>'
        for row in profile["technical_skills"]
    ]
    return " ".join(parts)


# -------------------------------------------------------------- employment --

def primary_appointment(employment: dict) -> dict:
    candidates = [a for a in employment["appointments"] if a.get("is_primary_current")]
    if not employment.get("allow_multiple_primary_current") and len(candidates) != 1:
        raise ValueError(f"expected exactly one primary current appointment, found {len(candidates)}")
    return candidates[0]


def ospo_intro_sentences(profile: dict, appointment: dict) -> str:
    ospo = appointment["ospo"]
    if ospo.get("current_description"):
        return ospo["current_description"]
    start_month = D.MONTH_FULL[D.parse_ym(ospo["start"])[1]]
    end_month = D.MONTH_FULL[D.parse_ym(ospo["end"])[1]]
    end_year = D.parse_ym(ospo["end"])[0]
    return (
        f'From {start_month} through {end_month} {end_year}, {ospo["effort_pct"]}% of my '
        f'{appointment["title"]} effort will be supported by {profile["institution_short"]}’s '
        f'Open Source Program Office ({ospo["program"]}). This is part of my '
        f'{profile["institution_short"]} appointment; {ospo["continuation_clause"]}.'
    )


def cv_experience_entry(profile: dict, appointment: dict, style: str = "html") -> str:
    title = appointment["title"]
    unit = appointment.get("unit")
    role = f'{title} · {unit}' if unit else title
    date_range = D.format_date_range(appointment["start"], appointment["end"], appointment.get("display_date"))
    parts = [
        '<div class="entry-heading">'
        f'<h3>{appointment["institution"]}</h3><span class="date">{date_range}</span></div>'
        f'<p class="role">{role}</p>'
    ]
    if appointment.get("ospo"):
        description = appointment["ospo"].get("cv_description")
        if description:
            parts.append(f"<p>{description}</p>")
        else:
            intro = ospo_intro_sentences(profile, appointment)
            cv_tail = appointment["ospo"]["cv_activities_sentence"]
            parts.append(f"<p>{intro} {cv_tail}</p>")
    if appointment.get("previous_role_note"):
        parts.append(f'<p class="appointment-history">Previously: {appointment["previous_role_note"]}</p>')
    bullets = appointment.get("bullets") or []
    parts.append(f'<div>{record_list(bullets) if bullets else ""}</div>')
    return f'<article class="entry">{"".join(parts)}</article>'


def cv_professional_experience(profile: dict, employment: dict) -> str:
    entries = [cv_experience_entry(profile, a) for a in employment["appointments"]]
    return " ".join(entries)


# --------------------------------------------------------------- education --

def education_entry(degree: dict) -> str:
    return (
        '<article class="entry"><div class="entry-heading">'
        f'<h3>{degree["institution"]}</h3><span class="date">{degree["year"]}</span></div>'
        f'<p class="role">{degree["degree"]}</p>'
        f'<div><strong>{degree["detail_label"]}:</strong> <em>{degree["detail_title"]}</em><br> '
        f'<strong>Advisor:</strong> {degree["advisor"]}</div></article>'
    )


def education_section(education: dict) -> str:
    return " ".join(education_entry(d) for d in education["degrees"])


# ----------------------------------------------------------------- funding --

def funded_project_item(project: dict) -> str:
    amount = f'${project["amount_usd"]:,}'
    return (
        f'<strong>{project["title"]}</strong>, <em>{project["project_title"]}</em>, '
        f'{project["years"]}.<br> Award: {amount}. PI: {project["pi"]}; '
        f'Co-PI: {project["co_pi"]}; Co-Investigator: {project["co_investigator"]}. '
        f'{project["description"]}'
    )


def funded_projects_list(funding: dict) -> str:
    return record_list([funded_project_item(p) for p in funding["funded_projects"]])


# ---------------------------------------------------------------- projects --

def _github_bare(url: str) -> str:
    return url.replace("https://", "")


def project_links_html(project: dict, style: str = "cv") -> str:
    if project.get("website"):
        return (
            f'<a href="{project["website"]}">Visit {project["name"]} ↗</a> · '
            f'<a href="{project["github"]}">GitHub ↗</a>'
        )
    return f'<a href="{project["github"]}">{_github_bare(project["github"])}</a>'


def cv_scientific_software_item(project: dict) -> str:
    name = project.get("cv_display_name", project["name"])
    return (
        f'<strong>{name}</strong> {EN_DASH} {project["blurb_cv"]}<br> '
        f'{project_links_html(project)}'
    )


def cv_scientific_software_list(projects: dict) -> str:
    ordered = sorted(projects["projects"], key=lambda p: p["cv_order"])
    return record_list([cv_scientific_software_item(p) for p in ordered])


def home_project_card(project: dict) -> str:
    header = (
        '<div class="project-top">'
        f'<span class="project-number">{project["number"]}</span>'
        f'<span class="project-symbol" aria-hidden="true">{project["symbol"]}</span></div>'
        f'<p class="eyebrow">{project["eyebrow"]}</p>'
        f'<h3><a href="software/#{project["id"]}">{project["name"]}</a></h3>'
        f'<p>{project["blurb_card"]}</p>'
        f'<p class="tags">{project["tags_card"]}</p>'
    )
    if project.get("website"):
        actions = (
            '<div class="actions">'
            f'<a class="button primary" href="{project["website"]}">Visit {project["name"]} ↗</a>'
            f'<a class="button" href="{project["github"]}">GitHub ↗</a></div>'
        )
    else:
        actions = (
            f'<a class="text-link" href="{project["github"]}">Explore the code '
            '<span aria-hidden="true">↗</span></a>'
        )
    return f'<article class="project-card">{header}{actions}</article>'


def home_project_grid(projects: dict) -> str:
    featured = sorted(
        (p for p in projects["projects"] if p.get("featured")), key=lambda p: p["order"]
    )
    return "".join(home_project_card(p) for p in featured)


def _project_by_id(projects: dict, project_id: str) -> dict:
    for p in projects["projects"]:
        if p["id"] == project_id:
            return p
    raise KeyError(project_id)


def sw_cryostack_detail(projects: dict) -> str:
    p = _project_by_id(projects, "cryostack")
    left = (
        f'<div><span class="project-number">{p["number"]}</span>'
        f'<p class="eyebrow">{p["eyebrow"]}</p><h2>{p["name"]}</h2>'
        f'<p class="tags">{p["tags_software"]}</p></div>'
    )
    right = (
        f'<div><p class="lead">{p["blurb_card"]}</p><p>{p["detail_html"]}</p>'
        '<div class="actions">'
        f'<a class="button primary" href="{p["website"]}">Visit {p["name"]} ↗</a>'
        f'<a class="button" href="{p["github"]}">GitHub ↗</a></div></div>'
    )
    return left + right


def sw_cryostack_applications(projects: dict) -> str:
    p = _project_by_id(projects, "cryostack")
    lis = []
    for app in p["applications"]:
        id_attr = f' id="{app["id"]}"' if app.get("html_anchor") else ""
        body = f'<h3><a href="{app["url"]}">{app["name"]} ↗</a></h3><p>{app["description_html"]}</p>'
        lis.append(f'<li{id_attr}>{body}</li>')
    return '<ul class="record-list">\n' + "\n".join(lis) + "\n</ul>"


def sw_icesee_detail(projects: dict) -> str:
    p = _project_by_id(projects, "icesee")
    left = (
        f'<div><span class="project-number">{p["number"]}</span>'
        f'<p class="eyebrow">{p["eyebrow"]}</p><h2>{p["name"]}</h2>'
        f'<p class="tags">{p["tags_card"]}</p></div>'
    )
    right = (
        f'<div><p class="lead">{p["blurb_card"]}</p><p>{p["detail_html"]}</p>'
        f'<a class="button primary" href="{p["github"]}">View {p["name"]} on GitHub ↗</a></div>'
    )
    return left + right


def sw_gt_dare_detail(projects: dict) -> str:
    p = _project_by_id(projects, "gt-dare")
    left = (
        f'<div><span class="project-number">{p["number"]}</span>'
        f'<p class="eyebrow">{p["eyebrow"]}</p><h2>{p["name"]}</h2>'
        f'<p class="tags">{p["tags_card"]}</p></div>'
    )
    right = (
        f'<div><p class="lead">{p["blurb_card"]}</p><p>{p["detail_html"]}</p>'
        f'<a class="button primary" href="{p["github"]}">View {p["name"]} on GitHub ↗</a></div>'
    )
    return left + right


def sw_geoflood_detail(projects: dict) -> str:
    p = _project_by_id(projects, "geoflood")
    left = (
        f'<div><span class="project-number">{p["number"]}</span>'
        f'<p class="eyebrow">{p["eyebrow"]}</p><h2>{p["name"]}</h2>'
        f'<p class="tags">{p["tags_card"]}</p></div>'
    )
    right = (
        f'<div><p class="lead">{p["blurb_card"]}</p><p>{p["detail_html"]}</p>'
        f'<a class="button primary" href="{p["github"]}">View {p["name"]} on GitHub ↗</a></div>'
    )
    return left + right


def sw_supporting_software(projects: dict) -> str:
    supporting = sorted(
        (p for p in projects["projects"] if not p.get("featured")), key=lambda p: p["order"]
    )
    cards = [
        f'<article><h3>{p["name"]}</h3><p>{p["blurb_card"]}</p>'
        f'<a class="text-link" href="{p["github"]}">Repository ↗</a></article>'
        for p in supporting
    ]
    return f'<div class="support-grid">{"".join(cards)}</div>'


# ------------------------------------------------------------- publications --

def publication_item_html(pub: dict) -> str:
    authors = D.join_authors(pub["authors"])
    status = pub.get("status")
    if status == "submitted":
        middle = f'Submitted to {pub["venue"]}' if pub.get("venue") else "Submitted"
    elif status == "in-preparation":
        middle = "In preparation"
    elif status == "published":
        middle = pub.get("venue") or pub.get("year") or "Published"
    else:
        raise ValueError(f"{pub['key']}: unknown status {status!r}")
    out = f'{authors}. <em>{pub["title"]}</em>. {middle}.'
    if pub.get("url") and pub.get("doi"):
        out += f' <a href="{pub["url"]}">{pub["doi"]}</a>.'
    elif pub.get("url"):
        out += f' <a href="{pub["url"]}">Read manuscript ↗</a>.'
    return out


def publications_list(publications: list[dict]) -> str:
    return record_list([publication_item_html(p) for p in publications])


# -------------------------------------------------------------------- talks --

def simple_html_list(items: list[dict]) -> str:
    return record_list([item["html"] for item in items])


def talks_ospo_section(profile: dict, employment: dict) -> str:
    appointment = primary_appointment(employment)
    ospo = appointment["ospo"]
    intro = ospo_intro_sentences(profile, appointment)
    return f'<p>{intro}</p><p>{ospo["talks_activities_sentence"]}</p>'


# ---------------------------------------------------------------- references --

def reference_item(ref: dict) -> str:
    return f'{ref["name"]}, {ref["institution"]} {EN_DASH} <a href="mailto:{ref["email"]}">{ref["email"]}</a>'


def references_list(references: dict) -> str:
    return record_list([reference_item(r) for r in references["references"]])
