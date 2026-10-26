#!/usr/bin/env python3
"""One command to regenerate every derived output from data/*.

    python scripts/build_all.py            # full build, incl. PDF
    python scripts/build_all.py --no-pdf   # skip pdflatex (e.g. not installed)

Order: validate -> website -> CV (LaTeX + PDF) -> GitHub profile README ->
LinkedIn/ORCID drafts. Safe to run repeatedly; reports what changed and
exits non-zero if canonical data is invalid or a step fails.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_cv
import build_github_profile
import build_profile_updates
import build_site
import validate_data


def main() -> int:
    print("== 1/5 validating canonical data ==")
    if validate_data.main() != 0:
        print("build_all: aborting -- fix data problems above first")
        return 1

    print("\n== 2/5 regenerating website ==")
    data = build_site.load_all()
    site_changed = build_site.build(data)
    for path, changed in site_changed.items():
        print(f"  {'updated' if changed else 'unchanged'}: {path}")

    print("\n== 3/5 regenerating CV (LaTeX + PDF) ==")
    try:
        cv_data = build_cv.load_all()
        tex_changed = build_cv.build_tex(cv_data)
        print(f"  {'updated' if tex_changed else 'unchanged'}: cv/brian-kyanjo-cv.tex")
        if "--no-pdf" in sys.argv:
            print("  pdf: skipped (--no-pdf)")
        else:
            print(f"  pdf: {build_cv.build_pdf()}")
    except Exception as exc:  # noqa: BLE001
        print(f"build_all: CV build failed: {exc}")
        return 1

    print("\n== 4/5 regenerating GitHub profile README ==")
    build_github_profile.main()

    print("\n== 5/5 regenerating LinkedIn + ORCID drafts ==")
    build_profile_updates.main()

    print("\nbuild_all: done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
