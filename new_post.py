#!/usr/bin/env python3
"""
Start a new blog post.

    python new_post.py "My post title"
    python new_post.py "My post title" -c "Learning Science" -c "The Latest" -t edtech -t psychometrics
    python new_post.py "My post title" --image ~/Desktop/photo.jpg
    python new_post.py "My post title" --date 2026-12-01      (schedule it for later)

It creates a ready-to-write file in content/posts/. Write your post below the
header block, save, then run:  python publish.py
"""
import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


def main():
    ap = argparse.ArgumentParser(description="Create a new blog post")
    ap.add_argument("title")
    ap.add_argument("-c", "--category", action="append", default=[], help="repeat for several")
    ap.add_argument("-t", "--tag", action="append", default=[], help="repeat for several")
    ap.add_argument("-a", "--author", default="sarah-maestrales", help="an id from people.yml")
    ap.add_argument("-i", "--image", help="path to a picture to use at the top of the post")
    ap.add_argument("-d", "--date", default=dt.date.today().isoformat(), help="YYYY-MM-DD (future dates are scheduled)")
    args = ap.parse_args()

    slug = slugify(args.title)
    path = ROOT / "content" / "posts" / f"{args.date}-{slug}.md"
    if path.exists():
        sys.exit(f"That post already exists: {path}")

    image_line = "# image: /img/posts/your-picture.jpg"
    if args.image:
        src = Path(args.image).expanduser()
        if not src.exists():
            sys.exit(f"Can't find the image: {src}")
        dest = ROOT / "static" / "img" / "posts" / f"{slug}{src.suffix.lower()}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        image_line = f"image: /img/posts/{dest.name}"

    cats = "[" + ", ".join(args.category) + "]" if args.category else "[The Latest]"
    tags = "[" + ", ".join(args.tag) + "]" if args.tag else "[]"
    safe_title = args.title.replace('"', '\\"')

    path.write_text(
        f'''---
title: "{safe_title}"
date: {args.date}
author: {args.author}
categories: {cats}
tags: {tags}
summary: One or two sentences that appear on the blog list and in search results.
{image_line}
# draft: true      <- remove the # at the start of this line to keep the post hidden
---

Write your post here. Use plain text, with blank lines between paragraphs.

## This is a section heading

- This is a bullet point
- **Bold text** and *italic text* work too

[This is a link](https://example.com)

This is an image ![Image alt text](/img/posts/your-picture.jpg)
''',
        encoding="utf-8",
    )
    print(f"\nCreated: {path.relative_to(ROOT)}")
    print("Open it in any text editor, write your post, save, then run:  python publish.py\n")


if __name__ == "__main__":
    main()
