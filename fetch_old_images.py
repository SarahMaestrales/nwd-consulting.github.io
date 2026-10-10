#!/usr/bin/env python3
"""
One-time helper: download the team photos and post pictures from the old
WordPress site into static/img/, so the new site doesn't depend on WordPress.

    python fetch_old_images.py

Run it BEFORE you cancel or repoint the old WordPress site.
Any file that can't be downloaded is skipped (initials are shown instead).
"""
import urllib.request
from pathlib import Path

BASE = "https://nwd-consulting.com/wp-content/uploads/"
ROOT = Path(__file__).resolve().parent

PEOPLE = [
    "2026/03/sarah-maestrales.png", "2026/03/ifeyinwa-onyenekwu.png", 
    "2026/07/jake-mirra.jpg", "2026/03/sadie-gunnink.png",
    "2026/03/kari-beth-krieger.png", "2026/05/antonio-triunfo.jpeg", "2026/03/davi-deconti.png",
    "2026/03/henno-kotze.png", "2026/08/gordon-tai.png", "2026/03/sarah-heany.png",
]
POSTS = ["2026/03/post-patent-announcement.png", "2026/03/ifeyinwa-onyenekwu.png"]


def grab(rel, folder):
    dest = ROOT / "static" / "img" / folder / Path(rel).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  already have {dest.name}")
        return
    req = urllib.request.Request(BASE + rel, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        print(f"  saved {dest.name}")
    except Exception as e:  # noqa: BLE001
        print(f"  could not get {rel}: {e}")


if __name__ == "__main__":
    print("Team photos:")
    for p in PEOPLE:
        grab(p, "people")
    print("Post pictures:")
    for p in POSTS:
        grab(p, "posts")
    print("\nDone. Don't forget your logo: save it as static/img/NWDLogo.jpg")
