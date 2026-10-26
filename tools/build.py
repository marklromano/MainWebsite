"""Builds the Romano Assets website: every page shares one header and footer from this file.

    python tools/build.py                       # rebuild the pages in tools/pages/
    python tools/build.py --docs <folder>       # also rebuild the Prefab Builder docs from its Documentation folder

The docs need the `markdown` package once:  pip install markdown
The output is plain HTML next to this folder, committed as it is: GitHub Pages serves it with no build step.
Links are relative and point at index.html files, so every page also opens by double-clicking it on your computer.
"""

import argparse
import html
import pathlib
import re

SITE = pathlib.Path(__file__).resolve().parent.parent
PAGES = pathlib.Path(__file__).resolve().parent / "pages"

# ---- Facts used on several pages: change them here ----

SITE_URL = "https://marklromano.github.io"
STORE_URL = "https://assetstore.unity.com/packages/tools/level-design/all-in-one-prefab-builder-kit-411146"
PUBLISHER_URL = "https://assetstore.unity.com/publishers/160196"
EMAIL = "marklromano@outlook.com"
# Empty until they exist: the pages then show "coming soon" instead of a link.
DISCORD_URL = ""
ISSUES_URL = ""
PREFAB_VERSION = "0.8.0"
YEAR = "2026"

ICON_EXTERNAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>')

NAV = [
    ("products", "Products", "index.html#products"),
    ("prefab", "Prefab Builder", "prefab-builder/index.html"),
    ("docs", "Docs", "prefab-builder/docs/index.html"),
    ("support", "Support", "support/index.html"),
]


def header(root, active):
    items = []
    for key, label, href in NAV:
        current = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{root}{href}"{current}>{label}</a></li>')
    items.append(f'<li class="nav-store"><a href="{STORE_URL}" rel="noopener">Asset Store</a></li>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{root}index.html" aria-label="Romano Assets home">
      <img src="{root}assets/logo.svg" alt="" width="30" height="30">
      <span>Romano Assets</span>
    </a>
    <nav aria-label="Main">
      <ul class="nav">
        {"".join(items)}
      </ul>
    </nav>
  </div>
</header>"""


def soon_or_link(url, label):
    return f'<a href="{url}" rel="noopener">{label}</a>' if url else f'<span>{label} (soon)</span>'


def footer(root):
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{root}index.html"><img src="{root}assets/logo.svg" alt="" width="30" height="30"><span>Romano Assets</span></a>
        <p>Unity editor tools, built while making a real game and polished for everyone else.</p>
      </div>
      <div>
        <h4>Products</h4>
        <ul>
          <li><a href="{root}prefab-builder/index.html">Prefab Builder Kit</a></li>
          <li><a href="{root}index.html#products">Coming next</a></li>
          <li><a href="{PUBLISHER_URL}" rel="noopener">Publisher page</a></li>
        </ul>
      </div>
      <div>
        <h4>Learn</h4>
        <ul>
          <li><a href="{root}prefab-builder/docs/index.html">Documentation</a></li>
          <li><a href="{root}prefab-builder/docs/getting-started.html">Getting started</a></li>
          <li><a href="{root}prefab-builder/docs/troubleshooting.html">Troubleshooting</a></li>
        </ul>
      </div>
      <div>
        <h4>Help</h4>
        <ul>
          <li><a href="{root}support/index.html">Support</a></li>
          <li><a href="mailto:{EMAIL}">Email</a></li>
          <li>{soon_or_link(DISCORD_URL, "Discord")}</li>
          <li>{soon_or_link(ISSUES_URL, "Bug tracker")}</li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <p>&copy; {YEAR} Romano Assets. Unity is a trademark of Unity Technologies.</p>
      <p>No trackers, no cookies, no analytics.</p>
    </div>
  </div>
</footer>"""


def page(root, active, title, description, body, path):
    full_title = "Romano Assets" if title == "Romano Assets" else f"{title} | Romano Assets"
    canonical = f"{SITE_URL}/{path}".replace("/index.html", "/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0B1220">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Romano Assets">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}styles.css">
</head>
<body>
{header(root, active)}
<main id="main">
{body}
</main>
{footer(root)}
</body>
</html>
"""


def fill(text, root):
    """Replaces {{name}} placeholders in a page fragment."""
    values = {
        "root": root, "store": STORE_URL, "publisher": PUBLISHER_URL, "email": EMAIL,
        "version": PREFAB_VERSION, "external": ICON_EXTERNAL,
        "discord_tile": discord_tile(), "issues_tile": issues_tile(root),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)


def discord_tile():
    if DISCORD_URL:
        return (f'<a class="tile" href="{DISCORD_URL}" rel="noopener"><span class="label">Community</span>'
                '<h3>Discord</h3><p>Ask questions, share what you build, hear about updates first.</p></a>')
    return ('<div class="tile tile-soon"><span class="label">Community <span class="pill">Soon</span></span>'
            '<h3>Discord</h3><p>A server for questions, show and tell, and update news is being set up.</p></div>')


def issues_tile(root):
    if ISSUES_URL:
        return (f'<a class="tile" href="{ISSUES_URL}" rel="noopener"><span class="label">Bugs</span>'
                '<h3>Report a bug</h3><p>Open an issue on GitHub and follow it until it is fixed.</p></a>')
    return ('<div class="tile tile-soon"><span class="label">Bugs <span class="pill">Soon</span></span>'
            '<h3>Public bug tracker</h3><p>A GitHub issue tracker is on the way. Until then, email bug reports.</p></div>')


# ---- Hand-written pages (tools/pages/*.html) ----

HAND_PAGES = [
    # fragment, output, root, active nav, title, description
    ("home.html", "index.html", "", "",
     "Romano Assets",
     "Unity editor tools by Romano Assets. Home of the All In One Prefab Builder Kit: turn any pack of prefabs into a "
     "world-building kit."),
    ("prefab-builder.html", "prefab-builder/index.html", "../", "prefab",
     "All In One Prefab Builder Kit",
     "Turn any pack of prefabs into a world-building kit: snap, draw roads, scatter, fence, dress streets, settle with "
     "physics and check your scene, all from one Unity window."),
    ("support.html", "support/index.html", "../", "support",
     "Support",
     "Get help with Romano Assets tools: documentation, bug reports, Discord and email."),
    ("404.html", "404.html", "/", "",
     "Page not found",
     "This page doesn't exist."),
]


def build_pages():
    for fragment, out, root, active, title, description in HAND_PAGES:
        body = fill((PAGES / fragment).read_text(encoding="utf-8"), root)
        target = SITE / out
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(root, active, title, description, body, out), encoding="utf-8")
        print("wrote", out)


# ---- Docs: the Prefab Builder's offline Documentation/*.md as web pages ----

DOCS = [
    # (group, source .md, output .html, title in the sidebar)
    ("Start here", "GettingStarted.md", "getting-started.html", "Getting started"),
    ("Start here", "WorldBuilderWindow.md", "window.html", "The Prefab Builder window"),
    ("Start here", "AddingPacks.md", "adding-packs.html", "Adding packs"),
    ("The tabs", "MoveTab.md", "move-tab.html", "Move"),
    ("The tabs", "PlaceTab.md", "place-tab.html", "Place"),
    ("The tabs", "PhysicsTab.md", "physics-tab.html", "Physics"),
    ("The tabs", "DressTab.md", "dress-tab.html", "Dress"),
    ("The tabs", "FixTab.md", "fix-tab.html", "Fix"),
    ("The tabs", "CheckTab.md", "check-tab.html", "Check"),
    ("The tabs", "SettingsTab.md", "settings-tab.html", "Settings"),
    ("Reference", "RulesAndData.md", "rules-and-data.html", "Rules, profiles, palettes, styles"),
    ("Reference", "Presets.md", "presets.html", "Presets"),
    ("Reference", "Extending.md", "extending.html", "Extending (C#)"),
    ("Reference", "Troubleshooting.md", "troubleshooting.html", "Troubleshooting"),
]
DOC_OUT = {src: out for _, src, out, _ in DOCS}
DOC_OUT["Index.md"] = "index.html"


def slugify(value, separator="-"):
    """GitHub's heading anchors, so links written for GitHub (#floors--terrain) keep working."""
    value = value.strip().lower()
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", "-")


def docs_nav(current):
    groups = []
    group = None
    for name, _, out, label in [("", "Index.md", "index.html", "Overview")] + DOCS:
        if name != group:
            if group is not None:
                groups.append("</div>")
            groups.append('<div class="docs-group">' + (f'<p class="label">{name}</p>' if name else ""))
            group = name
        cur = ' aria-current="page"' if out == current else ""
        groups.append(f'<a href="{out}"{cur}>{label}</a>')
    groups.append("</div>")
    links = "".join(groups)
    return (f'<nav class="docs-nav" aria-label="Documentation">'
            f'<div class="docs-links">{links}</div>'
            f'<details><summary>All documentation pages</summary><div class="docs-links">{links}</div></details>'
            f'</nav>')


def convert(md_text):
    import markdown  # only needed for the docs
    from markdown.extensions.toc import TocExtension

    # Links between the .md files become links between the .html pages
    def relink(match):
        target, anchor = match.group(2), match.group(3) or ""
        return f"]({DOC_OUT.get(target, target)}{anchor})"

    md_text = re.sub(r"\]\((?!https?:)(([A-Za-z]+\.md))(#[^)]*)?\)", lambda m: relink(m), md_text)
    out = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists",
                                                 TocExtension(slugify=slugify, toc_depth="2-4")])
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out


QUICK_START = """<div class="callout">
  <p class="label label-accent">Quick start: five minutes</p>
  <ol>
    <li>Import the package from the Asset Store. Everything lands in <code>Assets/AllInOnePrefabBuilderKit/</code>.</li>
    <li>Open <strong>Tools &gt; All In One Prefab Builder &gt; Prefab Builder</strong> (<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>W</kbd>) and click <strong>Try the sample kits</strong>, or add your own pack with <strong>Tools &gt; All In One Prefab Builder &gt; Add Pack...</strong></li>
    <li>On the review screen, check the categories, fronts and grid cell. Pieces marked <strong>!</strong> or <strong>?</strong> deserve a look. Click <strong>Create Kit</strong>.</li>
    <li>Pick a piece in the palette and click in the Scene view. <kbd>R</kbd> turns it, <kbd>T</kbd> tilts it, green means it fits.</li>
  </ol>
</div>"""


def build_docs(folder):
    folder = pathlib.Path(folder)
    out_dir = SITE / "prefab-builder" / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    order = [("Index.md", "index.html", "Overview")] + [(s, o, l) for _, s, o, l in DOCS]
    for i, (src, out, label) in enumerate(order):
        text = (folder / src).read_text(encoding="utf-8")
        if src == "Index.md":
            # Our own title and the quick start replace the file's first heading
            text = re.sub(r"^# .*\n", "", text, count=1)
            body_html = ("<h1>Prefab Builder documentation</h1>\n" + QUICK_START + "\n" + convert(text))
            title = "Prefab Builder documentation"
        else:
            title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
            body_html = convert(text)
        prev_link = f'<a href="{order[i - 1][1]}">&larr; {order[i - 1][2]}</a>' if i > 0 else "<span></span>"
        next_link = f'<a href="{order[i + 1][1]}">{order[i + 1][2]} &rarr;</a>' if i + 1 < len(order) else "<span></span>"
        body = f"""<div class="wrap docs-layout">
{docs_nav(out)}
<article class="prose">
<div class="doc-meta"><span class="label">All In One Prefab Builder Kit &middot; v{PREFAB_VERSION}</span></div>
{body_html}
<div class="doc-foot">{prev_link}{next_link}</div>
</article>
</div>"""
        description = f"{title}: documentation for the All In One Prefab Builder Kit for Unity."
        (out_dir / out).write_text(page("../../", "docs", title, description, body, f"prefab-builder/docs/{out}"),
                                   encoding="utf-8")
        print("wrote", f"prefab-builder/docs/{out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs", help="the Prefab Builder's Documentation folder, to rebuild the docs pages")
    args = parser.parse_args()
    build_pages()
    if args.docs:
        build_docs(args.docs)
