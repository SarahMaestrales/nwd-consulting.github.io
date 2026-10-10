# Getting started

A step-by-step guide, written for someone who last touched Git a bajillion years ago.
Do the steps in order. Nothing here changes your live website until Step 9.

---

## How this all fits together

- You write posts as simple text files (in `content/posts/`).
- A Python script (`build.py`) turns the text files into website pages, and automatically updates the home page, the blog list, category pages, the RSS feed, and the sitemap.
- GitHub runs that script for you **every time you upload changes**, and publishes the result. You never have to build or upload HTML yourself.

Day to day, publishing a post is two commands:

```
python new_post.py "My post title"
   (write the post, save)
python publish.py
```

---

## Step 1: Install three free tools (one time)

1. **Python** (from python.org/downloads). On Windows, tick **"Add python.exe to PATH"** on the first installer screen. This is the most common thing people miss.
2. **Git** (from git-scm.com/downloads). Accept the defaults.
3. **GitHub CLI** (from cli.github.com). This is what lets your laptop log in to GitHub without fiddly passwords or tokens.

Then open a terminal (Windows: search for "PowerShell". Mac: open "Terminal") and check they work:

```
python --version
git --version
gh --version
```

(On a Mac, use `python3` wherever this guide says `python`.)

Tell Git who you are (one time):

```
git config --global user.name "Sarah Maestrales"
git config --global user.email "your-github-email@example.com"
```

Log in to GitHub (one time). Follow the prompts: choose **GitHub.com**, **HTTPS**, say **yes** to authenticating Git, and **Login with a web browser**:

```
gh auth login
```

---

## Step 2: Create the new repository on GitHub

1. Go to github.com/new (signed in as SarahMaestrales).
2. Repository name: **nwd-website**
3. Choose **Public** (free GitHub Pages hosting needs a public repository unless you pay for a plan).
4. Do **not** tick "Add a README", "Add .gitignore", or "Choose a license". It must start empty.
5. Click **Create repository**.

---

## Step 3: Put the project on your laptop and set up Python

1. Unzip `nwd-website.zip` somewhere easy, like your Documents folder.
2. In your terminal, move into the folder. Example:
   ```
   cd Documents/nwd-website
   ```
3. Create a private Python "workspace" for this project (so it doesn't tangle with anything else on your laptop), and install the three small libraries it needs:

   **Windows (PowerShell):**
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   (If PowerShell complains about scripts being disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer Y, and try again.)

   **Mac:**
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   After activating, your terminal line starts with `(.venv)`. **Each time you open a new terminal to work on the site, run the activate line again** (the second line above).

---

## Step 4: Add your logo and photos

1. Save your logo as **`static/img/NWDLogo.jpg`** (exact name). Until you do, the site shows a gold "NWD" monogram instead.
2. Download the existing team photos and post pictures from the old WordPress site:
   ```
   python fetch_old_images.py
   ```
   Do this **before** you ever switch your domain away from WordPress. Any photo it can't fetch is simply skipped, and initials are shown. You can drop replacement photos into `static/img/people/` (keep the file names listed in `people.yml`).

---

## Step 5: Connect this folder to GitHub

```
git init -b main
git add -A
git commit -m "New NWD website"
git remote add origin https://github.com/SarahMaestrales/nwd-website.git
git push -u origin main
```

Refresh your repository page on GitHub. Your files should be there.

---

## Step 6: Turn on GitHub Pages

1. On GitHub, open the repository, then **Settings**, then **Pages** (left sidebar).
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Open the **Actions** tab. You'll see "Build and deploy website" running. When it turns green, your site is live at a temporary address like `https://sarahmaestrales.github.io/nwd-website/`.

Note: the temporary address will look unstyled or have broken links, because the site is built to live at your own domain (the root of a web address), not inside a sub-folder. That's expected. Use the preview in Step 7 to check how it looks, and Step 9 to put it on your real domain.

---

## Step 7: Preview on your laptop

```
python build.py --serve
```

Open **http://localhost:8000** in your browser. Press **Ctrl+C** in the terminal to stop. (Re-run the command after you make changes.)

---

## Step 8: Write and publish a blog post

```
python new_post.py "How to choose a reliability coefficient" -c "Learning Science" -t psychometrics
```

Options (all optional):

| Option | What it does |
|---|---|
| `-c "Category"` | Adds a category. Repeat for several. |
| `-t tag` | Adds a tag. Repeat for several. |
| `--image path/to/photo.jpg` | Copies the photo into the site and puts it at the top of the post. |
| `--date 2026-12-01` | Schedules the post. It stays hidden until that date, then appears automatically. |

It prints the file it created (in `content/posts/`). Open it in any text editor (Notepad, TextEdit, VS Code), write below the header block, and save.

Formatting cheat sheet:

```
## A section heading
Normal paragraphs, separated by blank lines.
**bold**   *italic*   [link text](https://example.com)
- a bullet point
```

Want to publish it? Run:

```
python publish.py
```

(or `python publish.py "Added the reliability post"` to give the change a name). It checks that the site builds, saves, and uploads. About a minute later the post is live, and **these update automatically**: the home page "latest" section, the blog list, the category and tag pages, the RSS feed, the sitemap, and the previous/next links on neighbouring posts.

To keep a post hidden while you work on it, remove the `#` from the `# draft: true` line in its header.

### Prefer not to use the terminal at all?

You can do everything in your web browser: on GitHub, go to `content/posts`, click **Add file**, **Create new file**, name it like `2026-11-02-my-title.md`, paste in a header block copied from another post, write, and click **Commit changes**. GitHub rebuilds the site automatically.

---

## Step 9: Move your real domain over (only when you're happy)

Your domain currently points to WordPress. Switching it over is the only step that changes what visitors see.

1. In the **old** repo (`nwd-consulting.github.io`), open **Settings, then Pages**, and clear the custom domain if one is set. A domain can only belong to one site.
2. In `nwd-website`, open **Settings, then Pages**, and enter **www.nwd-consulting.com** under Custom domain. Save, and tick **Enforce HTTPS** once it becomes available.
3. At wherever your **DNS** is managed (this may be WordPress.com, or your domain registrar; look at where the domain was bought), set:
   - **CNAME** record: `www` pointing to `sarahmaestrales.github.io`
   - For the bare domain `nwd-consulting.com` (no www), add four **A** records pointing to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - **Leave any MX records alone**. They control your email.
4. DNS changes take anywhere from minutes to a day. Keep WordPress available until the new site is showing on your domain.

GitHub's own instructions, if you get stuck: search "GitHub Pages custom domain" in their docs.

---

## Everyday editing

| To change... | Edit this file |
|---|---|
| Menu, intake form link, LinkedIn, tagline | `site.yml` |
| The five services | `content/services/*.md` |
| Team members and photos | `people.yml` |
| FAQ | `faq.yml` |
| About page intro | `content/pages/about.md` |
| Privacy policy | `content/pages/privacy-policy.md` |
| Colours and font sizes | top of `static/css/style.css` |

After any edit: `python publish.py`.

## If something goes wrong

- **"BUILD ERROR" with a file name**: the message names the file and what's wrong. The usual cause is a colon in a title; wrap the whole title in quotes.
- **`python` not found**: reinstall Python and tick "Add to PATH" (Windows), or use `python3` (Mac).
- **`git push` is rejected**: run `git pull --rebase`, then `python publish.py` again.
- **The site didn't update**: check the **Actions** tab on GitHub for a red X and click it to read the error.
