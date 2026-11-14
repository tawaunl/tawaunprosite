# tawaunprosite

Professional site for **Tawaun A. Lucas, Ph.D.**, computational biologist.

It's plain static HTML, CSS and JS, with no framework and no build step. Deployment runs through GitHub Pages.

```
index.html            # all page content
404.html
assets/css/style.css  # design tokens (light + dark) and layout
assets/js/main.js     # theme toggle, nav, publication filters, hero embedding animation
assets/img/           # headshot, favicon, publication figures
cv/TawaunLucas_CV.pdf # fallback CV (replaced at deploy time, see below)
.github/workflows/deploy.yml
```

## Preview locally

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Editing content

All text lives in `index.html`, one commented block per section (hero, about, research,
experience, publications, resources, service, contact).

- **New publication:** copy an `<li>` in `.publist`. Set `data-tags` to `first` and/or
  `preprint` so the filters pick it up, and wrap your name in `<b>`.
- **Featured paper:** add a figure to `assets/img/pubs/` (≈1400px wide JPG) and copy an
  `<article class="feature">` block.
- **Colors:** edit the tokens at the top of `style.css`. Dark mode redefines the same tokens.

## Deployment

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Every push to `main` deploys. A weekly scheduled run also re-syncs the CV.
3. *(Optional)* Add a repo secret `RESUME_CV_TOKEN` (a fine-grained token with read access
   to `tawaunl/ResumeCV` contents). Each deploy then publishes the latest `FullResume.pdf`.
   Without the secret, the committed `cv/TawaunLucas_CV.pdf` is used.
4. *(Optional) Custom domain:* add a `CNAME` file containing `tawaunlucas.com`, set the domain
   under Settings → Pages, and point DNS at GitHub Pages.
