# NWD Consulting Network website

Static site for https://www.nwd-consulting.com, built with a small Python script and published by GitHub Pages.

**New here? Read [GETTING_STARTED.md](GETTING_STARTED.md).**

```
python new_post.py "Post title"   # start a post
python build.py --serve           # preview at http://localhost:8000
python publish.py                 # publish to the live site
```

Layout: `content/` (pages, services, posts) · `templates/` · `static/` (css, images) · `site.yml`, `people.yml`, `faq.yml` · `.github/workflows/deploy.yml` (automatic build and deploy).
