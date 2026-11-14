#!/usr/bin/env python3
"""Build the static site into _site/.

No dependencies beyond the Python standard library.

    python3 build.py                     # links rooted at "/"
    BASE_PATH=/tawaunprosite/ python3 build.py   # for a GitHub Pages project URL

Content lives in data/*.json; static files (CSS, JS, images, PDFs) in static/.
"""
import datetime as dt
import html
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
BASE = "/" + os.environ.get("BASE_PATH", "/").strip("/") + "/"
BASE = BASE.replace("//", "/")
ME = "Tawaun A. Lucas"

profile = json.loads((ROOT / "data/profile.json").read_text())
experience = json.loads((ROOT / "data/experience.json").read_text())
pubs = json.loads((ROOT / "data/publications.json").read_text())
pubs.sort(key=lambda p: p["date"], reverse=True)

e = html.escape


def u(path=""):
    """Site URL for a path relative to the site root."""
    if path.startswith(("http://", "https://", "mailto:")):
        return path
    return BASE + path.lstrip("/")


# ---------------------------------------------------------------- layout

NAV = [
    ("About", "#about", "home"),
    ("Experience & Skills", "exp/", "exp"),
    ("Publications", "publication/", "publication"),
    ("CV", "cv/", "cv"),
    ("Book Me", "booking/", "booking"),
]


def layout(title, body, active="", description=None, extra_head=""):
    desc = description or profile["description"]
    full_title = ME if title == ME else f"{title} | {ME}"
    links = []
    for label, href, key in NAV:
        url = u("") + href if href.startswith("#") else u(href)
        cls = ' class="active"' if key == active else ""
        links.append(f'<li><a href="{url}"{cls}>{e(label)}</a></li>')
    twitter = next(s for s in profile["social"] if s["label"] == "Twitter")
    year = dt.date.today().year
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full_title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="author" content="{ME}">
  <meta property="og:title" content="{e(full_title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{e(profile['url'].rstrip('/') + '/img/avatar.jpg')}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" type="image/png" href="{u('img/icon.png')}">
  <link rel="apple-touch-icon" href="{u('img/icon.png')}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:wght@400;700&family=Roboto+Mono&family=Roboto:wght@400;700&display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/academicons/1.9.4/css/academicons.min.css">
  <link rel="stylesheet" href="{u('css/site.css')}">
{extra_head}</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="navbar">
    <div class="navbar__inner">
      <a class="navbar__brand" href="{u()}">{ME}</a>
      <button class="navbar__toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="menu"><i class="fas fa-bars"></i></button>
      <nav class="navbar__menu" id="menu" aria-label="Main">
        <ul>{''.join(links)}</ul>
      </nav>
      <a class="navbar__social" href="{twitter['url']}" target="_blank" rel="noopener" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
    </div>
  </header>
  <main id="main">
{body}
  </main>
  <footer class="site-footer">
    <p>© {year} {ME}</p>
  </footer>
  <div class="modal" id="cite-modal" hidden>
    <div class="modal__dialog" role="dialog" aria-modal="true" aria-labelledby="cite-title">
      <div class="modal__header">
        <h5 id="cite-title">Cite</h5>
        <button class="modal__close" aria-label="Close">&times;</button>
      </div>
      <pre class="modal__body"><code id="cite-code"></code></pre>
      <div class="modal__footer">
        <button class="btn btn-outline-primary" id="cite-copy"><i class="fas fa-copy"></i> Copy</button>
        <a class="btn btn-outline-primary" id="cite-download" download><i class="fas fa-download"></i> Download</a>
      </div>
    </div>
  </div>
  <script src="{u('js/site.js')}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- helpers

def fmt_month(date):
    return dt.date.fromisoformat(date).strftime("%B %Y")


def authors_html(authors):
    out = []
    for a in authors:
        if a == ME:
            out.append(f'<span class="author-highlighted"><a href="{u()}">{e(a)}</a></span>')
        else:
            out.append(f"<span>{e(a)}</span>")
    return ", ".join(out)


def bibtex(p):
    if p.get("bibtex"):
        return p["bibtex"]
    key = re.sub(r"\W", "", p["authors"][0].split()[-1]).lower() + p["date"][:4]
    names = " and ".join(a for a in p["authors"] if a != "…")
    kind = "article"
    fields = [f"  title = {{{p['title']}}}", f"  author = {{{names}}}",
              f"  journal = {{{p['venue']}}}", f"  year = {{{p['date'][:4]}}}"]
    if p.get("doi"):
        fields.append(f"  doi = {{{p['doi']}}}")
    return f"@{kind}{{{key},\n" + ",\n".join(fields) + "\n}"


def pub_buttons(p):
    b = []
    if p.get("pdf"):
        b.append(f'<a class="btn btn-outline-primary btn-page-header btn-sm" href="{e(p["pdf"])}" target="_blank" rel="noopener">PDF</a>')
    b.append(f'<button class="btn btn-outline-primary btn-page-header btn-sm js-cite" data-slug="{e(p["slug"])}">Cite</button>')
    if p.get("doi"):
        b.append(f'<a class="btn btn-outline-primary btn-page-header btn-sm" href="https://doi.org/{e(p["doi"])}" target="_blank" rel="noopener">DOI</a>')
    for link in p.get("links", []):
        b.append(f'<a class="btn btn-outline-primary btn-page-header btn-sm" href="{e(link["url"])}" target="_blank" rel="noopener">{e(link["label"])}</a>')
    return '<div class="btn-links">' + "".join(b) + "</div>"


def pub_item(p, compact=False):
    year = p["date"][:4]
    note = f' <span class="pub-note">{e(p["note"])}.</span>' if p.get("note") else ""
    return f"""<div class="pub-list-item" data-type="{e(p['type'])}" data-year="{year}">
  <i class="far fa-file-alt pub-icon" aria-hidden="true"></i>
  <span class="{'article-metadata ' if compact else ''}li-cite-author">{authors_html(p['authors'])}</span>
  ({year}).
  <a href="{u('publication/' + p['slug'] + '/')}">{e(p['title'])}</a>.
  <em>{e(p['venue'])}</em>.{note}
  <p>{pub_buttons(p)}</p>
</div>"""


def bib_data(items):
    data = {p["slug"]: bibtex(p) for p in items}
    return f'<script type="application/json" id="bibtex-data">{json.dumps(data)}</script>'


# ---------------------------------------------------------------- pages

def page_home():
    social = "".join(
        f'<li><a href="{e(u(s["url"]))}" aria-label="{e(s["label"])}"'
        + ('' if s["url"].startswith("mailto:") else ' target="_blank" rel="noopener"')
        + f'><i class="{s["icon"]} big-icon"></i></a></li>'
        for s in profile["social"] if s["label"] != "CV"
    )
    social += f'<li><a href="{u("cv/TawaunLucas_CV.pdf")}" target="_blank" rel="noopener" aria-label="CV"><i class="ai ai-cv big-icon"></i></a></li>'
    bio = "".join(f"<p>{e(p)}</p>" for p in profile["bio"])
    edu = "".join(
        f'<li><i class="fa-li fas fa-graduation-cap"></i><div class="description"><p class="course">{e(c["course"])}, {c["year"]}</p><p class="institution">{e(c["institution"])}</p></div></li>'
        for c in profile["education"]
    )
    interests = "".join(f'<li><i class="fa-li fas fa-check-square"></i>{e(i)}</li>' for i in profile["interests"])
    featured = [p for p in pubs if p.get("featured")][:2]
    org = profile["organization"]
    body = f"""
<section id="about" class="home-section">
  <div class="container">
    <div class="row">
      <div class="col-profile">
        <div id="profile">
          <img class="avatar" src="{u('img/avatar.jpg')}" alt="{ME}" width="270" height="270">
          <div class="portrait-title">
            <h2>{ME}</h2>
            <h3>{e(profile['role'])}</h3>
            <h3><a href="{org['url']}" target="_blank" rel="noopener">{e(org['name'])}</a></h3>
          </div>
          <ul class="network-icon" aria-hidden="false">{social}</ul>
        </div>
      </div>
      <div class="col-content">
        <h1>About me</h1>
        <div class="article-style">
          {bio}
          <h4 class="cv-link"><a href="{u('cv/TawaunLucas_CV.pdf')}" target="_blank" rel="noopener"><i class="fa fa-download" aria-hidden="true"></i> Download my CV</a></h4>
        </div>
        <div class="row two-up">
          <div>
            <h3>Education</h3>
            <ul class="ul-edu fa-ul">{edu}</ul>
          </div>
          <div>
            <h3>Interests</h3>
            <ul class="ul-interests fa-ul">{interests}</ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="publications" class="home-section wg-pages">
  <div class="container">
    <div class="row">
      <div class="section-heading col-profile">
        <h1>Publications &amp; Preprints</h1>
      </div>
      <div class="col-content">
        {''.join(pub_item(p, compact=True) for p in featured)}
        <div class="see-all">
          <a href="{u('publication/')}">See all publications <i class="fas fa-angle-right"></i></a>
        </div>
      </div>
    </div>
  </div>
</section>
{bib_data(featured)}
"""
    return layout(ME, body, "home")


def page_exp():
    def entry(item, kind, current=False):
        cls = f"entry {kind}" + (" current" if current else "")
        extra = ""
        for line in item.get("lines", []):
            extra += f"<div>{e(line)}</div>"
        if item.get("supervisor"):
            s = item["supervisor"]
            extra += f'<div>Supervised by <a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>.</div>'
        if item.get("thesis"):
            extra += f'<div class="thesis"><a href="{u(item["thesis"])}" target="_blank" rel="noopener"><i class="fas fa-download"></i> Read Thesis</a></div>'
        summary = f'<div class="summary">{e(item["summary"])}</div>' if item.get("summary") else f'<div class="summary">{extra}</div>'
        return f"""<div class="{cls}">
  <div class="content">
    <div class="title">{e(item['title'])}</div>
    <div class="company">{e(item['org'])}</div>
    <div class="dates">{e(item['dates'])}</div>
    {summary}
  </div>
</div>"""

    work = "".join(entry(w, "experience", i == 0) for i, w in enumerate(experience["work"]))
    edu = "".join(entry(w, "education") for w in experience["education"])
    skills = ""
    for group, items in experience["skills"].items():
        cells = ""
        for s in items:
            label = f"<span>{e(s['name'])}</span>" if s.get("show_name") else ""
            cells += f"""<div class="skill">
  <div class="circle" style="--fill-scale: {s['level']};" role="img" aria-label="{e(s['name'])}: {int(s['level'] * 100)}%"><div class="fill"></div></div>
  <div class="skill-name"><img src="{u(s['img'])}" width="{s['width']}" alt="{e(s['name'])}">{label}</div>
</div>"""
        skills += f'<h1>{e(group)}</h1><div class="skills-grid">{cells}</div>'
    body = f"""
<div class="exp-page">
  <h1>Work Experience</h1>
  <div class="timeline">{work}</div>
  <hr>
  <h1>Education</h1>
  <div class="timeline">{edu}</div>
  <hr>
  <div class="skills-container">{skills}</div>
</div>
"""
    return layout("Experience & Skills", body, "exp")


def page_pubs():
    years = sorted({p["date"][:4] for p in pubs}, reverse=True)
    types = sorted({p["type"] for p in pubs})
    body = f"""
<div class="universal-wrapper pt-3">
  <h1>Publications</h1>
  <div class="pub-filters">
    <input type="search" class="form-control" id="pub-search" placeholder="Search..." autocomplete="off" aria-label="Search publications">
    <select class="form-control" id="pub-type" aria-label="Filter by type">
      <option value="*">Type</option>
      {''.join(f'<option value="{e(t)}">{e(t)}</option>' for t in types)}
    </select>
    <select class="form-control" id="pub-year" aria-label="Filter by year">
      <option value="*">Date</option>
      {''.join(f'<option value="{y}">{y}</option>' for y in years)}
    </select>
  </div>
  <div class="pub-list" id="pub-list">
    {''.join(pub_item(p) for p in pubs)}
  </div>
  <p class="pub-empty" id="pub-empty" hidden>No publications match your search.</p>
</div>
{bib_data(pubs)}
"""
    return layout("Publications", body, "publication")


def page_pub(p):
    related = [q for q in pubs if q is not p and set(q.get("tags", [])) & set(p.get("tags", []))][:5]
    img = f'<div class="article-header featured-image"><img src="{u(p["image"])}" alt="Featured figure for {e(p["title"])}"></div>' if p.get("image") else ""
    abstract = f'<h3>Abstract</h3><p class="pub-abstract">{e(p["abstract"])}</p>' if p.get("abstract") else ""
    tags = "".join(f'<span class="badge">{e(t)}</span>' for t in p.get("tags", []))
    tags_html = f'<div class="article-tags">{tags}</div>' if tags else ""
    note = f'<div class="pub-meta-row"><div class="pub-meta-label">Status</div><div>{e(p["note"])}</div></div>' if p.get("note") else ""
    social = "".join(
        f'<li><a href="{e(u(s["url"]))}" aria-label="{e(s["label"])}" target="_blank" rel="noopener"><i class="{s["icon"]}"></i></a></li>'
        for s in profile["social"]
    )
    rel = ""
    if related:
        items = "".join(f'<li><a href="{u("publication/" + q["slug"] + "/")}">{e(q["title"])}</a></li>' for q in related)
        rel = f'<div class="article-widget"><h3>Related</h3><ul>{items}</ul></div>'
    body = f"""
<div class="pub">
  <div class="article-container pt-3">
    <h1>{e(p['title'])}</h1>
    <div class="article-metadata">
      <div>{authors_html(p['authors'])}</div>
      <span class="article-date">{fmt_month(p['date'])}</span>
    </div>
    {pub_buttons(p)}
  </div>
  {img}
  <div class="article-container">
    {abstract}
    <div class="pub-meta-row"><div class="pub-meta-label">Type</div><div>{e(p['type'])}</div></div>
    <div class="pub-meta-row"><div class="pub-meta-label">Publication</div><div><em>{e(p['venue'])}</em></div></div>
    {note}
    {tags_html}
    <div class="media author-card">
      <a href="{u()}"><img class="avatar avatar-sm" src="{u('img/avatar.jpg')}" alt="{ME}" width="52" height="52"></a>
      <div class="media-body">
        <h5 class="card-title"><a href="{u()}">{ME}</a></h5>
        <h6 class="card-subtitle">{e(profile['role'])}</h6>
        <ul class="network-icon">{social}</ul>
      </div>
    </div>
    {rel}
  </div>
</div>
{bib_data([p])}
"""
    desc = (p.get("abstract") or p["title"])[:200]
    return layout(p["title"], body, "publication", description=desc)


def page_cv():
    pdf = u("cv/TawaunLucas_CV.pdf")
    body = f"""
<div class="universal-wrapper pt-3 cv-page">
  <div class="cv-embed">
    <iframe src="{pdf}#view=FitH&amp;pagemode=none&amp;navpanes=0" title="CV - {ME}"></iframe>
  </div>
  <p class="cv-fallback">If the PDF does not display above, you can <a href="{pdf}" target="_blank" rel="noopener">download the CV</a> instead.</p>
</div>
"""
    return layout("CV", body, "cv")


def page_booking():
    rid = profile["booking"]["reclaim_id"]
    body = f"""
<div class="universal-wrapper pt-3 booking-page">
  <div class="booking-embed">
    <script src="https://meet.reclaimai.com/scripts/embed-scheduling-link.0.x.x.js" data-id="{e(rid)}" data-redirect="NONE"></script>
  </div>
  <p class="cv-fallback">Prefer email? Reach me at <a href="mailto:{profile['email']}">{profile['email']}</a>.</p>
</div>
"""
    return layout("Book Me", body, "booking", description=f"Book a meeting with {ME}.")


def page_404():
    body = f"""
<div class="universal-wrapper pt-3 notfound">
  <h1>Page not found</h1>
  <p>Perhaps you were looking for one of these?</p>
  <ul>
    <li><a href="{u()}">About</a></li>
    <li><a href="{u('publication/')}">Publications</a></li>
    <li><a href="{u('exp/')}">Experience &amp; Skills</a></li>
  </ul>
</div>
"""
    return layout("Page not found", body)


# ---------------------------------------------------------------- build

def write(rel, content):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    write("index.html", page_home())
    write("exp/index.html", page_exp())
    write("publication/index.html", page_pubs())
    for p in pubs:
        write(f"publication/{p['slug']}/index.html", page_pub(p))
    write("cv/index.html", page_cv())
    write("booking/index.html", page_booking())
    write("404.html", page_404())
    (OUT / ".nojekyll").touch()
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {n} pages into {OUT.relative_to(ROOT)}/ (base path {BASE})")


if __name__ == "__main__":
    main()
