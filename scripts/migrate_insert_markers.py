"""One-time (but safely re-runnable) migration: wrap the existing,
hand-authored HTML/LaTeX content in <!--gen:NAME--> / %gen:NAME markers so
that scripts/build_site.py and scripts/build_cv.py can regenerate exactly
those regions from canonical data. Every marker is inserted around content
that is already present, so running this script changes no visible output;
`build_site.py`/`build_cv.py` do the actual (data-driven) regeneration.

Run once: ./.venv/bin/python scripts/migrate_insert_markers.py
Safe to re-run: already-migrated markers are left untouched.
"""
from __future__ import annotations

from pathlib import Path

from lib.markers import insert_marker_between

ROOT = Path(__file__).resolve().parents[1]

HTML_PAGES = [
    "index.html",
    "research/index.html",
    "software/index.html",
    "publications/index.html",
    "talks/index.html",
    "cv/index.html",
    "contact/index.html",
    "404.html",
]

COMMON_MARKERS = [
    ("json-ld", '<script type="application/ld+json">', "</script>"),
    ("footer-links", '<div class="footer-links">', '</div><p class="footer-note">'),
]

PAGE_MARKERS: dict[str, list[tuple[str, str, str]]] = {
    "index.html": [
        (
            "home-project-grid",
            '<div class="project-grid">',
            '</div></section><section class="research-feature">',
        ),
    ],
    "research/index.html": [
        (
            "research-education",
            "<h2>Education</h2>",
            "</section></main>",
        ),
        (
            "research-funded-project",
            "<h2>Arête Glacier Initiative</h2>",
            '</section><section class="section "><h2>Research experience</h2>',
        ),
    ],
    "software/index.html": [
        (
            "sw-cryostack-detail",
            '<section class="software-detail" id="cryostack">',
            '</section>\n<section class="section" id="cryostack-applications">',
        ),
        (
            "sw-cryostack-applications",
            "<h2>Four scientific applications</h2>",
            '</section>\n<section class="section" id="computing-access">',
        ),
        (
            "sw-icesee-detail",
            '<section class="software-detail" id="icesee">',
            '</section><div class="software-figure"><figure class="research-figure ">',
        ),
        (
            "sw-geoflood-detail",
            '<section class="software-detail" id="geoflood">',
            '</section><div class="software-figure"><figure class="research-figure flood-figure">',
        ),
        (
            "sw-supporting-software",
            "<h2>Supporting software</h2>",
            "</section></main>",
        ),
    ],
    "publications/index.html": [
        (
            "publications-list",
            '<div class="publication-list">',
            "</div></main>",
        ),
    ],
    "talks/index.html": [
        (
            "talks-invited",
            "<h2>Invited Talks and Visits</h2>",
            '</section><section class="section ">' + "<h2>Selected Conference Posters</h2>",
        ),
        (
            "talks-posters",
            "<h2>Selected Conference Posters</h2>",
            '</section><section class="section ">'
            + "<h2>Selected Conferences and Short Courses</h2>",
        ),
        (
            "talks-conferences",
            "<h2>Selected Conferences and Short Courses</h2>",
            '</section><section class="section ">' + "<h2>Activities, Associations, and Awards</h2>",
        ),
        (
            "talks-activities",
            "<h2>Activities, Associations, and Awards</h2>",
            '</section><section class="section" id="ospo">',
        ),
        (
            "talks-ospo",
            '<h2>OSPO@GT and open-source activities</h2>',
            "</section></main>",
        ),
    ],
    "cv/index.html": [
        (
            "cv-page-intro-lead",
            '<div class="page-intro"><p class="eyebrow">Curriculum vitae</p><h1>Brian Kyanjo</h1><p class="lead">',
            '</p></div><div class="actions cv-actions">',
        ),
        (
            "cv-contact-line",
            'LaTeX source</a></div><p class="cv-contact">',
            "</p><p class=\"cv-contact\">This web CV includes",
        ),
        (
            "cv-professional-summary",
            '<section id="professional-summary"><h2>Professional Summary</h2><p>',
            '</p></section><section id="education">',
        ),
        (
            "cv-education",
            '<section id="education"><h2>Education</h2>',
            '</section><section id="technical-skills">',
        ),
        (
            "cv-technical-skills",
            '<section id="technical-skills"><h2>Technical Skills</h2>',
            '</section><section id="professional-experience">',
        ),
        (
            "cv-professional-experience",
            '<section id="professional-experience"><h2>Professional Experience</h2>',
            '</section><section id="selected-funded-projects">',
        ),
        (
            "cv-funded-projects",
            '<section id="selected-funded-projects"><h2>Selected Funded Projects</h2>',
            '</section><section id="selected-scientific-software">',
        ),
        (
            "cv-scientific-software",
            '<section id="selected-scientific-software"><h2>Selected Scientific Software</h2>',
            '</section><section id="journal-publications-and-refereed-conference-proceedings">',
        ),
        (
            "cv-publications",
            '<section id="journal-publications-and-refereed-conference-proceedings">'
            + "<h2>Journal Publications and Refereed Conference Proceedings</h2>",
            '</section><section id="selected-conferences-and-short-courses">',
        ),
        (
            "cv-conferences",
            '<section id="selected-conferences-and-short-courses">'
            + "<h2>Selected Conferences and Short Courses</h2>",
            '</section><section id="selected-conference-posters">',
        ),
        (
            "cv-posters",
            '<section id="selected-conference-posters"><h2>Selected Conference Posters</h2>',
            '</section><section id="invited-talks-and-visits">',
        ),
        (
            "cv-invited-talks",
            '<section id="invited-talks-and-visits"><h2>Invited Talks and Visits</h2>',
            '</section><section id="activities-associations-and-awards">',
        ),
        (
            "cv-activities",
            '<section id="activities-associations-and-awards">'
            + "<h2>Activities, Associations, and Awards</h2>",
            '</section><section id="references">',
        ),
        (
            "cv-references",
            '<section id="references"><h2>References</h2>',
            "</section></div></main>",
        ),
    ],
    "contact/index.html": [
        (
            "contact-appointment",
            '<h2><a href="mailto:bkyanjo3@gatech.edu">bkyanjo3@gatech.edu ↗</a></h2><p>',
            "</p><p><a href=\"tel:",
        ),
    ],
    "404.html": [],
}


TEX_MARKERS: list[tuple[str, str, str]] = [
    (
        "tex-professional-summary",
        "\\section*{Professional Summary}\n\n",
        "\n\n\n% ============================================================\n% Education",
    ),
    (
        "tex-education",
        "\\section*{Education}\n\n",
        "\n\n% ============================================================\n% Technical Skills",
    ),
    (
        "tex-technical-skills",
        "\\section*{Technical Skills}\n\n",
        "\n\n% ============================================================\n% Professional Experience",
    ),
    (
        "tex-professional-experience",
        "\\section*{Professional Experience}\n\n",
        "\n\n\\section*{Selected Funded Projects}",
    ),
    (
        "tex-funded-projects",
        "\\section*{Selected Funded Projects}\n\n",
        "\n% ============================================================\n% Open-Source Scientific Software",
    ),
    (
        "tex-scientific-software",
        "\\section*{Selected Scientific Software}\n\n",
        "\n\n% ============================================================\n% Publications",
    ),
    (
        "tex-publications",
        "\\section*{Journal Publications and Refereed Conference Proceedings}\n\n",
        "\n% ============================================================\n% Conferences and Short Courses",
    ),
    (
        "tex-conferences",
        "\\section*{Selected Conferences and Short Courses}\n\n",
        "\n% ============================================================\n% Conference Posters",
    ),
    (
        "tex-posters",
        "\\section*{Selected Conference Posters}\n\n",
        "\n% ============================================================\n% Invited Talks and Visits",
    ),
    (
        "tex-invited-talks",
        "\\section*{Invited Talks and Visits}\n\n",
        "\n% ============================================================\n% Activities, Associations, and Awards",
    ),
    (
        "tex-activities",
        "\\section*{Activities, Associations, and Awards}\n\n",
        "\n% ============================================================\n% References",
    ),
    (
        "tex-references",
        "\\section*{References}\n\n",
        "\n\\end{document}",
    ),
]


def migrate_tex_file() -> None:
    path = ROOT / "cv" / "brian-kyanjo-cv.tex"
    text = path.read_text(encoding="utf-8")
    for name, start, end in TEX_MARKERS:
        text = insert_marker_between(text, name, start, end, kind="tex")
    path.write_text(text, encoding="utf-8")


def migrate_html_file(rel_path: str) -> None:
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    for name, start, end in COMMON_MARKERS:
        text = insert_marker_between(text, name, start, end, kind="html")
    for name, start, end in PAGE_MARKERS.get(rel_path, []):
        text = insert_marker_between(text, name, start, end, kind="html")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for rel in HTML_PAGES:
        migrate_html_file(rel)
        print(f"migrated {rel}")
    migrate_tex_file()
    print("migrated cv/brian-kyanjo-cv.tex")


if __name__ == "__main__":
    main()
