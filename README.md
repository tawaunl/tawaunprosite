# tawaunprosite

Professional site for **Tawaun A. Lucas, Ph.D.** This is a remake of the original Hugo/Wowchemy
site (tawaunlucas.com). It keeps the same pages, layout, fonts and colors, but builds from one
small Python script with no dependencies.

```
build.py                  # renders every page into _site/
data/profile.json         # name, role, bio, social links, education, interests, booking id
data/experience.json      # work timeline, education, skill circles
data/publications.json    # papers: authors, venue, DOI/PDF links, abstract, tags, BibTeX
static/                   # css, js, images, CV PDF, thesis PDF (copied as-is)
.github/workflows/deploy.yml
```

Pages: **About** (home) · **Experience & Skills** · **Publications** (with a detail page per paper)
· **CV** (embedded PDF) · **Book Me** (Reclaim scheduler embed).

## Preview locally

```sh
python3 build.py
python3 -m http.server 8000 -d _site
# open http://localhost:8000
```

## Editing content

- **Add a publication:** add an object to `data/publications.json`. Write your name exactly as
  `Tawaun A. Lucas` so it gets bolded. Set `"featured": true` to show it on the home page (the two
  most recent featured papers appear there). For a figure, put an image in `static/img/pubs/` and
  set `"image"`. Tags drive the "Related" list.
- **Update a job:** edit `data/experience.json`. The first entry gets the red "current" briefcase.
- **Bio or links:** edit `data/profile.json`.
- **Styling:** `static/css/site.css`. The primary blue `#035AA6` and the section colors are
  variables at the top.

## Deployment

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Every push to `main` builds and deploys. A weekly run also re-syncs the CV.
3. *(Optional)* Add a repo secret `RESUME_CV_TOKEN` (a fine-grained token with read access to
   `tawaunl/ResumeCV` contents). Each deploy then publishes the latest `FullResume.pdf`.
4. *(Optional) Custom domain:* add a `CNAME` file containing `tawaunlucas.com` at the repo root,
   set the domain under Settings → Pages, and point DNS at GitHub Pages. The build picks up the
   right base path automatically.
