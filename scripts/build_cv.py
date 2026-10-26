#!/usr/bin/env python3
"""Regenerate the marked (%gen:NAME) regions of cv/brian-kyanjo-cv.tex from
the same canonical data used for the website, then (if pdflatex is
available) rebuild cv/brian-kyanjo-cv.pdf.

This closes the gap described by the old cv/index.html note ("the
downloadable PDF and LaTeX source remain the earlier CV snapshot"): the
LaTeX/PDF CV now carries the same OSPO@GT and CryoStack-applications facts
already on the web CV.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from lib import dataio as D
from lib import render_tex as RT
from lib.markers import apply_to_file

ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / "cv" / "brian-kyanjo-cv.tex"


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


def build_tex(data: dict) -> bool:
    profile, employment, education = data["profile"], data["employment"], data["education"]
    projects, publications = data["projects"], data["publications"]
    talks, service, funding, references = data["talks"], data["service"], data["funding"], data["references"]

    replacements = {
        "tex-professional-summary": RT.professional_summary(profile),
        "tex-education": RT.education(education),
        "tex-technical-skills": RT.technical_skills(profile),
        "tex-professional-experience": RT.professional_experience(profile, employment),
        "tex-funded-projects": RT.funded_projects(funding),
        "tex-scientific-software": RT.scientific_software(projects),
        "tex-publications": RT.publications(publications),
        "tex-conferences": RT.simple_list(talks["conferences_and_short_courses"]),
        "tex-posters": RT.simple_list(talks["conference_posters"]),
        "tex-invited-talks": RT.simple_list(talks["invited_talks"]),
        "tex-activities": RT.simple_list(service["activities_associations_awards"]),
        "tex-references": RT.references(references),
    }
    return apply_to_file(TEX_PATH, replacements, kind="tex")


def build_pdf() -> str:
    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        return "skipped (pdflatex not found on PATH -- rebuild manually, see cv/README or repo README)"
    cv_dir = ROOT / "cv"
    pdf_path = cv_dir / "brian-kyanjo-cv.pdf"
    before = pdf_path.read_bytes() if pdf_path.exists() else None
    # Fixed SOURCE_DATE_EPOCH so pdflatex emits a deterministic CreationDate
    # and /ID -- otherwise the PDF's bytes change on every run even when the
    # .tex source hasn't, breaking the "rerun produces no diff" check.
    env = {**os.environ, "SOURCE_DATE_EPOCH": "1735689600"}
    for _ in range(2):
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(cv_dir), str(TEX_PATH)],
            cwd=cv_dir, capture_output=True, text=True, env=env,
        )
        if result.returncode != 0:
            tail = "\n".join(result.stdout.splitlines()[-40:])
            raise RuntimeError(f"pdflatex failed:\n{tail}")
    for ext in ("aux", "log", "out"):
        f = cv_dir / f"brian-kyanjo-cv.{ext}"
        if f.exists():
            f.unlink()
    after = pdf_path.read_bytes()
    return "unchanged: cv/brian-kyanjo-cv.pdf" if after == before else "rebuilt cv/brian-kyanjo-cv.pdf"


def main() -> None:
    data = load_all()
    changed = build_tex(data)
    print(f"{'updated' if changed else 'unchanged'}: cv/brian-kyanjo-cv.tex")
    skip_pdf = "--no-pdf" in sys.argv
    if skip_pdf:
        print("pdf: skipped (--no-pdf)")
    else:
        print(f"pdf: {build_pdf()}")


if __name__ == "__main__":
    main()
