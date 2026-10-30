# Romano Assets website

The Romano Assets website: plain HTML and CSS, no framework, no web fonts, no trackers, cookies or analytics. The
only script is the docs search (`assets/docs.js`), which is ours, runs offline and sends nothing anywhere. Published free with **GitHub Pages** at **https://romanoassets.github.io**.

```
index.html                    home: the products, standards, help, about
prefab-builder/index.html     the All In One Prefab Builder Kit's page
prefab-builder/docs/          its documentation (made from what ships in the kit, see below)
docs/index.html               every kit's documentation in one place
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

Each kit's docs are made from what ships in its package, so they always match the product:

- `Documentation/*.md`: the pages. `Documentation/docs.json`, if the kit has one, sets their order and sidebar groups.
- `Documentation/Images/`: pictures the pages use (`![caption](Images/name.png)` in the .md).
- `CHANGELOG.md`: the Changelog page.
- The `[Shortcut]` attributes and the `MouseControls` list in the kit's editor code: the Keyboard shortcuts page.

Every docs page gets the sidebar, search, "On this page" links, previous/next and a "tell us" link to the bug tracker.
After changing the kit's docs:

```
pip install markdown          (once)
python tools/build.py --docs prefab-builder="C:\AllInOneWorldBuilderKit\Assets\AllInOnePrefabBuilderKit"
```

**A new kit:** add an entry to `PRODUCTS` at the top of `tools/build.py` (name, version, summary, quick start), give the
kit a `Documentation/docs.json`, and build with `--docs <its-slug>=<its product folder>`. It gets `<slug>/docs/` and a
card on the docs hub.

## Images

Each kit's pictures come from Mark's `Pictures\<Kit>Pictures` folder (for the Prefab Builder,
`PrefabBuilderPictures`: the 12 store gallery images and the cover). They live in `assets/img/<kit>/` as JPG: the full
1920 × 1080 picture, plus a 960 × 540 `-sm` copy for the gallery grid (keep each under ~300 KB). The docs pages show
some of them (`page_images` in `tools/build.py`). `assets/img/og-image.jpg` (1200 × 630, cut from the cover) is the
picture shown when someone shares a link to the site.

## Publish

GitHub Pages serves the `main` branch: push to `main` and the site updates within a minute or two.

**The address.** GitHub serves https://romanoassets.github.io from the repository named exactly
`romanoassets.github.io` in the `romanoassets` organization (moved from marklromano/marklromano.github.io). In
Settings > Pages: Source **Deploy from a branch**, branch **main**, folder **/ (root)**.

**The old address.** https://marklromano.github.io is now a separate small repo,
[marklromano/marklromano.github.io](https://github.com/marklromano/marklromano.github.io), that forwards every old
link (including deep links) to the same page here. Keep it and its GitHub Pages site switched on: version 0.8.0 of the
Prefab Builder Kit has the old address built in.

**Your own domain (optional).** Buy a domain (e.g. `romanoassets.com`), enter it in Settings > Pages > Custom domain,
add the DNS records GitHub shows at your registrar, and tick **Enforce HTTPS** once it's offered. Then change
`SITE_URL` in `tools/build.py` and rebuild.

## Keep it fast and private

- No scripts from other sites, analytics snippets, embedded videos or social widgets: each loads things from other
  companies and can track visitors. Link to a video instead of embedding it.
- Keep images small (see above).
