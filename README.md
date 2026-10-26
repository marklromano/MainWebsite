# Romano Assets — website

The Romano Assets website: plain HTML and CSS, no framework, no JavaScript, no web fonts, no trackers, cookies or
analytics. Published free with **GitHub Pages** at **https://marklromano.github.io** once this repository is named
`marklromano.github.io` (see below).

```
index.html                    home: the products, standards, help, about
prefab-builder/index.html     the All In One Prefab Builder Kit's page
prefab-builder/docs/          its documentation (made from the kit's Documentation/*.md)
support/index.html            how to get help and report a bug
404.html                      "page not found"
styles.css                    all the looks (colours at the top)
assets/                       logo, favicon and images (assets/img/)
tools/build.py                makes every page above from tools/pages/ and the kit's docs
tools/pages/                  the words of each hand-written page
.nojekyll                     tells GitHub Pages to serve the files as they are
```

## See it on your computer

Double-click `index.html`; it opens in your browser. Every link works offline too.

## Change the words

Edit the page in `tools/pages/` (`home.html`, `prefab-builder.html`, `support.html`), then run:

```
python tools/build.py
```

That writes the finished pages with the shared header and footer. (Editing `index.html` and the other finished pages
directly also works, but the next build overwrites it.)

**Facts used on several pages** sit at the top of `tools/build.py`: the Asset Store link, the email address, the
Prefab Builder's version, and the **Discord** and **bug tracker** links. While `DISCORD_URL` or `ISSUES_URL` is empty
the pages say "soon"; paste the link in and rebuild, and every page links to it.

## Update the docs

The docs pages are made from the Prefab Builder's own offline documentation, so they always match what ships. After
changing `Documentation/*.md` in the kit:

```
pip install markdown          (once)
python tools/build.py --docs "C:\AllInOneWorldBuilderKit\Assets\AllInOnePrefabBuilderKit\Documentation"
```

A new docs page also needs a line in the `DOCS` list in `tools/build.py`.

## Images

Keep each image under ~300 KB: JPG at 1200 × 675 (1600 × 900 for the big one at the top of the home page). The
images here are renders of the kit's sample scenes (Showcase City, Try It) made from Kenney's CC0 City Kits.
`assets/img/og-image.jpg` (1200 × 630) is the picture shown when someone shares a link to the site.

## Publish

GitHub Pages serves the `main` branch: push to `main` and the site updates within a minute or two.

**The address.** After the username change from xMark42 to marklromano, GitHub no longer serves xmark42.github.io,
and a repository called `xMark42.github.io` under the new account is only served at
`marklromano.github.io/xMark42.github.io/`. Rename the repository to **`marklromano.github.io`** (Settings > General >
Repository name) and the site is at **https://marklromano.github.io**. Then check Settings > Pages: Source **Deploy
from a branch**, branch **main**, folder **/ (root)**.

**Your own domain (optional).** Buy a domain (e.g. `romanoassets.com`), enter it in Settings > Pages > Custom domain,
add the DNS records GitHub shows at your registrar, and tick **Enforce HTTPS** once it's offered. Then change
`SITE_URL` in `tools/build.py` and rebuild.

## Keep it fast and private

- No `<script>` tags, analytics snippets, embedded videos or social widgets: each loads things from other companies
  and can track visitors. Link to a video instead of embedding it.
- Keep images small (see above).
