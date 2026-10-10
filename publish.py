#!/usr/bin/env python3
"""
Publish your changes to the live website.

    python publish.py
    python publish.py "Add post about psychometrics"

What it does, in order:
  1. Builds the site locally, so mistakes are caught before they go live
  2. Saves ("commits") every change in this folder
  3. Sends ("pushes") it to GitHub, which rebuilds and updates the website
     (this takes about a minute)
"""
import datetime as dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*cmd, check=True):
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"\nA step failed:  {' '.join(cmd)}\n")
        print(result.stdout + result.stderr)
        sys.exit(1)
    return result


def main():
    message = " ".join(sys.argv[1:]).strip() or f"Update site {dt.datetime.now():%Y-%m-%d %H:%M}"

    if run("git", "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        sys.exit("This folder isn't connected to Git yet. See GETTING_STARTED.md, step 5.")

    print("1/3  Checking the site builds...")
    build = subprocess.run([sys.executable, "build.py"], cwd=ROOT)
    if build.returncode != 0:
        sys.exit("The build failed, so nothing was published. Fix the error above and try again.")

    print("2/3  Saving changes...")
    run("git", "add", "-A")
    if not run("git", "status", "--porcelain").stdout.strip():
        sys.exit("Nothing has changed since the last publish.")
    run("git", "commit", "-m", message)

    print("3/3  Sending to GitHub...")
    run("git", "pull", "--rebase", "--autostash")
    run("git", "push")

    print("\nDone. GitHub is now building the site; it usually goes live within a minute or two.")
    print("Watch progress at: https://github.com/SarahMaestrales/nwd-website/actions\n")


if __name__ == "__main__":
    main()
