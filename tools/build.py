"""Builds the Romano Assets website: every page shares one header and footer from this file.

    python tools/build.py                                         # rebuild the hand-written pages
    python tools/build.py --docs prefab-builder=<product folder>  # also rebuild that kit's documentation

<product folder> is the kit's folder inside its Unity project, e.g.
C:\\AllInOneWorldBuilderKit\\Assets\\AllInOnePrefabBuilderKit. The docs are made from what ships in it:
  Documentation/*.md         the pages (Documentation/docs.json, if there, sets their order and sidebar groups)
  Documentation/Images/      pictures the pages use (copied to the site)
  CHANGELOG.md               the Changelog page
  Editor/**/*.cs             [Shortcut] attributes and a MouseControls list, for the Keyboard shortcuts page

A new kit: add it to PRODUCTS below, then build with --docs <slug>=<its folder>.
The docs need the `markdown` package once:  pip install markdown
The output is plain HTML next to this folder, committed as it is: GitHub Pages serves it with no build step.
Links are relative and point at index.html files, so every page also opens by double-clicking it on your computer.
"""

import argparse
import html
import json
import pathlib
import posixpath
import re
import shutil

SITE = pathlib.Path(__file__).resolve().parent.parent
PAGES = pathlib.Path(__file__).resolve().parent / "pages"

# ---- Facts used on several pages: change them here ----

SITE_URL = "https://marklromano.github.io"
STORE_URL = "https://assetstore.unity.com/packages/tools/level-design/all-in-one-prefab-builder-kit-411146"
PUBLISHER_URL = "https://assetstore.unity.com/publishers/160196"
EMAIL = "marklromano@outlook.com"
# Empty until they exist: the pages then show "soon" instead of a link.
DISCORD_URL = "https://discord.gg/AmpBDxRAKu"
ISSUES_URL = "https://github.com/marklromano/RomanoAssetSupport/issues"
PREFAB_VERSION = "0.8.0"
SAVE_VERSION = "1.0.0"
YEAR = "2026"

ICON_EXTERNAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>')

# ---- The kits. Each one with docs gets <slug>/docs/ ----

PRODUCTS = [
    {
        "slug": "prefab-builder",
        "name": "All In One Prefab Builder Kit",
        "short": "Prefab Builder",
        "accent": "c-prefab",
        "status": "live",
        "version": PREFAB_VERSION,
        "store": STORE_URL,
        "summary": "Turn any pack of prefabs into a world-building kit: snap, draw roads, scatter, fence, dress streets, "
                   "settle with physics and check your scene, all from one window.",
        "requirements": ["Unity 6000.3+", "Built-in & URP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Prefab Builder",
        "quick_start": [
            "Import the package from the Asset Store. Everything lands in <code>Assets/AllInOnePrefabBuilderKit/</code>.",
            "Open <strong>Tools &gt; All In One Prefab Builder &gt; Prefab Builder</strong> (<kbd>Alt</kbd>+<kbd>Shift</kbd>+<kbd>W</kbd>) "
            "and click <strong>Try the sample kits</strong>, or add your own pack with <strong>Tools &gt; All In One Prefab Builder &gt; Add Pack...</strong>",
            "On the review screen, check the categories, fronts and grid cell. Pieces marked <strong>!</strong> or <strong>?</strong> "
            "deserve a look. Click <strong>Create Kit</strong>.",
            "Pick a piece in the palette and click in the Scene view. <kbd>R</kbd> turns it, <kbd>T</kbd> tilts it, green means it fits.",
        ],
        # Used when the kit has no Documentation/docs.json: (sidebar group, source .md, output .html, sidebar title)
        "pages": [
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
        ],
        # Friendlier names for the shortcut groups (the first part of each shortcut's id)
        "shortcut_groups": {
            "Line": "Row, Spline, Fill, Fence, Closures, Signs",
            "Place": "Any placing tool",
            "Re-roll": "Re-roll (after a Fill, Brush stroke, Row or Spline)",
            "Physics": "Physics > Place (stamp)",
        },
        # Pictures the site adds under a page's opening paragraph: output .html -> (assets/img file, caption)
        "page_images": {
            "getting-started.html": ("showcase-hero.jpg", "Showcase City, one of the demo scenes built from the sample kits."),
            "place-tab.html": ("try-roads.jpg", "Roads drawn with Place > Roads in the Try It sample scene."),
            "dress-tab.html": ("showcase-park.jpg", "A park fenced with Dress > Fence, and street lights along every road."),
            "physics-tab.html": ("try-physics.jpg", "Containers dropped and settled with the Physics tab in the Try It scene."),
        },
    },
    {
        # In development: its page is up, its docs build with --docs save-kit=<folder> but are published (and listed
        # on the docs hub) only once "status" is "live" and "store" is set, on launch day.
        "slug": "save-kit",
        "name": "All In One Save Kit",
        "short": "Save Kit",
        "accent": "c-save",
        "status": "in development",
        "version": SAVE_VERSION,
        "store": "",
        "summary": "Save and restore player progress, world objects and settings, with slots, autosaves, a finished save "
                   "menu, backups and automatic recovery from damaged saves.",
        "requirements": ["Unity 2022.3+", "Built-in, URP & HDRP", "No code needed", "Full C# source"],
        "menu": "Tools > All In One Save Kit",
        "quick_start": [
            "Import the package from the Asset Store. Everything lands in <code>Assets/AllInOneSaveKit/</code>, and the Start window opens.",
            "In the Start window, click <strong>Fix</strong> on any item of the setup check that isn't ticked.",
            "Click <strong>Make objects remember</strong>, pick the objects that should keep their state, and tick what each one keeps.",
            "Press Play, then <kbd>F5</kbd> to save and <kbd>F9</kbd> to load. A note in the Game view says what was saved and what came back.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "Walkthroughs.md", "walkthroughs.html", "Walkthroughs"),
            ("Walkthroughs", "Walkthroughs/FirstSave.md", "walkthrough-first-save.html", "Your first save"),
            ("Walkthroughs", "Walkthroughs/WorldObjects.md", "walkthrough-world-objects.html", "World objects"),
            ("Walkthroughs", "Walkthroughs/SaveMenu.md", "walkthrough-save-menu.html", "The save menu"),
            ("Walkthroughs", "Walkthroughs/BackupsAndRecovery.md", "walkthrough-backups.html", "Backups and recovery"),
            ("Walkthroughs", "Walkthroughs/GameUpdates.md", "walkthrough-game-updates.html", "Game updates"),
            ("Learn", "Guide.md", "guide.html", "Guide"),
            ("Learn", "GameUpdates.md", "game-updates.html", "Game updates and migrations"),
            ("Learn", "Coop.md", "coop.html", "Co-op"),
            ("Learn", "SteamCloud.md", "steam-cloud.html", "Steam Cloud"),
            ("Reference", "Reference.md", "reference.html", "Reference"),
            ("Reference", "ApiReference.md", "api.html", "API reference"),
            ("Reference", "LimitsAndFAQ.md", "limits-and-faq.html", "Limits and FAQ"),
            ("Reference", "Troubleshooting.md", "troubleshooting.html", "Troubleshooting"),
            ("Reference", "KnownIssues.md", "known-issues.html", "Known issues"),
            ("Reference", "Support.md", "support.html", "Support"),
        ],
        "shortcut_groups": {},
        "page_images": {},
    },
]

# Kits without docs yet, for the docs hub
COMING = [
    ("All In One Save Kit", "c-save", "In development"),
    ("Interaction Kit", "c-interact", "In development"),
    ("Settings & Menu Kit", "c-settings", "Planned"),
    ("All In One Runtime Building Kit", "c-runtime", "In development"),
]

NAV = [
    ("products", "Products", "index.html#products"),
    ("prefab", "Prefab Builder", "prefab-builder/index.html"),
    ("docs", "Docs", "docs/index.html"),
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
          <li><a href="{root}save-kit/index.html">Save Kit</a></li>
          <li><a href="{root}index.html#products">Coming next</a></li>
          <li><a href="{PUBLISHER_URL}" rel="noopener">Publisher page</a></li>
        </ul>
      </div>
      <div>
        <h4>Learn</h4>
        <ul>
          <li><a href="{root}docs/index.html">Documentation</a></li>
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


def page(root, active, title, description, body, path, scripts=""):
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
{scripts}
</body>
</html>
"""


def fill(text, root):
    """Replaces {{name}} placeholders in a page fragment."""
    values = {
        "root": root, "store": STORE_URL, "publisher": PUBLISHER_URL, "email": EMAIL,
        "version": PREFAB_VERSION, "external": ICON_EXTERNAL,
        "discord_tile": discord_tile(), "issues_tile": issues_tile(root), "discord_button": discord_button(),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)


def discord_tile():
    if DISCORD_URL:
        return (f'<a class="tile" href="{DISCORD_URL}" rel="noopener"><span class="label">Community</span>'
                '<h3>Discord</h3><p>Ask questions, share what you build, hear about updates first.</p></a>')
    return ('<div class="tile tile-soon"><span class="label">Community <span class="pill">Soon</span></span>'
            '<h3>Discord</h3><p>A server for questions, show and tell, and update news is being set up.</p></div>')


def discord_button():
    if DISCORD_URL:
        return f'<a class="btn" href="{DISCORD_URL}" rel="noopener">Join the Discord {ICON_EXTERNAL}</a>'
    return f'<a class="btn" href="mailto:{EMAIL}">Email us</a>'


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
    ("save-kit.html", "save-kit/index.html", "../", "save",
     "All In One Save Kit",
     "Save and restore player progress, world objects and settings in Unity: no code needed, slots, autosaves, a "
     "finished save menu, backups and automatic recovery from damaged saves. In development."),
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
        write(out, page(root, active, title, description, body, out))
    build_docs_hub()


def write(out, text):
    target = SITE / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print("wrote", out)


def build_docs_hub():
    """docs/index.html: every kit's documentation in one place."""
    cards = []
    for p in PRODUCTS:
        if p["status"] != "live":
            continue
        d = f"../{p['slug']}/docs/"
        cards.append(f"""<article class="product product-flag {p['accent']}">
  <div class="flag-copy">
    <div class="product-top"><span class="pill pill-live">v{p['version']}</span></div>
    <h2>{p['name']}</h2>
    <p>{p['summary']}</p>
    <div class="btn-row">
      <a class="btn" href="{d}index.html">Open the documentation</a>
      <a class="btn btn-ghost" href="{d}getting-started.html">Getting started</a>
    </div>
  </div>
  <ul class="doc-links">
    <li><a href="{d}index.html#quick-start"><strong>Quick start</strong><span>From import to your first placed piece</span></a></li>
    <li><a href="{d}shortcuts.html"><strong>Keyboard shortcuts</strong><span>Every key and mouse control</span></a></li>
    <li><a href="{d}troubleshooting.html"><strong>Troubleshooting</strong><span>Common problems and their fixes</span></a></li>
    <li><a href="{d}changelog.html"><strong>Changelog</strong><span>What changed in each version</span></a></li>
  </ul>
</article>""")
    soon = "".join(
        f'<article class="product product-planned {accent}"><div class="product-top"><h3>{html.escape(name)}</h3>'
        f'<span class="pill{" pill-dev" if status == "In development" else ""}">{status}</span></div>'
        f'<p>Its documentation goes up here the day it launches.</p></article>'
        for name, accent, status in COMING)
    body = f"""<section class="product-hero blueprint">
  <div class="wrap hero-copy">
    <p class="label label-accent">Documentation</p>
    <h1>Learn every kit, tool by tool</h1>
    <p class="lead">Step-by-step guides, a page for every feature, and the full shortcut list, kept in step with what ships in each package.</p>
  </div>
</section>
<section class="section">
  <div class="wrap products">
    {"".join(cards)}
    {soon}
  </div>
</section>"""
    write("docs/index.html", page("../", "docs", "Documentation",
                                  "Documentation for every Romano Assets Unity tool.", body, "docs/index.html"))


# ---- Docs: a kit's offline Documentation/*.md as a documentation site ----

def slugify(value, separator="-"):
    """GitHub's heading anchors, so links written for GitHub (#floors--terrain) keep working."""
    value = value.strip().lower()
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"[^\w\- ]", "", value)
    return value.replace(" ", "-")


def plain(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def load_pages(product, docs_dir):
    """[(group, source, output, title)] from Documentation/docs.json, or the product's own list."""
    manifest = docs_dir / "docs.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        # Keep the addresses pages already have (links to them are out in the world)
        known = {src: out for _, src, out, _ in product["pages"]}
        pages = []
        for group in data["groups"]:
            for entry in group["pages"]:
                src = entry["file"]
                if src == "Index.md":
                    out = "index.html"
                else:
                    out = (entry.get("output") or known.get(src)
                           or re.sub(r"(?<!^)(?=[A-Z])", "-", pathlib.Path(src).stem).lower() + ".html")
                pages.append((group["title"], src, out, entry.get("title") or pathlib.Path(src).stem))
        return pages
    return list(product["pages"])


def index_descriptions(index_md):
    """The 'What it covers' column of Documentation/Index.md, by linked file."""
    return {m.group(1): m.group(2).strip()
            for m in re.finditer(r"^\|\s*\[[^\]]+\]\(([^)#]+\.md)\)\s*\|\s*(.+?)\s*\|\s*$", index_md, re.M)}


CALLOUT = re.compile(r'<blockquote>\s*<p>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*', re.I)


def convert(md_text, doc_out, folder=""):
    """Markdown to HTML; returns (html, [(level, id, title)]). folder: the page's subfolder of Documentation, if any."""
    import markdown  # only needed for the docs
    from markdown.extensions.toc import TocExtension

    def relink(match):
        target, anchor = match.group(1), match.group(2) or ""
        key = posixpath.normpath(posixpath.join(folder, target)) if folder else target
        return f"]({doc_out.get(key, target)}{anchor})"

    # Links between the .md files become links between the .html pages; Images/ moves to img/
    md_text = re.sub(r"\]\((?!https?:)((?:\.\./|[A-Za-z]+/)?[A-Za-z]+\.md)(#[^)]*)?\)", relink, md_text)
    md_text = re.sub(r"\]\((?:\./)?Images/", "](img/" + (folder + "/" if folder else ""), md_text)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists",
                                       TocExtension(slugify=slugify, toc_depth="2-3")])
    out = md.convert(md_text)
    toc = []

    def walk(tokens):
        for t in tokens:
            toc.append((t["level"], t["id"], plain(t["name"])))
            walk(t["children"])
    walk(md.toc_tokens)

    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # GitHub-style callouts: > [!NOTE] ...
    out = CALLOUT.sub(lambda m: f'<blockquote class="note note-{m.group(1).lower()}"><p><strong class="note-title">'
                                f'{m.group(1).title()}</strong> ', out)
    # Images get a frame; their alt text becomes the caption
    out = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)"\s*/?></p>',
                 r'<figure class="doc-figure"><img src="\2" alt="\1" loading="lazy"><figcaption>\1</figcaption></figure>', out)
    # A link icon on every section heading, to share a link to it
    out = re.sub(r'<(h[23]) id="([^"]+)">(.*?)</\1>',
                 r'<\1 id="\2">\3 <a class="anchor" href="#\2" aria-label="Link to this section">#</a></\1>', out)
    return out, toc


def sections(body_html, title, url):
    """Search entries: one per section of a page."""
    entries = []
    parts = re.split(r'(<h[123][^>]*>.*?</h[123]>)', body_html)
    heading, anchor = title, ""
    for part in parts:
        m = re.match(r'<h([123])(?: id="([^"]+)")?[^>]*>(.*?)</h\1>', part)
        if m:
            heading = plain(re.sub(r'<a class="anchor".*?</a>', "", m.group(3)))
            anchor = m.group(2) or ""
            continue
        text = plain(part)
        if text or anchor:
            entries.append({"p": title, "h": heading, "u": url + (f"#{anchor}" if anchor else ""), "x": text[:600]})
    return entries


# ---- The Keyboard shortcuts page, read from the kit's [Shortcut] attributes ----

KEY_NAMES = {"LeftBracket": "[", "RightBracket": "]", "Backspace": "Backspace", "Return": "Enter", "Space": "Space",
             "Escape": "Esc", "Delete": "Delete", "Tab": "Tab", "Minus": "-", "Equals": "=", "Comma": ",",
             "Period": ".", "Slash": "/", "Backslash": "\\", "Semicolon": ";", "Quote": "'", "BackQuote": "`"}


def key_label(code):
    if code.startswith("Alpha"):
        return code[5:]
    if code.startswith("Keypad"):
        return "Num " + code[6:]
    return KEY_NAMES.get(code, code)


def kbd(combo):
    return "+".join(f"<kbd>{html.escape(k)}</kbd>" for k in combo)


def read_shortcuts(editor_dir):
    """[(group, action, [keys], hold)] and [(action, keys)] mouse controls, from the C# source."""
    sources = [p.read_text(encoding="utf-8", errors="ignore") for p in sorted(editor_dir.rglob("*.cs"))]
    text = "\n".join(sources)
    consts = dict(re.findall(r'const string (\w+)\s*=\s*"([^"]*)"\s*;', text))
    for name, rest in re.findall(r'const string (\w+)\s*=\s*(\w+\s*\+\s*"[^"]*")\s*;', text):
        base, lit = re.match(r'(\w+)\s*\+\s*"([^"]*)"', rest).groups()
        consts[name] = consts.get(base, "") + lit
    mods = {"AltShift": ["Alt", "Shift"]}
    shortcuts = []
    for kind, args in re.findall(r'\[(Shortcut|ClutchShortcut)\((.*?)\)\]', text):
        parts = [a.strip() for a in re.split(r',(?![^(]*\))', args)]
        m = re.match(r'(?:(\w+)\s*\+\s*)?"([^"]*)"$', parts[0])
        sid = (consts.get(m.group(1), "") if m.group(1) else "") + m.group(2) if m else consts.get(parts[0], "")
        key = next((p.split(".")[1] for p in parts if p.startswith("KeyCode.")), None)
        if not sid or not key:
            continue  # no default key: the user sets one if they want it
        combo = []
        for p in parts:
            if p in mods:
                combo += mods[p]
            for mod in re.findall(r'ShortcutModifiers\.(\w+)', p):
                combo.append({"Action": "Ctrl/Cmd"}.get(mod, mod))
        combo.append(key_label(key))
        path = sid.split("/")[1:] if "/" in sid else [sid]
        if len(path) == 1:
            group, action = "General (anywhere in the editor)", path[0]
        elif path[0] == "Tools":
            group, action = "Pick a tool", " > ".join(path[1:])
            if re.fullmatch(r"Tool \d", action):
                action += " of the open tab"
        elif path[0] == "Tabs":
            group, action = "Switch tabs", path[-1].replace("Tab ", "Tab ") + " (in the order the tabs are shown)"
        else:
            group, action = path[0], " ".join(path[1:])
        shortcuts.append((group, action, combo, kind == "ClutchShortcut"))
    mouse = []
    block = re.search(r'MouseControls\s*=\s*\{(.*?)\};', text, re.S)
    if block:
        mouse = re.findall(r'\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\)', block.group(1))
    return shortcuts, mouse


def shortcuts_markdown(product, shortcuts, mouse):
    lines = [f"# Keyboard shortcuts", "",
             f"Every {product['short']} shortcut with its default keys. They are Unity shortcuts, so you can change any of "
             "them in **Edit > Shortcuts** (or the kit's own Settings > Hotkeys), and the tools follow your keys. "
             "Tool keys work while the mouse is over the Scene view or the kit's window.", ""]
    groups = {}
    names = product.get("shortcut_groups", {})
    for group, action, combo, hold in shortcuts:
        groups.setdefault(names.get(group, group), []).append((action, combo, hold))
    order = sorted(groups, key=lambda g: (g != "General (anywhere in the editor)", g in ("Pick a tool", "Switch tabs"), g))
    for g in order:
        lines += [f"## {g}", "", "| Action | Keys |", "|---|---|"]
        for action, combo, hold in groups[g]:
            note = " (press: one step; hold and move the mouse: freely)" if hold else ""
            lines.append(f"| {action}{note} | {kbd(combo)} |")
        lines.append("")
    if mouse:
        lines += ["## Mouse", "", "| Action | How |", "|---|---|"]
        for action, how in mouse:
            lines.append(f"| {action} | {how} |")
        lines.append("")
    return "\n".join(lines)


# ---- Docs pages ----

def docs_nav(groups, current):
    out = []
    for name, items in groups:
        links = "".join(f'<a href="{o}"{" aria-current=\"page\"" if o == current else ""}>{html.escape(t)}</a>'
                        for o, t in items)
        out.append(f'<div class="docs-group">{f"<p class=label>{name}</p>" if name else ""}{links}</div>')
    links = "".join(out)
    return links


def docs_side(product, groups, current):
    links = docs_nav(groups, current)
    return f"""<aside class="docs-side" aria-label="Documentation">
  <div class="docs-product"><a href="index.html">{html.escape(product['short'])} docs</a><span class="pill">v{product['version']}</span></div>
  <div class="docs-search" hidden>
    <label class="sr-only" for="docs-q">Search the documentation</label>
    <input id="docs-q" type="search" placeholder="Search the docs" autocomplete="off" spellcheck="false">
    <kbd class="docs-search-key" aria-hidden="true">/</kbd>
    <div class="docs-results" id="docs-results" role="listbox" hidden></div>
  </div>
  <nav class="docs-nav"><div class="docs-links">{links}</div>
    <details><summary>All pages</summary><div class="docs-links">{links}</div></details>
  </nav>
</aside>"""


def toc_html(toc):
    items = [(lvl, i, t) for lvl, i, t in toc if lvl in (2, 3)]
    if len(items) < 2:
        return '<nav class="docs-toc" aria-label="On this page"></nav>'
    lis = "".join(f'<li class="toc-{lvl}"><a href="#{i}">{html.escape(t)}</a></li>' for lvl, i, t in items)
    return f'<nav class="docs-toc" aria-label="On this page"><p class="label">On this page</p><ul>{lis}</ul></nav>'


def report_link(title):
    if not ISSUES_URL:
        return f'<a href="mailto:{EMAIL}?subject=Docs:%20{html.escape(title)}">Something unclear? Tell us</a>'
    q = re.sub(r"\s+", "+", f"Docs: {title}")
    return f'<a href="{ISSUES_URL}/new?title={html.escape(q)}" rel="noopener">Something unclear or wrong? Tell us</a>'


def build_docs(product, kit_root):
    import markdown  # noqa: F401  (fail early with a clear message if it isn't installed)
    kit_root = pathlib.Path(kit_root)
    docs_dir = kit_root / "Documentation"
    slug = product["slug"]
    out_dir = SITE / slug / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    pages = load_pages(product, docs_dir)
    index_md = (docs_dir / "Index.md").read_text(encoding="utf-8") if (docs_dir / "Index.md").exists() else ""
    descriptions = index_descriptions(index_md)
    m = re.search(r"^Version (\d+\.\d+\.\d+)", index_md, re.M)
    product = dict(product, version=m.group(1) if m else product["version"])
    doc_out = {src: out for _, src, out, _ in pages}
    doc_out["Index.md"] = "index.html"

    # Extra generated pages: shortcuts and changelog, in the last group
    extras = []
    shortcuts, mouse = read_shortcuts(kit_root / "Editor") if (kit_root / "Editor").exists() else ([], [])
    if shortcuts:
        extras.append(("shortcuts.html", "Keyboard shortcuts", shortcuts_markdown(product, shortcuts, mouse),
                       "Every key and mouse control, and how to change them"))
    if (kit_root / "CHANGELOG.md").exists():
        cl = (kit_root / "CHANGELOG.md").read_text(encoding="utf-8")
        cl = re.sub(r"^# .*\n", "# Changelog\n", cl, count=1)
        extras.append(("changelog.html", "Changelog", cl, "What changed in each version"))
        doc_out.setdefault("Changelog.md", "changelog.html")  # a kit's own copy of the changelog
    last_group = pages[-1][0] if pages else "Reference"

    groups = []
    for g, _, out, title in pages:
        if not groups or groups[-1][0] != g:
            groups.append((g, []))
        groups[-1][1].append((out, title))
    for out, title, _, _ in extras:
        if groups and groups[-1][0] == last_group:
            groups[-1][1].append((out, title))
        else:
            groups.append((last_group, [(out, title)]))
    if not any(out == "index.html" for _, _, out, _ in pages):
        # The overview (made here, not from a page) opens the sidebar on its own
        groups.insert(0, ("", [("index.html", "Overview")]))
    pages = [p for p in pages if p[2] != "index.html"]

    order = [(o, t, g) for g, items in groups for o, t in items]

    # Pictures from the kit's Documentation/Images
    if (docs_dir / "Images").exists():
        shutil.copytree(docs_dir / "Images", out_dir / "img", dirs_exist_ok=True)
    for folder in sorted({posixpath.dirname(src) for _, src, _, _ in pages} - {""}):
        if (docs_dir / folder / "Images").exists():
            shutil.copytree(docs_dir / folder / "Images", out_dir / "img" / folder, dirs_exist_ok=True)

    search = []
    rendered = {}
    folders = {}
    for _, src, out, title in pages:
        text = (docs_dir / src).read_text(encoding="utf-8")
        rendered[out] = (title, text, descriptions.get(src, ""))
        folders[out] = posixpath.dirname(src)
    for out, title, text, desc in extras:
        rendered[out] = (title, text, desc)

    for i, (out, nav_title, group) in enumerate(order):
        if out == "index.html":
            body_html, toc = docs_home(product, groups, rendered)
            h1 = f"{product['short']} documentation"
        else:
            title, text, _ = rendered[out]
            body_html, toc = convert(text, doc_out, folders.get(out, ""))
            m = re.search(r"<h1[^>]*>(.*?)</h1>", body_html)
            h1 = plain(m.group(1)) if m else title
            if out in product.get("page_images", {}):
                img, cap = product["page_images"][out]
                fig = (f'<figure class="doc-figure"><img src="../../assets/img/{img}" alt="{html.escape(cap)}" '
                       f'width="1200" height="675" loading="lazy"><figcaption>{html.escape(cap)}</figcaption></figure>')
                body_html = re.sub(r"(</h1>\s*<p>.*?</p>)", lambda m_: m_.group(1) + fig, body_html, count=1, flags=re.S)
            search += sections(body_html, h1, out)
        crumbs = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="../../docs/index.html">Docs</a><span>/</span>'
                  f'<a href="index.html">{html.escape(product["short"])}</a>'
                  + (f'<span>/</span><span>{html.escape(group)}</span>' if group else "") + "</nav>")
        prev_card = (f'<a class="pager prev" href="{order[i - 1][0]}"><span class="label">Previous</span>{html.escape(order[i - 1][1])}</a>'
                     if i > 0 else "<span></span>")
        next_card = (f'<a class="pager next" href="{order[i + 1][0]}"><span class="label">Next</span>{html.escape(order[i + 1][1])}</a>'
                     if i + 1 < len(order) else "<span></span>")
        body = f"""<div class="wrap docs-shell">
{docs_side(product, groups, out)}
<article class="prose" id="doc">
{crumbs}
{body_html}
<div class="doc-pager">{prev_card}{next_card}</div>
<p class="doc-report">{report_link(h1)} &middot; <a href="../../support/index.html">Get help</a></p>
</article>
{toc_html(toc)}
</div>"""
        description = (f"{h1}: documentation for the {product['name']} for Unity." if out != "index.html"
                       else f"Documentation for the {product['name']} for Unity: quick start, every tool, shortcuts and changelog.")
        scripts = '<script src="search-index.js"></script>\n<script src="../../assets/docs.js"></script>'
        write(f"{slug}/docs/{out}", page("../../", "docs", h1 if out != "index.html" else f"{product['name']} documentation",
                                         description, body, f"{slug}/docs/{out}", scripts))

    index_js = "window.DOCS_INDEX=" + json.dumps(search, ensure_ascii=False, separators=(",", ":")) + ";\n"
    write(f"{slug}/docs/search-index.js", index_js)


def docs_home(product, groups, rendered):
    steps = "".join(f"<li>{s}</li>" for s in product["quick_start"])
    reqs = "".join(f"<li>{html.escape(r)}</li>" for r in product["requirements"])
    sections_html = []
    for name, items in groups:
        items = [(o, t) for o, t in items if o != "index.html"]
        if not items:
            continue
        cards = []
        for out, title in items:
            desc = rendered[out][2]
            if not desc:
                m = re.search(r"^(?!#|\||-|\s)(.+)$", rendered[out][1], re.M)
                desc = m.group(1) if m else ""
                desc = re.sub(r"[*`]", "", desc)
                desc = desc[:150].rsplit(" ", 1)[0] + "..." if len(desc) > 150 else desc
            desc = html.escape(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc))
            cards.append(f'<a class="doc-card" href="{out}"><strong>{html.escape(title)}</strong><span>{desc}</span></a>')
        sections_html.append(f'<h2 id="{slugify(name)}">{html.escape(name)}</h2><div class="doc-cards">{"".join(cards)}</div>')
    toc = [(2, "quick-start", "Quick start")] + [(2, slugify(n), n) for n, items in groups
                                                  if any(o != "index.html" for o, _ in items)] + [(2, "help", "Need help?")]
    return f"""<h1>{html.escape(product['name'])} documentation</h1>
<p class="lead">{product['summary']}</p>
<ul class="specs">{reqs}<li>Version {product['version']}</li></ul>
<div class="btn-row">
  <a class="btn" href="getting-started.html">Get started</a>
  {f'<a class="btn btn-ghost" href="{product["store"]}" rel="noopener">Asset Store {ICON_EXTERNAL}</a>' if product["store"] else ""}
</div>
<div class="callout" id="quick-start">
  <p class="label label-accent">Quick start: five minutes</p>
  <ol>{steps}</ol>
</div>
{"".join(sections_html)}
<h2 id="help">Need help?</h2>
<div class="doc-cards">
  <a class="doc-card" href="troubleshooting.html"><strong>Troubleshooting</strong><span>Answers to the most common problems.</span></a>
  {f'<a class="doc-card" href="{DISCORD_URL}" rel="noopener"><strong>Discord</strong><span>Ask other users and the developer.</span></a>' if DISCORD_URL else ''}
  <a class="doc-card" href="../../support/index.html"><strong>Support</strong><span>Report a bug or email the developer.</span></a>
</div>""", toc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs", action="append", default=[], metavar="SLUG=FOLDER",
                        help="rebuild a kit's docs from its product folder (repeatable)")
    args = parser.parse_args()
    build_pages()
    products = {p["slug"]: p for p in PRODUCTS}
    for spec in args.docs:
        slug, _, folder = spec.partition("=")
        if slug not in products:
            raise SystemExit(f"Unknown kit '{slug}'. Add it to PRODUCTS in tools/build.py first.")
        build_docs(products[slug], folder)
