# Brian Kyanjo — personal research website

A complete static website for **https://kyanjo.github.io**. Plain HTML, CSS, and JavaScript; no framework, dependency installation, or build step. Includes seven pages, light/dark mode, responsive navigation, a printable web CV, compiled PDF, favicon, sitemap, and page-specific search/social metadata.

## Correct repository and address

| Setting | Value |
| --- | --- |
| GitHub owner | `KYANJO` |
| Repository name | `kyanjo.github.io` |
| Full repository | `KYANJO/kyanjo.github.io` |
| Published URL | `https://kyanjo.github.io/` |
| Publishing source | `main`, `/ (root)` |

GitHub specifies a lowercase `<username>.github.io` repository name for user pages when the username contains uppercase letters. Thus `KYANJO` does not need to be renamed to use `kyanjo.github.io`. The supplied CV identifies `KYANJO`; the site is configured for that owner. You must have permission to publish to that account.

Creating this repository under a different account does **not** claim `kyanjo.github.io`. For example, `bkyanjo/kyanjo.github.io` would ordinarily be a project site under `bkyanjo.github.io/kyanjo.github.io/`. If the actual owner changes, update every canonical URL, Open Graph URL, JSON-LD URL, sitemap entry, and the sitemap URL in `robots.txt`. The custom 404 uses root-relative links and assumes a user site; change its paths for a project site. Do not add a `CNAME` for a `github.io` address.

Official references: [Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) and [GitHub Pages API](https://docs.github.com/en/rest/pages/pages).

## Deploy a new repository

Install Git and the [GitHub CLI](https://cli.github.com/). Extract the archive, open a terminal in its parent directory, and run the following commands. These create a **public** repository and publish the included site.

```sh
cd kyanjo.github.io
gh auth login
gh api user --jq .login
```

Confirm the account is `KYANJO` (case-insensitive), or that you have access to publish under that owner. Then:

```sh
git init -b main
git add .
git commit -m "Add Brian Kyanjo research website"
gh repo create KYANJO/kyanjo.github.io --public --source=. --remote=origin --push
gh api --method POST repos/KYANJO/kyanjo.github.io/pages \
  -f build_type=legacy \
  -f 'source[branch]=main' \
  -f 'source[path]=/'
gh api repos/KYANJO/kyanjo.github.io/pages --jq '{url: .html_url, status: .status}'
```

The `.nojekyll` file makes this a plain static deployment. No custom GitHub Actions workflow is required. Allow the initial Pages deployment a few minutes to finish. Check the repository's **Actions** tab and **Settings → Pages** if publication is still pending.

If Pages is already configured, use the update endpoint instead of the create endpoint:

```sh
gh api --method PUT repos/KYANJO/kyanjo.github.io/pages \
  -f build_type=legacy \
  -f 'source[branch]=main' \
  -f 'source[path]=/'
```

## If the repository already exists

Do not run the new-repository commands over an existing checkout or force-push. Clone the repository into a separate folder:

```sh
gh repo clone KYANJO/kyanjo.github.io existing-site
```

Copy this package's contents, including `.nojekyll` and `.gitignore`, into that checkout. Preserve its `.git` directory and review its existing files, especially any custom `CNAME`, `_config.yml`, or deployment workflows. Remove obsolete site files only after reviewing them. Commit the reviewed changes on its publishing branch:

```sh
cd existing-site
git status
git add .
git diff --cached
git commit -m "Refresh Brian Kyanjo research website"
git push
```

If needed, configure Pages for that branch with the PUT command above (replace `main` if the repository uses another branch).

## Deploy through the GitHub website

1. Under the `KYANJO` account, create the public repository `kyanjo.github.io`.
2. Upload the **contents** of this folder. `index.html` must be at the repository root, not inside another `kyanjo.github.io` folder. Include `.nojekyll`.
3. In **Settings → Pages**, select **Deploy from a branch**, choose `main` and `/ (root)`, and save.
4. Open `https://kyanjo.github.io/` once GitHub reports deployment success.

## Preview locally

From the repository folder:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. Stop the server with Ctrl+C. No Node.js installation is required. Navigation and content also work without JavaScript; JavaScript enhances the mobile menu, theme preference, and print button. Without JavaScript, use the browser's Print command for the web CV.

## Canonical data

Biographical/professional facts (employment, education, projects,
publications, talks, service, funding) now live in `data/` and are
generated into the pages below, the CV (web + LaTeX + PDF), and the
`profile-setup/` files by `scripts/build_all.py`. See `data/README.md` for
the day-to-day workflow. The rest of this section describes the generated
files themselves and still applies to page-specific layout/prose that isn't
in `data/`.

## Files and editing

```text
index.html
research/index.html
software/index.html
publications/index.html
talks/index.html
cv/index.html
cv/brian-kyanjo-cv.pdf
cv/brian-kyanjo-cv.tex
contact/index.html
assets/css/main.css
assets/js/theme.js
assets/js/main.js
assets/images/favicon.svg
assets/images/computational-terrain.svg
404.html
robots.txt
sitemap.xml
.nojekyll
.gitignore
README.md
```

Edit the HTML pages directly. Shared navigation, footers, and metadata are deliberately included in each page so the website works without a build system. Apply changes to those elements across all pages, including `404.html`. Shared styles and behavior live in `assets/css` and `assets/js`.

Software links are taken from the CV. The software page has direct anchors at `/software/#icesee`, `/software/#cryostack`, and `/software/#geoflood`. Research details, publication titles, authors, statuses, grant information, awards, and contact details come from the supplied CV. The current appointment has been updated from Brian’s September 2026 instruction: Research Scientist II since September 2026, following the postdoctoral role (August 2024–August 2026). This correction appears on the website, in structured metadata, and in both CV formats. The homepage and research/software introductions condense that material. Publication statuses remain **Submitted** and **In preparation** where specified; no later acceptance or publication status is inferred. Undated events remain undated. The web CV includes all 12 CV sections, including references, and preserves the source's differing conference names.

The homepage, Research, and Software pages use Brian’s own figures from the dissertation and ICESEE archives. Full-size figures are linked and scientific panels are preserved. See `assets/images/research/SOURCES.md` for their exact provenance. No missing-image placeholders are shipped. Brian’s supplied portrait is displayed on the homepage and Contact page. The Teton and Malpasset flood figures preserve their full map extents, legends, and imagery credits. The monogram favicon is included. Social titles/descriptions are present; no social-card image is assumed.

## PDF and web CV

The PDF is already included at **`cv/brian-kyanjo-cv.pdf`**. Replace that file with future CV exports using exactly the same filename; the download buttons will continue to work.

The included LaTeX source incorporates the Research Scientist II appointment and the preceding postdoctoral dates supplied by Brian in September 2026. Other wording is preserved. Layout adjustments include: extra line-breaking flexibility, positive spacing below entry headings, and space reserved before entries to avoid isolated headings. Rebuild using a TeX distribution with the packages listed in the source (including `needspace`):

```sh
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=cv cv/brian-kyanjo-cv.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=cv cv/brian-kyanjo-cv.tex
```

Generated auxiliary files are ignored by Git. The web CV is a separate HTML document with print styles; when updating the LaTeX, also update `cv/index.html` and the related site sections. The site does not convert LaTeX at runtime.

## Maintenance and checks

- Keep the CV, research pages, publication statuses, and contact information aligned.
- Preview at desktop and phone widths and check both themes before publishing updates.
- Check navigation, project links, DOI links, PDF download, and web-CV printing.
- When using another hostname, update SEO URLs and the sitemap together.
- The site uses no analytics, cookies, remote fonts, third-party scripts, or contact-form service. The theme choice is saved locally when browser storage is available.

Commit and push changes to the publishing branch to redeploy:

```sh
git add .
git commit -m "Update research website"
git push
```


## Working folder and GitHub profile

Use `/Users/bkyanjo3/kyanjo.github.io` as the editable checkout alongside `geoflood-project`. Open that folder in your editor and preview with `python3 -m http.server 8000`. Keep future changes there, then commit and push to `KYANJO/kyanjo.github.io`.

GitHub does not offer an automatic redirect from a personal profile to an external website. The supported setup is:

1. Publish the site at `https://kyanjo.github.io`.
2. In GitHub **Settings → Public profile**, set the website/URL field to `https://kyanjo.github.io` and save.
3. Put the contents of `profile-setup/README-for-KYANJO.md` into `README.md` at the root of the public **`KYANJO/KYANJO`** repository. This places a prominent **Visit my research website** link at the top of your profile.
4. Pin `kyanjo.github.io` on the profile if desired.

The profile README belongs in `KYANJO/KYANJO`, separate from this website repository. A prepared copy is included; it has not been published. The homepage has a **GitHub repositories** button, and every page has a **Website repository** link in the footer.

The GitHub repositories already exist. The working folder can be attached to the website repository using the commands below only if it is still empty. If it has existing commits, clone it into a separate checkout and copy the reviewed website files into that checkout instead:

```sh
cd /Users/bkyanjo3/kyanjo.github.io
gh auth login -h github.com
git init -b main
git remote add origin https://github.com/KYANJO/kyanjo.github.io.git
git add .
git commit -m "Add research website with current role and research figures"
git push -u origin main
```

Then configure Pages with the POST or PUT command above. If the repository has gained commits since setup, clone and merge the reviewed files instead of force-pushing. If this folder is already a Git checkout, skip `git init` and inspect `git remote -v` before adding the remote.


### Folder hygiene

The deliverable contains only the website, CV, research assets, and profile-setup files. A nested `existing-site` checkout found in the earlier working directory is not part of the website and is excluded from the standalone copy and ZIP. Do not publish a nested repository or copy an old `.git` directory into this folder. Source archives and Desktop images are left unchanged.
