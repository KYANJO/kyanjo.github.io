# Maintaining this data

This directory is the **single source of truth** for Brian's professional
facts. The website, CV (web + LaTeX + PDF), GitHub profile README, LinkedIn
draft, and ORCID checklist are all *generated* from these files. Don't edit
generated output directly (anything between `<!--gen:...-->` or `%gen:...`
markers, or the files in `profile-setup/`) -- edit the data here and
regenerate.

## The one command

```sh
python3 -m venv .venv && ./.venv/bin/pip install -r scripts/requirements.txt   # once
./.venv/bin/python scripts/build_all.py
```

This validates the data, then regenerates the website, the CV (LaTeX +
PDF), the GitHub profile README, and the LinkedIn/ORCID drafts, and prints
what changed. Run it after every edit in this directory. It's safe to run
repeatedly -- if nothing changed, it says so.

## Where to make a change

| When... | Edit... |
| --- | --- |
| You get a new job/title, or an appointment's dates/effort change | `data/employment.yml` |
| The OSPO@GT arrangement changes (dates, effort %, activities) | the `ospo:` block under the Georgia Tech entry in `data/employment.yml` |
| You finish a degree or need to correct one | `data/education.yml` |
| You publish, submit, or start a new paper | `data/publications.bib` (see the comment at its top -- never mark a manuscript `published` before it actually is) |
| You give a talk, poster, or attend a conference | `data/talks.yml` |
| You get an award, join/lead an organization, or take on service | `data/service.yml` |
| A grant is awarded, ends, or changes | `data/funding.yml` |
| A reference's contact info changes | `data/references.yml` |
| A project's links, description, or status change | `data/projects.yml` |
| CryoStack changes (its own links, or one of its four applications) | the `cryostack` entry (and its `applications:` list) in `data/projects.yml` |
| Your contact info, bio, or profile links change | `data/profile.yml` |

After any of the above, run `scripts/build_all.py` and commit both the data
change and the regenerated output together.

## What stays hand-written (and why)

Not everything is data-driven -- some prose is legitimately page-specific
and would only get harder to maintain if forced into YAML:

- Homepage hero copy, the "Models, methods, and reproducible science"
  paragraph, and the research page's per-theme framing paragraphs (they're
  narrative framing of the facts, not the facts themselves).
- The software page's CryoStack "documentation"/"computing and
  access"/"demonstrated workflows" sections (implementation narrative, not
  biographical/profile facts).
- The research page's "Research experience" summary paragraph (a
  hand-written condensation of `employment.yml`, not a 1:1 rendering of it).
- LaTeX preamble/macros in `cv/brian-kyanjo-cv.tex` (formatting, not
  content) -- only the marked regions between them are generated.

If you change one of the *facts* those sections mention (e.g. a date in
`employment.yml`), double-check the hand-written prose that paraphrases it
is still accurate.

## Validating without regenerating

```sh
./.venv/bin/python scripts/validate_data.py
```

Checks: required fields on the current position, valid `YYYY-MM` dates,
exactly one primary current appointment, valid URLs, duplicate
publications/project ids, publication status sanity (and specifically
refuses a JOSS-titled entry marked `published`), and required project
links.

## If pdflatex isn't installed

`scripts/build_all.py` and `scripts/build_cv.py` still update
`cv/brian-kyanjo-cv.tex` from data; they just skip rebuilding
`cv/brian-kyanjo-cv.pdf` and say so. Rebuild it later with:

```sh
./.venv/bin/python scripts/build_cv.py
```
