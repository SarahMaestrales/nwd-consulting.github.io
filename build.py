#!/usr/bin/env python3
"""
Build the NWD Consulting Network website.

    python build.py            builds everything into ./_site
    python build.py --serve    builds, then previews at http://localhost:8000

You normally never run this by hand on a publish day: GitHub runs it for you
every time you push. Run it locally only to preview.
"""
import argparse
import datetime as dt
import html
import math
import re
import shutil
import sys
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
STATIC = ROOT / "static"
CONTENT = ROOT / "content"
TODAY = dt.date.today()


# ------------------------------------------------------------------ helpers
def fail(msg):
    print(f"\nBUILD ERROR: {msg}\n", file=sys.stderr)
    sys.exit(1)


def load_yaml(name):
    path = ROOT / name
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        fail(f"{name} is not valid YAML: {e}")


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "untitled"


def split_front_matter(text, where):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    try:
        return (yaml.safe_load(m.group(1)) or {}), m.group(2)
    except yaml.YAMLError as e:
        fail(f"The header block (between the --- lines) in {where} is not valid: {e}\n"
             "Tip: if a title contains a colon, wrap the whole title in quotes.")


_md = markdown.Markdown(extensions=["extra", "smarty", "sane_lists"])


def render_md(body):
    _md.reset()
    return _md.convert(body)


def plain_text(fragment):
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


def to_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        return dt.date.fromisoformat(value.strip()[:10])
    return None


def as_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return list(value)


def long_date(d):  # cross-platform "March 5, 2026"
    return f"{d:%B} {d.day}, {d.year}"


def initials(name):
    words = str(name).split(",")[0].split()
    if not words:
        return "?"
    return (words[0][0] + (words[-1][0] if len(words) > 1 else "")).upper()


def terms(names, kind):
    return [{"name": n, "slug": slugify(n), "url": f"/{kind}/{slugify(n)}/"} for n in as_list(names)]


# --------------------------------------------------------------- load content
def load_dir(sub):
    items = []
    for path in sorted((CONTENT / sub).glob("*.md")):
        rel = path.relative_to(ROOT)
        meta, body = split_front_matter(path.read_text(encoding="utf-8"), rel)
        meta["_file"] = str(rel)
        meta["_stem"] = path.stem
        meta["content"] = render_md(body)
        items.append(meta)
    return items


def load_posts():
    posts = []
    for meta in load_dir("posts"):
        where = meta["_file"]
        if not meta.get("title"):
            fail(f"{where} has no title. Add a line like:  title: My post title")
        if meta.get("draft"):
            print(f"  skipping draft: {where}")
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)$", meta["_stem"])
        try:
            date = to_date(meta.get("date")) or (dt.date.fromisoformat(m.group(1)) if m else None)
        except ValueError:
            fail(f"{where}: the date must look like 2026-03-12")
        if date is None:
            fail(f"{where} needs a date (add  date: 2026-03-12  or name the file 2026-03-12-my-post.md)")
        if date > TODAY:
            print(f"  scheduled for {date}: {where}")
            continue
        slug = meta.get("slug") or (m.group(2) if m else slugify(meta["title"]))
        words = len(plain_text(meta["content"]).split())
        summary = meta.get("summary") or plain_text(meta["content"])[:200].rsplit(" ", 1)[0] + "…"
        meta.update(
            date=date,
            slug=slug,
            url=f"/{date:%Y}/{date:%m}/{date:%d}/{slug}/",
            categories=terms(meta.get("categories"), "category"),
            tags=terms(meta.get("tags"), "tag"),
            read_minutes=max(1, round(words / 220)),
            summary=summary,
        )
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["_stem"]), reverse=True)
    return posts


# -------------------------------------------------------------------- output
class Builder:
    def __init__(self):
        self.site = load_yaml("site.yml")
        self.faq = load_yaml("faq.yml")
        self.groups = load_yaml("people.yml")
        self.people = {p["id"]: p for g in self.groups for p in g["people"] if "id" in p}
        self.urls = []

        logo = self.site.get("logo", "")
        has_logo = bool(logo) and (STATIC / logo.lstrip("/")).exists()
        if not has_logo:
            print("  note: logo not found at static" + logo + " (showing the NWD monogram instead)")

        self.env = Environment(
            loader=FileSystemLoader(ROOT / "templates"),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["longdate"] = long_date
        self.env.filters["initials"] = initials
        base_path = self.site.get("base_path", "").rstrip("/")
        self.env.globals.update(
            site=self.site,
            nav=[{**n, "url": f"{base_path}{n['url']}"} for n in self.site.get("nav", [])],
            has_logo=has_logo,
            year=TODAY.year,
            build_id=dt.datetime.now().strftime("%Y%m%d%H%M%S"),
            static_exists=lambda p: bool(p) and (STATIC / str(p).lstrip("/")).exists(),
        )

    # -- writing
    def write(self, url, template, index=True, **ctx):
        ctx["url"] = url
        out = self.env.get_template(template).render(**ctx)
        target = OUT / url.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")
        if index:
            self.urls.append(url)

    def redirect(self, old, new):
        target = OUT / old.strip("/") / "index.html"
        if target.exists():
            return
        dest = self.site["url"] + new
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f'<!doctype html><meta charset="utf-8"><title>Redirecting…</title>'
            f'<link rel="canonical" href="{dest}"><meta http-equiv="refresh" content="0; url={new}">'
            f'<p>This page has moved to <a href="{new}">{dest}</a>.</p>',
            encoding="utf-8",
        )

    # -- build
    def build(self):
        if OUT.exists():
            shutil.rmtree(OUT)
        OUT.mkdir()
        shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

        posts = load_posts()
        for p in posts:
            author = p.get("author") or self.site.get("default_author")
            p["author_obj"] = self.people.get(author)
            p["author_name"] = (
                self._full_name(p["author_obj"]) if p["author_obj"] else (author or "")
            )

        services = sorted(load_dir("services"), key=lambda s: s.get("order", 99))
        for s in services:
            self._need(s, "title", "slug")
            s["url"] = f"/{s['slug']}/"
            s["card_title"] = s.get("card_title") or s["title"]
        pages = load_dir("pages")

        categories, tags = {}, {}
        for p in posts:
            for c in p["categories"]:
                categories.setdefault(c["slug"], {"term": c, "posts": []})["posts"].append(p)
            for t in p["tags"]:
                tags.setdefault(t["slug"], {"term": t, "posts": []})["posts"].append(p)
        all_categories = sorted((v["term"] for v in categories.values()), key=lambda c: c["name"])

        common = dict(all_categories=all_categories)

        # home
        self.write("/", "home.html", title=None, services=services, latest=posts[:3],
                   faq=self.faq, bodyclass="home", **common)

        # services
        self.write("/services/", "services.html", title="Services", services=services)
        for s in services:
            self.write(s["url"], "service.html", title=s["title"], item=s,
                       description=s.get("summary"))
            for old in as_list(s.get("aliases")):
                self.redirect(old, s["url"])

        # standalone pages
        for pg in pages:
            self._need(pg, "title", "slug")
            url = pg.get("url") or f"/{pg['slug']}/"
            template = pg.get("template", "page.html")
            self.write(url, template, title=pg["title"], item=pg, groups=self.groups,
                       description=pg.get("description"))
            for old in as_list(pg.get("aliases")):
                self.redirect(old, url)

        # blog index (paginated)
        per = int(self.site.get("posts_per_page", 10))
        n_pages = max(1, math.ceil(len(posts) / per))
        for i in range(n_pages):
            url = "/blog/" if i == 0 else f"/blog/page/{i + 1}/"
            self.write(url, "blog_index.html", title="Get the latest" if i == 0 else f"Get the latest, page {i + 1}",
                       posts=posts[i * per:(i + 1) * per], pg=i + 1, pages=n_pages, **common)
        self.redirect("/get-the-latest-from-nwd/", "/blog/")

        # categories and tags
        for kind, bucket in (("category", categories), ("tag", tags)):
            for slug, v in bucket.items():
                self.write(f"/{kind}/{slug}/", "term.html", title=f"{v['term']['name']}",
                           term=v["term"], kind=kind, posts=v["posts"], **common)

        # posts
        for i, p in enumerate(posts):
            self.write(p["url"], "post.html", title=p["title"], item=p, description=p["summary"],
                       newer=posts[i - 1] if i > 0 else None,
                       older=posts[i + 1] if i + 1 < len(posts) else None)
            for old in as_list(p.get("aliases")):
                self.redirect(old, p["url"])

        # 404
        html404 = self.env.get_template("404.html").render(url="/404.html", title="Page not found")
        (OUT / "404.html").write_text(html404, encoding="utf-8")

        self._feed(posts)
        self._sitemap()
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {self.site['url']}/sitemap.xml\n")
        (OUT / ".nojekyll").write_text("")
        if self.site.get("cname"):
            (OUT / "CNAME").write_text(self.site["cname"] + "\n")

        print(f"Built {len(self.urls)} pages ({len(posts)} posts, {len(services)} services) into {OUT}")

    # -- internals
    @staticmethod
    def _need(item, *keys):
        for k in keys:
            if not item.get(k):
                fail(f"{item['_file']} is missing '{k}' in its header block.")

    @staticmethod
    def _full_name(p):
        return p["name"] + (f", {p['credentials']}" if p.get("credentials") else "")

    def _sitemap(self):
        base = self.site["url"]
        rows = "".join(f"<url><loc>{base}{u}</loc></url>" for u in sorted(self.urls))
        (OUT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>',
            encoding="utf-8",
        )

    def _feed(self, posts):
        base, esc = self.site["url"], html.escape
        items = ""
        for p in posts[:20]:
            stamp = format_datetime(dt.datetime(p["date"].year, p["date"].month, p["date"].day, 12, tzinfo=dt.timezone.utc))
            items += (
                f"<item><title>{esc(p['title'])}</title><link>{base}{p['url']}</link>"
                f"<guid>{base}{p['url']}</guid><pubDate>{stamp}</pubDate>"
                f"<description>{esc(p['summary'])}</description></item>"
            )
        (OUT / "feed.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f"<title>{esc(self.site['name'])}</title><link>{base}/</link>"
            f"<description>{esc(self.site['description'])}</description>{items}</channel></rss>",
            encoding="utf-8",
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="preview at http://localhost:8000 after building")
    args = ap.parse_args()
    Builder().build()
    if args.serve:
        import functools
        import http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("Previewing at http://localhost:8000  (press Ctrl+C to stop)")
        try:
            http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
