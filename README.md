# Romano Assets — website

A one-page static site: plain HTML and CSS, no framework, no build step, no JavaScript, no web fonts, no trackers,
cookies or analytics. It's published free with **GitHub Pages**.

```
index.html          all the words (one page, four sections)
styles.css          all the looks (dark theme, colours at the top)
assets/             images: placeholders now, your screenshots later
  favicon.svg       the little "R" icon in the browser tab
  pawnheads-1.svg   ┐
  pawnheads-2.svg   ├ Pawnheads screenshots (placeholders)
  pawnheads-3.svg   ┘
  world-builder.svg   the World Builder Kit image (placeholder)
.nojekyll           tells GitHub Pages to serve the files as they are
```

## See it on your computer

Double-click `index.html`; it opens in your browser. After any change, save the file and press **F5** in the browser.

## Update it

Open files in any text editor (Notepad works; VS Code is nicer). Only change the text **between** the `<tags>`.

**Change the words.** In `index.html`, each section starts with a comment, `<!-- INTRO -->`, `<!-- PAWNHEADS -->`,
`<!-- WORLD BUILDER KIT -->` and `<!-- CONTACT -->`. Edit the sentences inside `<p class="lead">…</p>`, the headings inside
`<h1>` / `<h2>`, the little pills inside `<ul class="tags">`, and the feature list inside `<ul class="features">`.

**Set your contact email.** It's a placeholder right now. In `index.html`, find `hello@example.com`: it appears **twice**
on one line (`mailto:hello@example.com` and the visible text). Change both. Remember that this address will be public;
a separate address just for the site keeps spam out of your personal inbox.

**Swap in a real screenshot.**
1. Save the screenshot into `assets/`, for example `assets/pawnheads-1.jpg`. JPG or WebP keeps it small; aim for
   1600 × 900 pixels (16:9) and under ~300 KB.
2. In `index.html`, change `src="assets/pawnheads-1.svg"` to `src="assets/pawnheads-1.jpg"`.
3. Update its `alt="…"` text to describe the picture (screen readers and search engines read it).
4. Delete the old `.svg` placeholder if you like.

The World Builder image works the same way (`assets/world-builder.svg`, 1600 × 1000).

**Change the colours.** At the top of `styles.css`: `--gold` is the Pawnheads colour, `--teal` the World Builder Kit
colour, `--bg` the page background.

**Add another project later.** Copy a whole `<section class="project" …> … </section>` block in `index.html`, give it a
new `id` (e.g. `id="my-next-game"`), change its words and images, and add a link to it in the `<ul class="nav">` at the top.

## Publish it with GitHub Pages (once)

1. On github.com: **New repository**. For the address `https://<your-username>.github.io`, name it exactly
   `<your-username>.github.io`. Any other name also works; the address is then
   `https://<your-username>.github.io/<repo-name>/`. Make it **Public** (free Pages needs that).
2. Put these files in it. From this folder in a terminal:
   ```
   git init
   git add .
   git commit -m "Romano Assets site"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
   (Or on the repo page: **Add file → Upload files** and drag everything in, including the `assets` folder.)
3. In the repo: **Settings → Pages**. Under **Build and deployment**: Source **Deploy from a branch**, Branch **main**,
   folder **/ (root)** → **Save**.
4. Wait a minute or two, then refresh that page. It shows **"Your site is live at …"**.

## Update the live site

Change the files, then:
```
git add .
git commit -m "Update site"
git push
```
GitHub Pages republishes by itself within a minute or two.

## Your own domain (optional)

Buy a domain (e.g. `romanoassets.com`). In the repo: **Settings → Pages → Custom domain**, type it in and Save (GitHub
adds a `CNAME` file). Then at your domain registrar add the DNS records GitHub shows you, and tick **Enforce HTTPS**
once it's offered.

## Keep it fast and private

- No `<script>` tags, analytics snippets, embedded videos or social widgets: each of those loads things from other
  companies and can track visitors. If you ever want a video, link to it instead of embedding it.
- Keep images under ~300 KB each.
