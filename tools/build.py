"""Builds the Rare Geometry website: every page shares one header and footer from this file.

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
import urllib.parse

SITE = pathlib.Path(__file__).resolve().parent.parent
PAGES = pathlib.Path(__file__).resolve().parent / "pages"

# ---- Facts used on several pages: change them here ----

SITE_URL = "https://raregeometry.github.io"
STORE_URL = "https://assetstore.unity.com/packages/tools/level-design/all-in-one-prefab-builder-kit-411146"
PUBLISHER_URL = "https://assetstore.unity.com/publishers/160196"
EMAIL = "raregeometrysupport@gmail.com"
# Empty until they exist: the pages then show "soon" instead of a link.
DISCORD_URL = "https://discord.gg/AmpBDxRAKu"
ISSUES_URL = "https://github.com/raregeometry/Support/issues"
GITHUB_URL = "https://github.com/raregeometry"
PREFAB_VERSION = "1.0.0"
SAVE_VERSION = "1.0.0"
INTERACTION_VERSION = "1.0.0"
RUNTIME_BUILDING_VERSION = "1.0.0"
SETTINGS_VERSION = "1.0.0"
BUG_REPORT_VERSION = "1.0.1"
FOOTSTEP_VERSION = "0.1.0"
HIT_FEEDBACK_VERSION = "1.0.0"
TUTORIAL_VERSION = "1.0.0"
WAYPOINT_VERSION = "1.0.0"
BEARING_VERSION = "1.0.0"
YEAR = "2026"

ICON_EXTERNAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>')

# ---- The kits. Each one with docs gets <slug>/docs/ ----

PRODUCTS = [
    {
        "slug": "prefab-builder",
        # Snapbuild is this kit's 2.0: the page forwards there, the 1.0 manual stays for 1.0 owners.
        "retired_to": "snapbuild",
        "keep_docs": True,
        "name": "All In One Prefab Builder Kit",
        "short": "Prefab Builder",
        "accent": "c-prefab",
        "status": "live",
        "version": PREFAB_VERSION,
        "store": STORE_URL,
        "summary": "Turn any pack of prefabs into a world-building kit: snap, draw roads, scatter, fence, dress streets, "
                   "settle with physics and check your scene, all from one window.",
        "requirements": ["Unity 6000.0 LTS+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Prefab Builder",
        # Where the kit's "copy support info" button is, for the generated Support page (if the kit has no Support.md)
        "support_info": "In the Prefab Builder window, click **\u22ee > Copy support info**",
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
            "getting-started.html": ("prefab-builder/12-included.jpg", "Everything that comes with the kit: sample kits, demo scenes, docs and support."),
            "adding-packs.html": ("prefab-builder/02-three-steps.jpg", "Add a pack, check one review screen, build: your first street in minutes."),
            "place-tab.html": ("prefab-builder/06-stamp.jpg", "Stamp: click to place, and the piece snaps flush against its neighbour."),
            "dress-tab.html": ("prefab-builder/04-street.jpg", "Dress > Street: street lights and bins along a road, doorways kept clear."),
            "physics-tab.html": ("prefab-builder/07-physics.jpg", "Physics: pieces inside each other, untangled and settled."),
            "check-tab.html": ("prefab-builder/11-check.jpg", "Check > Performance: what the scene costs to draw, and its heaviest meshes."),
        },
    },
    {
        # Coming soon: its page is up, its docs build with --docs save-kit=<folder> but are published (and listed
        # on the docs hub) only once "status" is "live" and "store" is set, on launch day.
        "slug": "save-kit",
        "retired_to": "shipready",
        "name": "All In One Save Kit",
        "short": "Save Kit",
        "accent": "c-save",
        "status": "coming soon",
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
            ("Walkthroughs", "Walkthroughs/OwnMenu.md", "walkthrough-own-menu.html", "Your own save menu (uGUI)"),
            ("Walkthroughs", "Walkthroughs/OwnMenuUIToolkit.md", "walkthrough-own-menu-ui-toolkit.html", "Your own save menu (UI Toolkit)"),
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
    {
        # Coming soon: page and docs are online before the store listing (Unity's reviewer opens them). On launch day:
        # "status": "live", "store": its Asset Store link, and the product page's pill and buttons (tools/pages/interaction-kit.html).
        "slug": "interaction-kit",
        "retired_to": "interactra",
        "name": "All In One Interaction Kit",
        "short": "Interaction Kit",
        "accent": "c-interact",
        "status": "coming soon",
        "version": INTERACTION_VERSION,
        "store": "",
        "summary": "Turn your own prefabs into doors, drawers, switches, pickups, keypads and puzzles, with prompts for "
                   "every controller, a \"why can't I interact?\" debugger and optional multiplayer.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Interaction Kit",
        "support_info": "**Tools > All In One Interaction Kit > Help and Support > Copy Support Info**",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneInteractionKit/</code>. Open "
            "<strong>Tools &gt; All In One Interaction Kit &gt; Open Demo &gt; The Locked Workshop (start here)</strong> and press Play.",
            "Open <strong>Tools &gt; All In One Interaction Kit &gt; Setup Wizard</strong> and drag your prefab into "
            "<strong>Prefab</strong>. Check the doors and drawers it found, then click <strong>Create Interactive Prefab</strong>.",
            "On your player, add an <strong>Interactor</strong> (Origin: your camera), a <strong>Look Ray Discovery</strong> "
            "and a <strong>Key Interaction Input</strong>. Add an <strong>Interaction Prompt (No Packages)</strong> to the scene.",
            "Press Play, look at your new prefab and press <kbd>E</kbd> (or <kbd>X</kbd> / <kbd>Square</kbd> on a controller).",
        ],
        "pages": [],
        "shortcut_groups": {},
        "hub_links": [
            ("index.html#quick-start", "Quick start", "From import to your first interactive prefab"),
            ("customizing.html", "Make it yours", "Themes, prompts, hold progress and the crosshair"),
            ("troubleshooting.html", "Troubleshooting", "Common problems and their fixes"),
            ("changelog.html", "Changelog", "What changed in each version"),
        ],
        "page_images": {
            "getting-started.html": ("interaction-kit/04-three-steps.jpg", "Drag in your prefab, check what the wizard found, press Play."),
            "customizing.html": ("interaction-kit/02-make-it-yours.jpg", "The same prompt in the six ready-made themes."),
            "prompts.html": ("interaction-kit/05-every-controller.jpg", "The prompt shows the button of the controller in use."),
            "power-and-puzzles.html": ("interaction-kit/08-wire-it-up.jpg", "Switches, plates and logic wired to doors and lights, no code."),
            "containers-and-loot.html": ("interaction-kit/10-clues-codes-loot.jpg", "Notes, keypads and chests from The Locked Workshop."),
            "troubleshooting.html": ("interaction-kit/07-tells-you-why.jpg", "The F3 debugger: what the player is looking at and why it can't be used."),
            "multiplayer.html": ("interaction-kit/11-2d-and-multiplayer.jpg", "A host and a client in the multiplayer demo, and the 2D demo."),
        },
    },
    {
        # Coming soon, like the Save Kit: page up, docs built locally, published on launch day.
        # Its Documentation/docs.json sets the sidebar groups, order and titles; this list only keeps the addresses.
        "slug": "runtime-building-kit",
        "retired_to": "snapbuild",
        "name": "All In One Runtime Building Kit",
        "short": "Runtime Building Kit",
        "accent": "c-runtime",
        "status": "coming soon",
        "version": RUNTIME_BUILDING_VERSION,
        "store": "",
        "summary": "Let players build bases and place furniture at runtime: turn your own models into build pieces in about "
                   "ten minutes without code, snap them together through sockets, drag out rows and areas or stamp whole "
                   "buildings, and see a plain reason whenever a spot is refused. Four ready-made themes, and every part "
                   "of the HUD, preview, words and sounds can be changed or switched off.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Runtime Building Kit",
        "support_info": "In the kit window, open the **Help** tab and click **Copy support info**",
        # Its Quick Start takes about ten minutes, not the five the docs home says by default
        "quick_start_time": "about ten minutes",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneRuntimeBuildingKit/</code>; your own pieces "
            "go to <code>Assets/AllInOneRuntimeBuildingKitData/</code>.",
            "Open <strong>Tools &gt; All In One Runtime Building Kit &gt; Open</strong>, click <strong>Open Sample Scene</strong> "
            "and press Play: <kbd>1</kbd>/<kbd>2</kbd> pick a piece, left click places, <kbd>R</kbd> turns it.",
            "Open <strong>Make Buildable</strong>, drop in your own model, check the measured size, pick a preset and "
            "click <strong>Create Piece</strong>.",
            "Click <strong>Test in Play Mode</strong>: a test scene opens with your piece ready to place. Then check "
            "<strong>Pieces</strong> and fix anything listed with one click.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "Samples.md", "samples.html", "Samples"),
            ("Start here", "Walkthroughs.md", "walkthroughs.html", "Walkthroughs"),
            ("Start here", "Upgrading.md", "upgrading.html", "Upgrading"),
            ("Using the kit", "KitWindow.md", "kit-window.html", "The kit window"),
            ("Using the kit", "MakeItYours.md", "make-it-yours.html", "Make it yours"),
            ("Using the kit", "MakeBuildable.md", "make-buildable.html", "Make Buildable"),
            ("Using the kit", "PlacementAndSockets.md", "placement-and-sockets.html", "Placement and sockets"),
            ("Using the kit", "Gameplay.md", "gameplay.html", "Costs, tools, undo, saving"),
            ("Using the kit", "Multiplayer.md", "multiplayer.html", "Multiplayer"),
            ("Reference", "Extending.md", "extending.html", "Extending (API)"),
            ("Reference", "TroubleshootingFAQ.md", "troubleshooting.html", "Troubleshooting and FAQ"),
            ("Reference", "KnownIssues.md", "known-issues.html", "Known issues"),
            ("Reference", "Support.md", "support.html", "Support"),
        ],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon, like the Save Kit: page up, docs built locally, published on launch day.
        "slug": "settings-menu-kit",
        "retired_to": "shipready",
        "name": "All In One Game Settings & Menu Kit",
        "short": "Settings & Menu Kit",
        "accent": "c-settings",
        "status": "coming soon",
        "version": SETTINGS_VERSION,
        "store": "",
        "summary": "A finished game front end: title screen, main menu, settings, pause, loading screen and dialogs, "
                   "with key rebinding, accessibility, subtitles and three themes, ready for keyboard, mouse and gamepad.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No code needed", "Full C# source"],
        "menu": "Tools > All In One Game Settings & Menu Kit",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/RomanoAssets/SettingsMenuKit/</code>.",
            "Open <strong>Tools &gt; All In One Game Settings &amp; Menu Kit</strong>. The <strong>Home</strong> tab lists the Quick Start steps.",
            "Click each step's button in order: copy the settings profile, create the audio mixer, add the front end, "
            "mark your menu scene. Each one gets a check mark.",
            "Press Play. The title screen opens; settings save, apply and come back every time.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "Samples.md", "samples.html", "Samples"),
            ("Features", "Screens.md", "screens.html", "Screens"),
            ("Features", "SettingsCatalog.md", "settings-catalog.html", "Settings catalog"),
            ("Features", "DisplaySafety.md", "display-safety.html", "Display safety"),
            ("Features", "Audio.md", "audio.html", "Audio"),
            ("Features", "Graphics.md", "graphics.html", "Graphics"),
            ("Features", "ControlsAndRebinding.md", "controls-and-rebinding.html", "Controls and rebinding"),
            ("Features", "Themes.md", "themes.html", "Themes"),
            ("Features", "Accessibility.md", "accessibility.html", "Accessibility"),
            ("Features", "Localization.md", "languages.html", "Languages"),
            ("Features", "PauseAndMultiplayer.md", "pause-and-multiplayer.html", "Pause and multiplayer"),
            ("For programmers", "ExtendingAPI.md", "extending.html", "Extending and API"),
            ("For programmers", "Upgrading.md", "upgrading.html", "Upgrading"),
            ("Reference", "SettingsReference.md", "settings-reference.html", "Settings reference"),
            ("Reference", "Troubleshooting.md", "troubleshooting.html", "Troubleshooting and FAQ"),
            ("Reference", "KnownIssues.md", "known-issues.html", "Known issues"),
            ("Reference", "Support.md", "support.html", "Support"),
        ],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon, like the Save Kit: page up, docs built locally, published on launch day.
        "slug": "bug-report-kit",
        "retired_to": "shipready",
        "free": True,
        "name": "All In One Bug Report Kit",
        "short": "Bug Report Kit",
        "accent": "c-bugreport",
        "status": "coming soon",
        "version": BUG_REPORT_VERSION,
        "store": "",
        "summary": "Testers press one key and you get one file: their words, a marked-up screenshot, a replay of the last "
                   "seconds, the log with stack traces, system info and your game's state. Plus an in-game console, "
                   "stats and debug options, and a Report Inbox in the Editor that clicks straight to the broken line.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Bug Report Kit",
        "support_info": "**Tools > All In One Bug Report Kit > Help and Support > Copy Support Info**",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneBugReportKit/</code>; your settings go to "
            "<code>Assets/AllInOneBugReportKitData/</code>.",
            "Open <strong>Tools &gt; All In One Bug Report Kit &gt; Open Demo &gt; Bug Hunt</strong> and press Play.",
            "Click <strong>Deliver the crate</strong>, press <kbd>F8</kbd>, write a line, circle the problem and click "
            "<strong>Save report</strong>.",
            "Stop playing and open <strong>Tools &gt; All In One Bug Report Kit &gt; Report Inbox</strong>. Click the "
            "stack line to open the broken script.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "Samples.md", "samples.html", "Samples"),
            ("Start here", "AddingToYourGame.md", "adding-to-your-game.html", "Adding it to your own game"),
            ("Using the kit", "ReportForm.md", "report-form.html", "The report form"),
            ("Using the kit", "DebugOverlay.md", "debug-overlay.html", "Debug overlay"),
            ("Using the kit", "ReportInbox.md", "report-inbox.html", "Report Inbox"),
            ("Using the kit", "MakeItYours.md", "make-it-yours.html", "Make it yours"),
            ("Using the kit", "BuildsAndPrivacy.md", "builds-and-privacy.html", "Builds and privacy"),
            ("Reference", "Settings.md", "settings.html", "Settings"),
            ("Reference", "Extending.md", "extending.html", "Extending (API)"),
            ("Reference", "Upgrading.md", "upgrading.html", "Upgrading"),
            ("Reference", "Troubleshooting.md", "troubleshooting.html", "Troubleshooting"),
            ("Reference", "Support.md", "support.html", "Support"),
        ],
        "shortcut_groups": {},
        # The kit's own Documentation/Images are in its pages already
        "page_images": {},
    },
    {
        # Coming soon: page up, docs built with --docs footstep-kit=<folder>, published (and listed on the docs hub)
        # on launch day with "status": "live" and "store" set. Its Documentation/docs.json sets the sidebar.
        "slug": "footstep-kit",
        "retired_to": "responsive-fx",
        "name": "All In One Surface Footstep Kit",
        "short": "Footstep Kit",
        "accent": "c-footstep",
        "status": "coming soon",
        "version": FOOTSTEP_VERSION,
        "store": "",
        "summary": "Footsteps that sound like what your characters walk on, for any controller in 3D and 2D, with effects, "
                   "footprints, AI hearing and a debugger that says why a step was silent.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Surface Footstep Kit",
        "support_info": "**Tools > All In One Surface Footstep Kit > Help and Support > Copy Support Info**",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneFootstepKit/</code>. Try "
            "<strong>Tools &gt; All In One Surface Footstep Kit &gt; Open Demo &gt; Showcase</strong> and press Play.",
            "Open <strong>Tools &gt; All In One Surface Footstep Kit &gt; Setup Wizard</strong> and pick your character.",
            "Check the surfaces it found in your scene, click <strong>Apply</strong>, then <strong>Add Footsteps</strong>.",
            "Press Play and walk. No sound? <strong>Why No Footstep?</strong> tells you why, with a fix button.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: page up, docs built with --docs hit-feedback-kit=<folder>, published (and listed on the docs hub)
        # on launch day with "status": "live" and "store" set. Its Documentation/docs.json sets the sidebar.
        "slug": "hit-feedback-kit",
        "retired_to": "responsive-fx",
        "name": "All In One Hit Feedback Kit",
        "short": "Hit Feedback Kit",
        "accent": "c-hitfeedback",
        "status": "coming soon",
        "version": HIT_FEEDBACK_VERSION,
        "store": "",
        "summary": "Make every hit land: damage numbers, hit flash, hitstop, screen shake, knockback, health bars and sound "
                   "from one component, with genre presets and a Why No Feedback? debugger.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > All In One Hit Feedback Kit",
        "support_info": "**Tools > All In One Hit Feedback Kit > Help and Support > Copy Support Info**",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/HitFeedbackKit/</code>. Try "
            "<strong>Tools &gt; All In One Hit Feedback Kit &gt; Open Demo &gt; Showcase</strong> and press Play.",
            "Select your enemies and open <strong>Tools &gt; All In One Hit Feedback Kit &gt; Setup Wizard</strong>.",
            "Pick a preset and click <strong>Add Hit Feedback</strong>.",
            "Hit them with <code>HitFeedback.Hit(enemy, 25)</code>, the Health component or a UnityEvent. Nothing? "
            "<strong>Why No Feedback?</strong> tells you why, with a fix button.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: submitted to the Asset Store (free), page and docs up so the store links work.
        # Its Documentation/docs.json sets the sidebar groups, order and titles.
        "slug": "tutorial-kit",
        "retired_to": "shipready",
        "name": "All In One Tutorial Kit",
        "short": "Tutorial Kit",
        "accent": "c-tutorial",
        "status": "coming soon",
        "free": True,
        "version": TUTORIAL_VERSION,
        "store": "",
        "summary": "In-game tutorials and onboarding without code: spotlight any button or object, show a tip, and finish "
                   "each step when the player really does it. uGUI, UI Toolkit, 2D and 3D.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No code needed", "Full C# source"],
        "menu": "Tools > All In One Tutorial Kit",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneTutorialKit/</code>.",
            "Open <strong>Tools &gt; All In One Tutorial Kit &gt; Open Demo &gt; Menu Tour (uGUI)</strong> and press Play to see it work.",
            "In your own scene, select the buttons or objects to point at and choose <strong>Add Selected As Steps</strong>.",
            "Write each step's words and press Play. Live Preview shows a step without pressing Play.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon, like the Save Kit: page up, docs built locally, published on launch day.
        "slug": "waypoint-minimap-kit",
        "retired_to": "bearing",
        "name": "All In One Waypoint & Minimap Kit",
        "short": "Waypoint & Minimap Kit",
        "accent": "c-waypoint",
        "status": "coming soon",
        "version": WAYPOINT_VERSION,
        "store": "",
        "summary": "Show players where to go: objective markers, edge arrows with distance, a compass bar, a minimap and "
                   "a full-screen map, with a one-click map maker, fog of war and region discovery.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No code needed", "Full C# source"],
        "menu": "Tools > All In One Waypoint & Minimap Kit",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/AllInOneWaypointKit/</code>.",
            "Open <strong>Tools &gt; All In One Waypoint &amp; Minimap Kit &gt; Setup Wizard</strong>. It adds the HUD, "
            "finds your player and camera, and picks a look.",
            "Add a <strong>Waypoint</strong> component to any object and pick an icon.",
            "Press Play. The waypoint shows on screen, at the screen edge, on the compass and on the minimap; M opens the map.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "Samples.md", "samples.html", "Demo scenes"),
            ("Start here", "FitYourGame.md", "fit-your-game.html", "Fit it into your game"),
            ("Features", "Waypoint.md", "waypoint.html", "The Waypoint component"),
            ("Features", "Hud.md", "hud.html", "The HUD: markers, edge arrows, compass, radar"),
            ("Features", "MakeItYours.md", "make-it-yours.html", "Make it yours"),
            ("Features", "Map.md", "map.html", "Minimap and full-screen map"),
            ("Features", "Discovery.md", "discovery.html", "Fog of war and region discovery"),
            ("Features", "Trails.md", "trails.html", "Objective trails, events and saving"),
            ("Features", "TwoD.md", "2d.html", "2D and top-down games"),
            ("Features", "Debugger.md", "debugger.html", "Why Can't I See It?"),
            ("For programmers", "Extending.md", "extending.html", "Code and your own UI"),
            ("For programmers", "Upgrading.md", "upgrading.html", "Upgrading"),
            ("Reference", "Troubleshooting.md", "troubleshooting.html", "Troubleshooting"),
            ("Reference", "Support.md", "support.html", "Support"),
        ],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: page, docs (five manuals in one: --docs shipready=<stage made by Shipready's DevTools>) and the
        # web demo (shipready/demo/) are up so the store description's links work. Launch day: "status": "live", "store".
        "slug": "shipready",
        "lineup": True,
        "name": "Shipready",
        "short": "Shipready",
        "the": "",
        "accent": "c-shipready",
        "status": "coming soon",
        "version": "1.0.0",
        "store": "",
        "summary": "Menus, settings, saves, tutorials and playtest tools in one connected package: the title screen, the "
                   "settings players expect, saves that survive crashes, first-time tours and bug reports with steps.",
        "requirements": ["Unity 6000.0.85f1+", "Built-in, URP & HDRP", "Unity UI + TextMesh Pro", "Full C# source"],
        "menu": "Tools > Shipready",
        "support_info": "Click the **?** in any Shipready window, then **Copy system info**",
        "quick_start": [
            "Import the package. Everything lands in <code>Assets/RareGeometry/Shipready/</code>. Try "
            "<code>Samples/LighthouseBay/Showcase_LighthouseBay.unity</code> and press Play.",
            "Open <strong>Tools &gt; Shipready &gt; Launch Desk</strong> and pick your game's starting point.",
            "Click <strong>Connect My Game</strong>. Every step is shown before anything changes.",
            "Press Play: the title screen opens, settings apply and the game saves and continues.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: page, manual and playable web demo up (Mark, 12 Nov: "push all five product pages, docs and web
        # demos"); on launch day set "status": "live" and "store".
        "slug": "bearing",
        "lineup": True,
        "name": "Bearing",
        "short": "Bearing",
        "the": "",
        "accent": "c-bearing",
        "status": "coming soon",
        "version": BEARING_VERSION,
        "store": "",
        "summary": "Compass, minimap, world markers and a full-screen map built from your level, with routes that follow "
                   "your roads, fast travel, fog of war and floors for buildings.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "Both input systems", "Full C# source"],
        "menu": "Tools > Bearing",
        "support_info": "In **Tools > Bearing > Help and Support**, click **Copy system info**",
        "quick_start": [
            "Import the package. Bearing lands in <code>Assets/RareGeometry/Bearing/</code>.",
            "Open <strong>Tools &gt; Bearing &gt; Setup Wizard</strong>. It checks your scene and adds the HUD, your player and camera.",
            "Add a <strong>Waypoint</strong> to a landmark and pick an icon, or add places from the <strong>Chart Table</strong>.",
            "Bake the map from the Waypoint Map component, press Play and press <kbd>M</kbd> for the full map.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Snapbuild is the Prefab Builder Kit's 2.0: the same Asset Store listing, renamed. Page, docs
        # (--docs snapbuild=<its product folder>) and the web demo (snapbuild/demo/) are up.
        "slug": "snapbuild",
        "lineup": True,
        "name": "Snapbuild",
        "short": "Snapbuild",
        "the": "",
        "accent": "c-prefab",
        "status": "live",
        "version": "2.0.0",
        "store": STORE_URL,
        "summary": "Build whole worlds from the prefabs you already own: stamp and paint them on a grid that snaps, draw roads "
                   "that join themselves, dress streets in one click and drag out whole buildings.",
        "requirements": ["Unity 6000.0.85f1+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > Snapbuild",
        "support_info": "In the Level Builder, click **\u22ee > Copy support info**",
        "quick_start": [
            "Import the package from the Asset Store. Everything lands in <code>Assets/RareGeometry/</code>.",
            "Open <strong>Tools &gt; Snapbuild &gt; Level Builder</strong> and click <strong>Try the sample city</strong> on Home, "
            "or add your own pack with <strong>Turn my pack into a kit</strong>.",
            "Open <strong>Build &gt; Rooms</strong> and drag a rectangle in the Scene view: a see-through ghost shows the building; let go to build it.",
            "Open <strong>Build &gt; Roads</strong> and drag along the grid, then <strong>Dress &gt; Street</strong> to line it with lights and bins.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: page and playable web demo up (Mark, 12 Nov: "push all five product pages, docs and web demos");
        # on launch day set "status": "live" and "store".
        "slug": "interactra",
        "lineup": True,
        "name": "Interactra",
        "short": "Interactra",
        "the": "",
        "accent": "c-interactra",
        "status": "coming soon",
        "version": "1.0.0",
        "store": "",
        "summary": "Make anything interactive, then let players build: doors, switches, keys and elevators from your "
                   "own prefabs, runtime building with ghosts, blueprints and wiring, and one save for all of it.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "Both input systems", "Full C# source"],
        "menu": "Tools > Interactra",
        "support_info": "In **Tools > Interactra > Workbench**, open **Help**, then **Copy system info**",
        "quick_start": [
            "Import the package. Interactra lands in <code>Assets/RareGeometry/Interactra/</code>.",
            "Open <strong>Tools &gt; Interactra &gt; Open Demo</strong> and play the Buildable Puzzle House.",
            "Open <strong>Tools &gt; Interactra &gt; Setup Wizard</strong>, pick your prefab and what it does.",
            "Open <strong>Tools &gt; Interactra &gt; Workbench</strong> to set up building pieces, wiring and rules.",
        ],
        "pages": [],
        "shortcut_groups": {},
        "page_images": {},
    },
    {
        # Coming soon: page, manual and playable web demo up (Mark, 12 Nov: "push the Responsive FX page and demo to the
        # website"); on launch day set "status": "live" and "store". Replaces the Hit Feedback and Footstep kits.
        "slug": "responsive-fx",
        "lineup": True,
        "name": "Responsive FX",
        "short": "Responsive FX",
        "the": "",
        "accent": "c-rfx",
        "status": "coming soon",
        "version": "1.0.0",
        "store": "",
        "summary": "Game feel for every hit, step and impact: sound, effects, marks, screen feedback and noise your AI "
                   "hears, tuned in one window and adjustable by your players.",
        "requirements": ["Unity 6000.0+", "Built-in, URP & HDRP", "No dependencies", "Full C# source"],
        "menu": "Tools > Responsive FX",
        "support_info": "In **Tools > Responsive FX > Help and Support**, click **Copy system info**",
        "quick_start": [
            "Import the package. Responsive FX lands in <code>Assets/RareGeometry/ResponsiveFX/</code>.",
            "Open <strong>Tools &gt; Responsive FX &gt; Demos &gt; Response Playground</strong> and press Play. Walk, "
            "strike (click), shoot (<kbd>F</kbd>) and open the player options (<kbd>O</kbd>).",
            "Run the <strong>Setup Wizards</strong> (hits and steps) on your own character. Your prefab gets a variant; "
            "the original stays as it is.",
            "Open <strong>Tools &gt; Responsive FX &gt; Impact Lab</strong>, click a square, press Listen and tune it.",
        ],
        "pages": [
            ("Start here", "QuickStart.md", "getting-started.html", "Quick start"),
            ("Start here", "ImpactLab.md", "impact-lab.html", "Impact Lab"),
            ("The system", "Surfaces.md", "surfaces.html", "Surfaces and responses"),
            ("The system", "Contacts.md", "contacts.html", "Contacts"),
            ("The system", "NoiseAndHearing.md", "noise-and-hearing.html", "Noise and hearing"),
            ("The system", "PlayerOptions.md", "player-options.html", "Player options and screens"),
            ("The system", "ResponseGraph.md", "response-graph.html", "Response Graph"),
            ("The system", "Integrations.md", "integrations.html", "Integrations"),
            ("Hit feedback", "Hits/Index.md", "hits.html", "Overview"),
            ("Hit feedback", "Hits/QuickStart.md", "hits-quick-start.html", "Quick start"),
            ("Hit feedback", "Hits/SetupWizard.md", "hits-setup-wizard.html", "Setup Wizard"),
            ("Hit feedback", "Hits/HitFeedback.md", "hit-feedback.html", "Hit Feedback"),
            ("Hit feedback", "Hits/Profiles.md", "hits-profiles.html", "Profiles, presets and Juice"),
            ("Hit feedback", "Hits/HitRecipeStudio.md", "hit-recipe-studio.html", "Hit Recipe Studio"),
            ("Hit feedback", "Hits/DamageNumbers.md", "damage-numbers.html", "Damage numbers"),
            ("Hit feedback", "Hits/Flash.md", "hit-flash.html", "Hit flash"),
            ("Hit feedback", "Hits/Motion.md", "hits-motion.html", "Hitstop, shake, knockback, squash"),
            ("Hit feedback", "Hits/HealthBars.md", "health-bars.html", "Health and health bars"),
            ("Hit feedback", "Hits/PlayerFeedback.md", "player-feedback.html", "Player feedback"),
            ("Hit feedback", "Hits/SoundParticlesKill.md", "sound-particles-kill.html", "Sound, particles, kill moment"),
            ("Hit feedback", "Hits/Accessibility.md", "accessibility.html", "Accessibility"),
            ("Hit feedback", "Hits/TwoD.md", "hits-2d.html", "2D games"),
            ("Hit feedback", "Hits/MakeItYours.md", "hits-make-it-yours.html", "Make it yours"),
            ("Hit feedback", "Hits/Integration.md", "hits-integration.html", "Hook it into your game"),
            ("Hit feedback", "Hits/Extending.md", "hits-extending.html", "Code, events and your own UI"),
            ("Hit feedback", "Hits/Debugger.md", "why-no-feedback.html", "Why No Feedback?"),
            ("Hit feedback", "Hits/Samples.md", "hits-samples.html", "Demo scenes"),
            ("Hit feedback", "Hits/Troubleshooting.md", "troubleshooting.html", "Troubleshooting and FAQ"),
            ("Footsteps", "Steps/Index.md", "steps.html", "Overview"),
            ("Footsteps", "Steps/QuickStart.md", "steps-quick-start.html", "Quick start"),
            ("Footsteps", "Steps/SetupWizard.md", "steps-setup-wizard.html", "Setup Wizard"),
            ("Footsteps", "Steps/Characters.md", "steps-characters.html", "Surface Footsteps"),
            ("Footsteps", "Steps/Triggers.md", "steps-triggers.html", "When steps happen"),
            ("Footsteps", "Steps/Surfaces.md", "steps-surfaces.html", "The Surface Library"),
            ("Footsteps", "Steps/Zones.md", "surface-zones.html", "Surface Zones"),
            ("Footsteps", "Steps/EffectsAndFootprints.md", "effects-and-footprints.html", "Effects and footprints"),
            ("Footsteps", "Steps/AIHearing.md", "ai-hearing.html", "AI hearing (stealth)"),
            ("Footsteps", "Steps/TwoD.md", "steps-2d.html", "2D games"),
            ("Footsteps", "Steps/MakeItYours.md", "steps-make-it-yours.html", "Make it yours"),
            ("Footsteps", "Steps/YourGame.md", "your-game.html", "Your controller and game"),
            ("Footsteps", "Steps/Extending.md", "steps-extending.html", "Extending with code"),
            ("Footsteps", "Steps/Debugger.md", "why-no-footstep.html", "Why No Footstep?"),
            ("Footsteps", "Steps/Samples.md", "steps-samples.html", "Demo scenes"),
            ("Footsteps", "Steps/Troubleshooting.md", "steps-troubleshooting.html", "Troubleshooting"),
            ("Reference", "Hits/Upgrading.md", "upgrading.html", "Upgrading"),
            ("Reference", "Steps/Support.md", "help-in-unity.html", "Help inside Unity"),
        ],
        "shortcut_groups": {},
        "page_images": {},
    },
]

# Kits without docs yet, for the docs hub and "More from Rare Geometry": (name, accent, status, one line)
COMING = []


# ---- The lineup (Nov 2026): five products replace the ten kits. A product in the lineup has "lineup": True. An old
# kit has "retired_to": the slug of the product it became; once that product's page is on the site, the old kit's
# pages are written as redirects to it (the files stay, so links out in the world keep working). ----

def retired(p):
    """True when an old kit's replacement is on the site, so the kit is hidden and its pages redirect."""
    return bool(p.get("retired_to")) and (SITE / p["retired_to"] / "index.html").exists()


def current_products():
    return [p for p in PRODUCTS if not retired(p)]


def redirect_stub(root, target, label):
    url = f"{root}{target}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moved | Rare Geometry</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITE_URL}/{target.replace('index.html', '')}">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="stylesheet" href="{root}styles.css">
</head>
<body>
<main id="main"><section class="section"><div class="wrap">
<h1>This page has moved</h1>
<p>It is now part of {html.escape(label)}. <a href="{url}">Continue to {html.escape(label)}</a>.</p>
</div></section></main>
<script>location.replace({json.dumps(url)});</script>
</body>
</html>
"""


def write_redirects():
    """Every page of a retired kit becomes a redirect: its product page to the new product, its docs to the new docs."""
    names = {p["slug"]: p["name"] for p in PRODUCTS}
    for p in PRODUCTS:
        if not retired(p):
            continue
        new = p["retired_to"]
        label = names.get(new, new.replace("-", " ").title())
        has_docs = (SITE / new / "docs" / "index.html").exists()
        folder = SITE / p["slug"]
        pages = [folder / "index.html"] + (sorted(folder.rglob("*.html")) if folder.exists() and not p.get("keep_docs") else [])
        for path in dict.fromkeys(pages):
            rel = path.relative_to(SITE)
            root = "../" * (len(rel.parts) - 1)
            in_docs = len(rel.parts) > 2 and rel.parts[1] == "docs"
            target = f"{new}/docs/index.html" if in_docs and has_docs else f"{new}/index.html"
            write(rel.as_posix(), redirect_stub(root, target, label))


# ---- The look of each product on the site (home page cards and "closer look" rows, the icon beside a product
# page's title, "More from Rare Geometry"). Words only: a product's facts stay in PRODUCTS. Pictures are in
# assets/img/<slug>/icon.png (its store icon) and assets/img/home/ (cut by tools/site_images.py). ----

LINEUP_ART = {
    "shipready": {
        "line": "Menus, settings, saves and playtest tools",
        "tagline": "From first launch to final save.",
        "ticks": ["Title screen, main menu, pause, settings and credits, already connected",
                  "92 ready-made settings with rebinding and accessibility presets",
                  "Saves that survive crashes, with slots, autosaves and backups"],
        "main_alt": "A Load Game menu made with Shipready: three save slots, each with a picture, place and play time",
        "inset_alt": "Shipready's settings menu on the Audio tab",
    },
    "bearing": {
        "line": "Minimap, compass and waypoints",
        "tagline": "Lead players to what matters.",
        "ticks": ["A full map built from your level, with floors for buildings",
                  "Compass, minimap and world markers that stay calm by default",
                  "Routes that follow your roads, fast travel and fog of war"],
        "main_alt": "Bearing's full-screen map of an island with places, a tracked objective and region progress",
        "inset_alt": "The Chart Table window listing every place in the level",
    },
    "snapbuild": {
        "line": "World building from your own prefabs",
        "tagline": "Build worlds from the prefabs you own.",
        "ticks": ["Stamp and paint your prefabs on a grid that snaps",
                  "Roads that join themselves and streets dressed in one click",
                  "A ghost shows everything first, and your pack's files are never changed"],
        "main_alt": "A house shown as a see-through ghost about to be stamped into a street of a town built with Snapbuild",
        "inset_alt": "Snapbuild's Level Builder window on the Stamp tool with a palette of buildings",
    },
    "interactra": {
        "line": "Interaction and runtime building",
        "tagline": "Build worlds you can use.",
        "ticks": ["Doors, drawers, switches, keys, keypads and elevators from your own prefabs",
                  "Runtime building with ghosts, blueprints and wiring",
                  "One save for everything players build and change"],
        "main_alt": "A wall's ghost snapping into place beside a house, with the build bar along the bottom",
        "inset_alt": "A lever wired to a powered door",
    },
    "responsive-fx": {
        "line": "Hit feedback, footsteps and surface impacts",
        "tagline": "Feel every hit. Hear every step.",
        "ticks": ["Damage numbers, hitstop, shake and health bars for every hit",
                  "Footsteps, footprints and bullet marks that match the surface",
                  "Noise your AI can hear, all tuned in one window"],
        "main_alt": "A knight striking a pane of glass, which cracks and sprays shards",
        "inset_alt": "Impact Lab: a grid of surfaces against contacts",
    },
}


def lineup_order():
    """Home page order: the lineup first, products on the Asset Store before the ones coming soon."""
    return sorted(current_products(), key=lambda q: (not q.get("lineup"), q["status"] != "live"))


def status_pill(p):
    if p["status"] == "live":
        return '<span class="pill pill-live">On the Asset Store</span>'
    return f'<span class="pill pill-dev">{html.escape(p["status"].capitalize())}</span>'


def icon_img(root, slug, size):
    """The product's own icon, or nothing when it has none on the site yet."""
    if not (SITE / "assets" / "img" / slug / "icon.png").exists():
        return ""
    return (f'<img class="picon" src="{root}assets/img/{slug}/icon.png" width="{size}" height="{size}" alt="" '
            f'loading="lazy" decoding="async">')


def home_img(root, slug, part, alt, cls, lazy=True):
    path = SITE / "assets" / "img" / "home" / f"{slug}-{part}.jpg"
    if not path.exists():
        return ""
    width, height = jpeg_size(path)
    lazy_attr = ' loading="lazy" decoding="async"' if lazy else ""
    return (f'<img class="{cls}" src="{root}assets/img/home/{slug}-{part}.jpg" width="{width}" height="{height}" '
            f'alt="{html.escape(alt)}"{lazy_attr}>')


def jpeg_size(path):
    """Width and height of a JPEG, read from its header (so the build needs no image library)."""
    data = path.read_bytes()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return 16, 10


def product_card(root, p, heading="h3", lazy=True):
    """One picture card: a real capture, the product's icon, its name and one line. The whole card is the link."""
    slug = p["slug"]
    art = LINEUP_ART.get(slug, {})
    shot = home_img(root, slug, "card", "", "pcard-img", lazy)
    return f"""<article class="pcard p-{slug}">
        <div class="pcard-shot">{shot}</div>
        <div class="pcard-body">
          {icon_img(root, slug, 52)}
          <{heading}><a href="{root}{slug}/index.html">{html.escape(p['name'])}</a></{heading}>
          <p>{html.escape(art.get('line') or p['summary'])}</p>
          {status_pill(p)}
        </div>
      </article>"""


def product_cards(root):
    """The home page's product cards, five across: the lineup first, then anything else still current."""
    return "\n      ".join(product_card(root, p, lazy=False) for p in lineup_order())


def product_showcase(root):
    """The home page's "closer look": one wide row per product, pictures on alternating sides."""
    rows = []
    for p in lineup_order():
        slug = p["slug"]
        art = LINEUP_ART.get(slug, {})
        buttons = [f'<a class="btn" href="{root}{slug}/index.html">Explore {html.escape(p["short"])}</a>']
        if (SITE / slug / "demo" / "index.html").exists():
            buttons.append(f'<a class="btn btn-ghost" href="{root}{slug}/demo/index.html">Play the demo</a>')
        links = []
        if p["status"] == "live" and p.get("store"):
            links.append(f'<a href="{p["store"]}" rel="noopener">Asset Store</a>')
        if (SITE / slug / "docs" / "index.html").exists():
            links.append(f'<a href="{root}{slug}/docs/index.html">Docs</a>')
        links.append(f'<a href="{root}{slug}/index.html#support">Support</a>')
        ticks = "".join(f"<li>{html.escape(tick)}</li>" for tick in art.get("ticks", []))
        tagline = f'<p class="show-tagline">{html.escape(art["tagline"])}</p>' if art.get("tagline") else ""
        rows.append(f"""<article class="show p-{slug}" id="{slug}">
        <a class="show-art" href="{root}{slug}/index.html" tabindex="-1" aria-hidden="true">
          {home_img(root, slug, "inset", "", "show-inset")}
          {home_img(root, slug, "main", "", "show-main")}
        </a>
        <div class="show-copy">
          <div class="show-title">
            {icon_img(root, slug, 64)}
            <div><h3>{html.escape(p['name'])}</h3>{status_pill(p)}</div>
          </div>
          {tagline}
          <p>{html.escape(p['summary'])}</p>
          <ul class="ticks">{ticks}</ul>
          <div class="btn-row">{''.join(buttons)}</div>
          <p class="card-links">{''.join(links)}</p>
        </div>
      </article>""")
    return "\n      ".join(rows)


def footer_products(root):
    return "\n          ".join(f'<li><a href="{root}{p["slug"]}/index.html">{html.escape(p["short"])}</a></li>'
                              for p in current_products())

NAV = [
    ("products", "Products", "index.html#products"),
    ("docs", "Docs", "docs/index.html"),
    ("support", "Support", "support/index.html"),
]


def header(root, active):
    items = []
    for key, label, href in NAV:
        current = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{root}{href}"{current}>{label}</a></li>')
    items.append(f'<li class="nav-store"><a href="{PUBLISHER_URL}" rel="noopener">Asset Store</a></li>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{root}index.html" aria-label="Rare Geometry home">
      <img src="{root}assets/logo.svg" alt="" width="34" height="34">
      <span>Rare Geometry</span>
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
        <a class="brand" href="{root}index.html"><img src="{root}assets/logo.svg" alt="" width="34" height="34"><span>Rare Geometry</span></a>
        <p>Core systems, carefully built.</p>
      </div>
      <div>
        <h4>Products</h4>
        <ul>
          {footer_products(root)}
          <li><a href="{PUBLISHER_URL}" rel="noopener">Publisher page</a></li>
        </ul>
      </div>
      <div>
        <h4>Learn</h4>
        <ul>
          <li><a href="{root}docs/index.html">Documentation</a></li>
          <li><a href="{root}support/index.html">Troubleshooting and help</a></li>
        </ul>
      </div>
      <div>
        <h4>Help</h4>
        <ul>
          <li><a href="{root}support/index.html">Support</a></li>
          <li><a href="mailto:{EMAIL}">Email</a></li>
          <li>{soon_or_link(DISCORD_URL, "Discord")}</li>
          <li>{soon_or_link(ISSUES_URL, "Bug tracker")}</li>
          <li><a href="{GITHUB_URL}" rel="noopener">GitHub</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <p>&copy; {YEAR} Rare Geometry. Unity is a trademark of Unity Technologies.</p>
      <p>No trackers, no cookies, no analytics.</p>
    </div>
  </div>
</footer>"""


def og_image(path):
    """The link-preview picture: a kit's own social art on its pages, the Rare Geometry card everywhere else."""
    if path.startswith("prefab-builder/"):
        return "prefab-builder/social.jpg"
    if path.startswith("shipready/"):
        return "shipready/social.jpg"
    if path.startswith("snapbuild/"):
        return "snapbuild/social.jpg"
    if path.startswith("bearing/"):
        return "bearing/social.jpg"
    if path.startswith("interactra/"):
        return "interactra/social.jpg"
    if path.startswith("responsive-fx/"):
        return "responsive-fx/social.jpg"
    return "og-image.jpg"


def body_class(path):
    """A product's pages carry its class (p-<slug>), which sets its accent colour in styles.css."""
    slug = path.split("/")[0]
    return f' class="p-{slug}"' if "/" in path and slug in LINEUP_ART else ""


def page(root, active, title, description, body, path, scripts=""):
    full_title = "Rare Geometry" if title == "Rare Geometry" else f"{title} | Rare Geometry"
    canonical = f"{SITE_URL}/{path}".replace("/index.html", "/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0D1014">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Rare Geometry">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/img/{og_image(path)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="{root}assets/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/favicon-180.png">
<link rel="stylesheet" href="{root}styles.css">
</head>
<body{body_class(path)}>
{header(root, active)}
<main id="main">
{body}
</main>
{footer(root)}
{scripts}
</body>
</html>
"""


def fill(text, root, slug=""):
    """Replaces {{name}} placeholders in a page fragment. slug: the kit the page is about, left out of {{more_from}}."""
    values = {
        "more_from": more_from(root, slug),
        "root": root, "store": STORE_URL, "publisher": PUBLISHER_URL, "email": EMAIL,
        "version": PREFAB_VERSION, "external": ICON_EXTERNAL,
        "discord_tile": discord_tile(), "issues_tile": issues_tile(root), "discord_button": discord_button(),
        "support": support_section(root, slug),
        "product_cards": product_cards(root),
        "product_showcase": product_showcase(root),
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)


def more_from(root, slug):
    """The other products, as picture cards linking to their pages (Shipping Standard: cross-link every product)."""
    cards, named = [], set()
    for p in lineup_order():
        named.add(p["name"])
        if p["slug"] == slug:
            continue
        cards.append(product_card(root, p))
    for name, accent, status, line in COMING:
        if name in named:
            continue
        cards.append(f'<article class="product product-planned {accent}"><div class="product-top">'
                     f'<span class="pill{" pill-dev" if status == "In development" else ""}">{status}</span></div>'
                     f'<h3>{html.escape(name)}</h3><p>{html.escape(line)}</p></article>')
    return f"""<section class="section section-band" aria-labelledby="more-title">
  <div class="wrap">
    <div class="section-head">
      <p class="label">More from Rare Geometry</p>
      <h2 id="more-title">Other tools, built to the same standard</h2>
    </div>
    <div class="lineup lineup-{len(cards)}">{"".join(cards)}</div>
  </div>
</section>"""


def support_section(root, slug):
    """A Support block for a kit's own page: its docs help page, Discord, the bug tracker and email, in one row."""
    product = next((p for p in PRODUCTS if p["slug"] == slug), None)
    if not product:
        return ""
    name = product["name"]
    subject = name.replace("All In One ", "").replace(" ", "%20")
    # Kits still in development may already have their manual built (linked from their page): use its Support page
    has_docs = (SITE / slug / "docs" / "support.html").exists()
    docs = (f'<a class="tile" href="{root}{slug}/docs/support.html"><span class="label">Docs</span>'
            '<h3>Help and troubleshooting</h3><p>Common problems and their fixes, and what to include when you ask.</p></a>'
            if has_docs else
            f'<a class="tile" href="{root}support/index.html"><span class="label">Help</span>'
            '<h3>Support page</h3><p>Every way to get help with Rare Geometry tools, in one place.</p></a>')
    return f"""<section class="section" id="support" aria-labelledby="support-title">
  <div class="wrap">
    <div class="section-head">
      <p class="label">Support</p>
      <h2 id="support-title">Help with {product.get("the", "the ")}{html.escape(product["short"])}</h2>
      <p>Stuck, found a bug or have an idea? Pick whichever is easiest. Every message gets an answer.</p>
    </div>
    <div class="tiles">
      {docs}
      {discord_tile()}
      {issues_tile(root)}
      <a class="tile" href="mailto:{EMAIL}?subject={subject}%20support"><span class="label">Email</span>
        <h3>Email the developer</h3><p>{EMAIL}</p></a>
    </div>
  </div>
</section>"""


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


# ---- Pictures in the manuals. The site adds these to a product's docs pages; the words still come from the
# Documentation folder that ships in the package. slug -> page.html -> [(picture under assets/img/, caption, where)].
# "where" is the id of the section heading the picture goes under; leave it out for under the page's opening
# paragraph. Every picture is a real capture or a store slide made from real captures. A product's own
# "page_images" in PRODUCTS (one picture per page) still works and is added to these. ----

DOC_IMAGES = {
    "bearing": {
        "getting-started.html": [
            ("bearing/docs/14-setup-wizard.jpg", "The Setup Wizard: add the HUD, mark your objects, pick the objective.", "1-add-the-hud"),
            ("bearing/docs/01-hero.jpg", "After the wizard: the compass, the objective tracker and the minimap, with the objective marked in the world.", "4-press-play"),
        ],
        "samples.html": [("bearing/docs/01-demo-in-editor.jpg", "The demo island, open in the editor.")],
        "chart-table.html": [("bearing/chart-table.jpg", "The Chart Table lists every place in the level; the small picture is the same level in the game.")],
        "hud.html": [
            ("bearing/docs/01-hero.jpg", "The HUD: compass along the top, objective tracker top right, minimap bottom left and a marker over the objective."),
            ("bearing/docs/18-skins-fantasy.jpg", "The same HUD with the Fantasy frames.", "look"),
        ],
        "make-it-yours.html": [("bearing/docs/02-four-looks.jpg", "The four ready-made looks on the same scene.")],
        "visibility.html": [("bearing/docs/20-calm.jpg", "Calm by default: only the objective and what is close by show on screen.")],
        "map.html": [
            ("bearing/docs/15-map-from-world.jpg", "A level seen from above, and the Clean map made from it.", "making-a-clean-map"),
            ("bearing/docs/03-full-map.jpg", "The full-screen map: places, the tracked objective, the map key and the controls along the bottom.", "the-full-screen-map"),
            ("bearing/docs/07-floors.jpg", "A building's ground floor on the map.", "floors"),
        ],
        "discovery.html": [
            ("bearing/docs/06-lookout-reveal.jpg", "Fog of war: a lookout reveals the land around it.", "fog-of-war"),
            ("bearing/docs/05-discovery.jpg", "Discovering a place: the banner, and its icon turning from a question mark.", "regions"),
        ],
        "routes.html": [("bearing/docs/08-route.jpg", "A route to the objective that follows the road and the bridge.", "routes")],
        "player-map.html": [
            ("bearing/docs/map-pin-editor-explorer.jpg", "A player placing a pin: name, icon and colour.", "pins-and-stamps"),
            ("bearing/docs/10-after-fast-travel.jpg", "Arriving at a camp after fast travel.", "fast-travel"),
        ],
        "scan-and-entities.html": [
            ("bearing/docs/09-world-scan.jpg", "A world scan: the ring sweeps out and marks what it passes.", "world-scan"),
            ("bearing/docs/10-entities.jpg", "Moving entities: two boats tracked in the world and on the minimap.", "moving-entities"),
        ],
        "sharing.html": [("bearing/docs/11-sharing.jpg", "A marker shared by another player, in the world and on the compass.")],
        "fit-your-game.html": [("bearing/docs/12-player-options.jpg", "The player options screen: players choose what the map and HUD show, within your limits.")],
        "2d.html": [("bearing/docs/17-top-down.jpg", "Bearing in a top-down game.")],
        "trails.html": [("bearing/docs/04-chain-wired.jpg", "A chain of objectives set up in the Chart Table.")],
    },
    "interactra": {
        "getting-started.html": [("interactra/docs/01-interactive-then-build.jpg", "The demo house: a lever wired to a powered door and a lamp.")],
        "setup-wizard.html": [("interactra/docs/02-your-prefab.jpg", "The Setup Wizard: pick your model, pick what it does, press Create.")],
        "ways-to-interact.html": [("interactra/docs/06-several-actions.jpg", "One door, two actions: tap to open, hold to lock, each with its own prompt line.")],
        "components.html": [("interactra/docs/10-doors-locks-keys.jpg", "A locked door, a physics door, keys and a keypad.")],
        "hands-on-objects.html": [("interactra/11-keypad.jpg", "A keypad, used with the mouse or a gamepad.")],
        "more-objects.html": [("interactra/docs/11-machines.jpg", "An elevator, its call button, a valve and a breakable crate.")],
        "power-and-puzzles.html": [("interactra/docs/07-power.jpg", "Power: the lever feeds the door and the lamp through a wire.")],
        "build-feel-and-wiring.html": [
            ("interactra/docs/05-build-animations.jpg", "The four ways a piece can arrive: grow, rise, drop or assemble.", "build-animations"),
            ("interactra/docs/08-wires.jpg", "The four wire looks: tidy, loose, straight or hidden.", "wire-looks"),
        ],
        "prompts.html": [("interactra/08-locked.jpg", "A prompt that says why: the door is locked and needs its key.")],
        "customizing.html": [("interactra/docs/13-four-looks.jpg", "The four ready-made looks: Clean, Industrial, Fantasy and Sci-Fi.")],
        "accessibility.html": [("interactra/docs/14-player-options.jpg", "The player options screen: prompt size, press instead of hold, captions and reduced motion.")],
        "saving-and-integrations.html": [("interactra/docs/15-everything-saves.jpg", "Before saving, cleared, and after loading: built pieces, wires and every object's state come back.")],
        "tools.html": [("interactra/docs/16-workbench.jpg", "The Workbench: its Objects, Pieces and Test pages.")],
        "samples.html": [("interactra/docs/12-build-menu.jpg", "The demo's build menu, with its categories and costs.")],
        "troubleshooting.html": [("interactra/docs/09-placement-reasons.jpg", "A refused spot says why, in the game and in the editor.")],
    },
    "responsive-fx": {
        "getting-started.html": [("responsive-fx/docs/01-one-volley-three-answers.jpg", "One volley, three answers: wood splinters, armour sparks, glass shatters.")],
        "impact-lab.html": [("responsive-fx/docs/04-meet-impact-lab.jpg", "Impact Lab: every surface against every kind of contact. Pick a square, press Listen, adjust it.")],
        "surfaces.html": [("responsive-fx/docs/02-same-blade.jpg", "The same blade on two surfaces: the surface decides the response.")],
        "contacts.html": [("responsive-fx/docs/15-every-bump.jpg", "Physics impacts: a tumbling crate gets the sound and effect of the surface it lands on.")],
        "noise-and-hearing.html": [
            ("responsive-fx/docs/07-your-steps-they-hear.jpg", "A guard hears the player's steps; the trace shows what was heard.", "let-ai-hear"),
            ("responsive-fx/docs/14-hear-it-find-it.jpg", "Showing the player where a sound came from, even off screen.", "show-the-player"),
        ],
        "player-options.html": [("responsive-fx/docs/09-comfort-on-their-terms.jpg", "The feedback options screen your players get.")],
        "response-graph.html": [("responsive-fx/docs/16-response-graph.jpg", "The Response Graph: when it happens, check the rule, fire the response.")],
        "integrations.html": [("responsive-fx/docs/20-ready-for-your-game.jpg", "Bridges, render pipelines and Unity versions.")],
        "hits.html": [("responsive-fx/docs/03-glass-breaks.jpg", "Hit by hit, the glass cracks, clouds over and shatters.")],
        "hits-samples.html": [("responsive-fx/volley.jpg", "The Response Playground demo.")],
        "hits-profiles.html": [("responsive-fx/docs/10-four-looks-one-system.jpg", "Four ready-made looks for the same hit.")],
        "hit-recipe-studio.html": [("responsive-fx/docs/05-build-the-feel.jpg", "Hit Recipe Studio beside the recipe library in Impact Lab.")],
        "health-bars.html": [("responsive-fx/docs/19-first-hit-to-final-blow.jpg", "A boss bar across the top, and the kill moment.")],
        "player-feedback.html": [("responsive-fx/docs/13-feel-the-hit.jpg", "Damage direction, screen-edge feedback and the low-health warning.")],
        "accessibility.html": [("responsive-fx/docs/08-sound-you-can-see.jpg", "Sound captions make important sounds visible.")],
        "hits-2d.html": [("responsive-fx/docs/12-2d-hits-full-force.jpg", "Damage numbers, flashes and impacts in a 2D game, in the four looks.")],
        "why-no-feedback.html": [("responsive-fx/docs/17-set-it-up-find-the-fix.jpg", "The Setup Wizard, and the Why No Feedback? and Why No Footstep? windows.")],
        "steps.html": [("responsive-fx/docs/06-every-step-leaves-a-mark.jpg", "Footprints follow the character across the snow.")],
        "effects-and-footprints.html": [("responsive-fx/snow.jpg", "A trail of footprints in fresh snow.")],
        "ai-hearing.html": [("responsive-fx/heard.jpg", "A guard turns towards a sound; the meter shows how loud the player is.")],
        "surface-zones.html": [("responsive-fx/docs/18-the-world-changes.jpg", "Weather, trails and rooms change what the world hears and remembers.")],
        "steps-2d.html": [("responsive-fx/docs/11-2d-steps-explained.jpg", "A 2D walker, with the panel that says which surface was found and which response played.")],
        "steps-samples.html": [("responsive-fx/glass.jpg", "The demo scene: surfaces to walk on and things to hit.")],
    },
    "snapbuild": {
        "getting-started.html": [("snapbuild/01-build-worlds.jpg", "A whole town made with Snapbuild from one modular pack.")],
        "world-builder-window.html": [("snapbuild/20-level-builder.jpg", "The Level Builder: every tool in one window, in the order you build.")],
        "adding-packs.html": [
            ("snapbuild/03-your-pack.jpg", "Turn a pack into a kit: choose it, check the review, build."),
            ("snapbuild/howto-pack-review.jpg", "The review screen: what each piece was recognised as.", "3-the-review-screen"),
        ],
        "place-tab.html": [
            ("snapbuild/02-prefabs.jpg", "Stamp: pick a prefab, click, and it snaps to the grid and its neighbours.", "stamp"),
            ("snapbuild/06-brush.jpg", "Brush: paint pieces across the ground.", "brush"),
            ("snapbuild/07-fill.jpg", "Fill: cover an area in one go.", "fill"),
            ("snapbuild/04-roads.jpg", "Roads: drag along the grid and the straights, corners and junctions join themselves.", "roads"),
        ],
        "build-catalog.html": [("snapbuild/21-build-menus.jpg", "Build menus made from your pack.")],
        "rooms.html": [("snapbuild/15-rooms.jpg", "Drag a room and get a building: walls, corners, floor, roof and door.")],
        "dress-tab.html": [("snapbuild/05-dress-the-street.jpg", "Dress a street in one click: lights, bins and signs along the road.")],
        "move-tab.html": [("snapbuild/13-line-it-up.jpg", "Line pieces up and space them evenly.")],
        "physics-tab.html": [("snapbuild/09-physics.jpg", "Physics: drop pieces and let them settle.")],
        "check-tab.html": [("snapbuild/18-find-problems.jpg", "Check finds problems in the scene and points at each one.")],
        "make-playable.html": [("snapbuild/19-ready-to-play.jpg", "Make Playable: ids, map places, surfaces and doors marked for your game.")],
        "rules-and-data.html": [("snapbuild/12-vary.jpg", "Variation rules keep repeated pieces from looking the same.")],
    },
}


def doc_images_for(product, out):
    """The pictures for one docs page: the product's own page_images entry first, then DOC_IMAGES."""
    own = product.get("page_images", {}).get(out)
    return ([tuple(own)] if own else []) + DOC_IMAGES.get(product["slug"], {}).get(out, [])


def doc_figure(img, caption, lazy=True):
    """A picture in a manual page: opens full size when clicked. Marked so the build can replace it later. The one
    at the top of a page is on screen at once, so it is not loaded lazily."""
    path = SITE / "assets" / "img" / img
    width, height = jpeg_size(path) if path.exists() else (1920, 1080)
    cap = html.escape(caption)
    return (f'<figure class="doc-figure" data-site-figure><a href="../../assets/img/{img}">'
            f'<img src="../../assets/img/{img}" alt="{cap}" width="{width}" height="{height}"{' loading="lazy" decoding="async"' if lazy else ""}>'
            f'</a><figcaption>{cap}</figcaption></figure>')


SITE_FIGURE = re.compile(r'\n?<figure class="doc-figure" data-site-figure>.*?</figure>', re.S)


def add_doc_figures(body_html, images):
    """Puts each picture under its section heading, or under the page's opening paragraph when it names none (or
    when the page no longer has that section). Safe to run again: it takes its own earlier pictures out first."""
    body_html = SITE_FIGURE.sub("", body_html)
    top = []
    for image in images:
        img, caption, where = (tuple(image) + (None,))[:3]
        if not (SITE / "assets" / "img" / img).exists():
            print(f"WARNING: docs picture {img} is not in assets/img; left out.")
            continue
        heading = re.search(rf'<h2 id="{re.escape(where)}"[^>]*>.*?</h2>', body_html, re.S) if where else None
        if heading:
            body_html = body_html[:heading.end()] + "\n" + doc_figure(img, caption) + body_html[heading.end():]
        else:
            top.append(doc_figure(img, caption, lazy=False))
    if top:
        figs = "".join(top)
        if re.search(r"</h1>\s*<p>.*?</p>", body_html, re.S):
            body_html = re.sub(r"(</h1>\s*<p>.*?</p>)", lambda m_: m_.group(1) + figs, body_html, count=1, flags=re.S)
        else:
            body_html = re.sub(r"(</h1>)", lambda m_: m_.group(1) + figs, body_html, count=1)
    return body_html


def apply_doc_images():
    """Adds the pictures to docs pages already on the site, so a product's manual need not be rebuilt for them."""
    for p in current_products():
        for out in sorted(set(DOC_IMAGES.get(p["slug"], {}))):
            path = SITE / p["slug"] / "docs" / out
            if not path.exists():
                print(f"WARNING: {p['slug']}/docs/{out} has pictures listed but is not on the site.")
                continue
            text = path.read_text(encoding="utf-8")
            start = text.find('<article class="prose" id="doc">')
            end = text.find('<div class="doc-pager">', start)
            if start < 0 or end < 0:
                continue
            new = text[:start] + add_doc_figures(text[start:end], doc_images_for(p, out)) + text[end:]
            if new != text:
                path.write_text(new, encoding="utf-8")
                print("pictures", f"{p['slug']}/docs/{out}")


# ---- Hand-written pages (tools/pages/*.html) ----

HAND_PAGES = [
    # fragment, output, root, active nav, title, description
    ("home.html", "index.html", "", "",
     "Rare Geometry",
     "Unity tools by Rare Geometry: core systems for finished games, each one complete on its own and built to work "
     "together. Documentation, web demos and support."),
    ("prefab-builder.html", "prefab-builder/index.html", "../", "prefab",
     "All In One Prefab Builder Kit",
     "Turn any pack of prefabs into a world-building kit: snap, draw roads, scatter, fence, dress streets, settle with "
     "physics and check your scene, all from one Unity window."),
    ("save-kit.html", "save-kit/index.html", "../", "save",
     "All In One Save Kit",
     "Save and restore player progress, world objects and settings in Unity: no code needed, slots, autosaves, a "
     "finished save menu, backups and automatic recovery from damaged saves. Coming soon to the Asset Store."),
    ("interaction-kit.html", "interaction-kit/index.html", "../", "interact",
     "All In One Interaction Kit",
     "Turn your own Unity prefabs into doors, drawers, switches, pickups, keypads and puzzles: a Setup Wizard, prompts "
     "for every controller, a debugger that says why something can't be used, and optional multiplayer. Coming soon to "
     "the Unity Asset Store."),
    ("runtime-building-kit.html", "runtime-building-kit/index.html", "../", "runtime",
     "All In One Runtime Building Kit",
     "Let players build bases and place furniture at runtime in Unity: your own models become build pieces in about ten "
     "minutes without code, snap through sockets, and every refused spot says why. Coming soon to the Asset Store."),
    ("settings-menu-kit.html", "settings-menu-kit/index.html", "../", "settings",
     "All In One Game Settings & Menu Kit",
     "A finished game front end for Unity: title screen, main menu, settings, pause and loading screens, key rebinding, "
     "accessibility, subtitles and three themes, without code. Coming soon to the Asset Store."),
    ("bug-report-kit.html", "bug-report-kit/index.html", "../", "bugreport",
     "All In One Bug Report Kit",
     "In-game bug reports for Unity: testers press one key and you get one file with their words, a marked-up "
     "screenshot, a replay, logs with stack traces and system info, plus a debug console and a Report Inbox that "
     "clicks to the broken line. Coming soon to the Asset Store."),
    ("footstep-kit.html", "footstep-kit/index.html", "../", "footstep",
     "All In One Surface Footstep Kit",
     "Footsteps for Unity that sound like what your characters walk on: any controller, 3D and 2D, terrain layers, "
     "zones, effects, footprints, AI hearing and a Why No Footstep? debugger. Coming soon to the Asset Store."),
    ("hit-feedback-kit.html", "hit-feedback-kit/index.html", "../", "hitfeedback",
     "All In One Hit Feedback Kit",
     "Make every hit land in Unity: damage numbers, hit flash, hitstop, screen shake, knockback, health bars and sound "
     "from one component, with genre presets and a Why No Feedback? debugger. Coming soon to the Asset Store."),
    ("tutorial-kit.html", "tutorial-kit/index.html", "../", "tutorial",
     "All In One Tutorial Kit",
     "In-game tutorials and onboarding for Unity without code: spotlight any button or object, show a tip, and finish "
     "each step when the player really does it. uGUI, UI Toolkit, 2D and 3D. Free. Coming soon to the Asset Store."),
    ("waypoint-minimap-kit.html", "waypoint-minimap-kit/index.html", "../", "waypoint",
     "All In One Waypoint & Minimap Kit",
     "Show players where to go in Unity: objective markers, edge arrows with distance, a compass bar, a minimap and a "
     "full-screen map, with a one-click map maker, fog of war and region discovery, without code. Coming soon to the Asset Store."),
    ("shipready.html", "shipready/index.html", "../", "",
     "Shipready",
     "Menus, settings, saves, tutorials and playtest tools for Unity in one connected package: title screen, 92 player "
     "settings, crash-safe saves, first-time tours and bug reports with steps. Try the web demo. Coming soon to the Asset Store."),
    ("bearing.html", "bearing/index.html", "../", "bearing",
     "Bearing",
     "Compass, minimap, world markers and a full-screen map built from your level for Unity, with routes that follow "
     "your roads, fast travel, fog of war and floors. Play the demo in your browser. Coming soon to the Unity Asset Store."),
    ("snapbuild.html", "snapbuild/index.html", "../", "",
     "Snapbuild: Prefab World Builder",
     "Build whole worlds in Unity from the prefabs you already own: stamp and paint them on a grid that snaps, draw roads "
     "that join themselves, dress streets in one click. Try the demo in your browser."),
    ("interactra.html", "interactra/index.html", "../", "",
     "Interactra",
     "Make anything interactive, then let players build, for Unity: doors, switches, keys and elevators from your own "
     "prefabs, runtime building with ghosts, blueprints and wiring. Play the demo in your browser. Coming soon to the Unity Asset Store."),
    ("responsive-fx.html", "responsive-fx/index.html", "../", "rfx",
     "Responsive FX",
     "Game feel for every hit, step and impact in Unity: damage numbers, hitstop and shake, footsteps and footprints, "
     "bullet marks, physics impacts and AI hearing, tuned in one window. Play the demo in your browser. Coming soon to "
     "the Unity Asset Store."),
    ("support.html", "support/index.html", "../", "support",
     "Support",
     "Get help with Rare Geometry tools: documentation, bug reports, Discord and email."),
    ("404.html", "404.html", "/", "",
     "Page not found",
     "This page doesn't exist."),
]


def title_with_icon(body, root, kit):
    """Puts the product's icon beside the first <h1> of its page (the hero title)."""
    icon = icon_img(root, kit["slug"], 72).replace(' loading="lazy" decoding="async"', "")
    if not icon:
        return body
    return re.sub(r"<h1>(.*?)</h1>", lambda m: f'<div class="product-title">{icon}<h1>{m.group(1)}</h1></div>',
                  body, count=1, flags=re.S)


def build_pages():
    by_slug = {p["slug"]: p for p in PRODUCTS}
    for fragment, out, root, active, title, description in HAND_PAGES:
        kit = by_slug.get(out.split("/")[0]) if "/" in out else None
        if kit and retired(kit):
            continue
        body = fill((PAGES / fragment).read_text(encoding="utf-8"), root, out.split("/")[0] if "/" in out else "")
        if kit and kit["slug"] in LINEUP_ART:
            body = title_with_icon(body, root, kit)
        write(out, page(root, active, title, description, body, out))
    write_redirects()
    apply_doc_images()
    build_docs_hub()
    sync_footers()


def sync_footers():
    """Docs pages are only regenerated with --docs, so give every page already on the site today's footer (the kit list
    in it changes whenever a kit is added)."""
    for path in SITE.rglob("*.html"):
        rel = path.relative_to(SITE)
        if rel.parts[0] in ("tools", "assets", ".git"):
            continue
        text = path.read_text(encoding="utf-8")
        start, end = text.find('<footer class="site-footer">'), text.find("</footer>")
        if start < 0 or end < 0:
            continue
        new = text[:start] + footer("../" * (len(rel.parts) - 1)) + text[end + len("</footer>"):]
        if new != text:
            path.write_text(new, encoding="utf-8")


def write(out, text):
    if "\u2014" in text or "&mdash;" in text:
        print(f"WARNING: {out} has an em dash; Mark's rule is none on the site. Reword it (a colon or a comma).")
    target = SITE / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print("wrote", out)


def build_docs_hub():
    """docs/index.html: every kit's documentation in one place."""
    cards = []
    for p in current_products():
        if p["status"] not in ("live", "coming soon"):
            continue
        if not (SITE / p["slug"] / "docs" / "index.html").exists():
            continue
        d = f"../{p['slug']}/docs/"
        pill = f'<span class="pill pill-live">v{p["version"]}</span>' if p["status"] == "live" else \
            f'<span class="pill pill-dev">v{p["version"]}, coming soon to the Asset Store</span>'
        links = p.get("hub_links") or [
            ("index.html#quick-start", "Quick start", "From import to your first result in minutes"),
            ("shortcuts.html", "Keyboard shortcuts", "Every key and mouse control"),
            ("troubleshooting.html", "Troubleshooting", "Common problems and their fixes"),
            ("changelog.html", "Changelog", "What changed in each version"),
        ]
        # Only pages this kit's manual has (not every kit has a shortcuts page)
        links = [l for l in links if (SITE / p["slug"] / "docs" / l[0].split("#")[0]).exists()]
        link_items = "\n    ".join(f'<li><a href="{d}{href}"><strong>{t}</strong><span>{line}</span></a></li>' for href, t, line in links)
        cards.append(f"""<article class="product product-flag {p['accent']} p-{p['slug']}">
  <div class="flag-copy">
    <div class="product-top">{pill}</div>
    <div class="show-title">{icon_img('../', p['slug'], 56)}<h2>{p['name']}</h2></div>
    <p>{p['summary']}</p>
    <div class="btn-row">
      <a class="btn" href="{d}index.html">Open the documentation</a>
      <a class="btn btn-ghost" href="{d}getting-started.html">Getting started</a>
    </div>
  </div>
  <ul class="doc-links">
    {link_items}
  </ul>
</article>""")
    soon = "".join(
        f'<article class="product product-planned {accent}"><div class="product-top"><h3>{html.escape(name)}</h3>'
        f'<span class="pill{" pill-dev" if status == "In development" else ""}">{status}</span></div>'
        f'<p>Its documentation goes up here the day it launches.</p></article>'
        for name, accent, status, _ in COMING)
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
                                  "Documentation for every Rare Geometry Unity tool.", body, "docs/index.html"))


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
    """What each page covers, from Documentation/Index.md, by linked file: a table row "| [Page](Page.md) | text |",
    or a list item "- [Page](Page.md): text" (its wrapped lines included)."""
    found = {m.group(1): m.group(2).strip()
             for m in re.finditer(r"^\|\s*\[[^\]]+\]\(([^)#]+\.md)\)\s*\|\s*(.+?)\s*\|\s*$", index_md, re.M)}
    for m in re.finditer(r"^[-*]\s+\[[^\]]+\]\(([^)#]+\.md)\):\s*(.+(?:\n[ \t]+\S.*)*)", index_md, re.M):
        text = re.sub(r"\s+", " ", m.group(2)).strip()
        found.setdefault(m.group(1), text[:1].upper() + text[1:])
    return found


CALLOUT = re.compile(r'<blockquote>\s*<p>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*', re.I)


# Mark's writing rule (2026-10-26): no em dashes anywhere on the site. Docs written before the rule still have them,
# so they're rewritten here: a term and its explanation get a colon, an aside or a joined clause gets a comma.
TERM = re.compile(r"^(\s*(?:[-*+]|\d+\.|>)?\s*(?:\*\*[^*]+\*\*|`[^`]+`)(?:\s*\([^)]*\))?\s*)\u2014\s*")


def undash(md_text):
    md_text = md_text.replace('shows "\u2014" where', "shows a dash where")  # Unity's mixed-value mark, not prose
    out, fenced = [], False
    for line in md_text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if fenced or "\u2014" not in line:
            out.append(line)
            continue
        if line.startswith("#"):
            line = re.sub(r"\s*\u2014\s*", ": ", line, count=1)
        line = TERM.sub(lambda m: m.group(1).rstrip() + ": ", line, count=1)
        line = re.sub(r"^(\s*(?:[-*+]|\d+\.)?\s*)\u2014\s*", r"\1", line)   # a dash opening a line
        line = re.sub(r"([,;:.!?])?\s*\u2014\s*", lambda m: (m.group(1) or ",") + " ", line)
        out.append(line.rstrip() if line.rstrip().endswith(",") else line)
    return "\n".join(out)


def convert(md_text, doc_out, folder=""):
    """Markdown to HTML; returns (html, [(level, id, title)]). folder: the page's subfolder of Documentation, if any."""
    import markdown  # only needed for the docs
    from markdown.extensions.toc import TocExtension

    def relink(match):
        target, anchor = match.group(1), match.group(2) or ""
        key = posixpath.normpath(posixpath.join(folder, target)) if folder else target
        return f"]({doc_out.get(key, target)}{anchor})"

    md_text = undash(md_text)
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
  <div class="docs-product"><a href="index.html">{html.escape(product['short'])} docs</a><span class="pill">v{product['version']}</span>{'' if product['status'] == 'live' else '<span class="pill pill-dev">Coming soon</span>'}</div>
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
    # Encoded, so an "&" in a title ("Settings & Menu Kit") stays part of it
    q = urllib.parse.quote_plus(f"Docs: {title}", safe=":")
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
    if "support.html" not in doc_out.values():
        extras.append(("support.html", "Support", support_markdown(product), "Where to get help and how to report a bug"))
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
        shutil.copytree(docs_dir / "Images", out_dir / "img", dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.meta"))
    for folder in sorted({posixpath.dirname(src) for _, src, _, _ in pages} - {""}):
        if (docs_dir / folder / "Images").exists():
            shutil.copytree(docs_dir / folder / "Images", out_dir / "img" / folder, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.meta"))

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
            images = doc_images_for(product, out)
            if images:
                body_html = add_doc_figures(body_html, images)
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


def support_markdown(product):
    """A docs Support page for a kit that doesn't ship one: every channel as plain text, and what to send."""
    lines = ["# Support", "",
             f"Stuck, or found a bug in the {product['name']}? Every message is read by the developer who wrote it.", "",
             "## Where to ask", ""]
    if DISCORD_URL:
        lines.append(f"- **Discord** (questions, ideas, show and tell): <{DISCORD_URL}>")
    if ISSUES_URL:
        lines.append(f"- **Bug tracker** (report a bug and follow it until it's fixed): <{ISSUES_URL.removesuffix('/issues')}>")
    lines += [f"- **Email**: <{EMAIL}>", f"- **Website and documentation**: <{SITE_URL}>", "",
              "## Reporting a bug", "", "Send these and it can be fixed fast:", ""]
    if product.get("support_info"):
        lines.append(f"1. **The support info.** {product['support_info']}: it puts the kit's version, Unity's version "
                     "and your render pipeline on the clipboard. Nothing is sent anywhere.")
    else:
        lines.append("1. **The versions:** the kit's version, Unity's version and your render pipeline.")
    lines += ["2. **What you did**, step by step, and what you expected to happen.",
              "3. **What happened instead**, with a screenshot if it shows.",
              "4. **Any red errors** from the Console (click one, then copy its full text).", ""]
    if product.get("store"):
        lines += ["## Reviews", "",
                  f"If the {product['short']} saves you time, a short review on the [Asset Store]({product['store']}) "
                  "helps a lot. Thank you!", ""]
    return "\n".join(lines)


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
                # The first paragraph, with its wrapped lines
                m = re.search(r"^(?!#|\||-|\s|```)(.+(?:\n(?!#|\||-|\s|```).+)*)", rendered[out][1], re.M)
                desc = re.sub(r"\s+", " ", m.group(1)) if m else ""
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
{'' if product['status'] == 'live' else '<p class="dim">Free, coming soon to the Asset Store.</p>' if product.get('free') else '<p class="dim">Coming soon to the Asset Store.</p>'}
<div class="btn-row">
  <a class="btn" href="getting-started.html">Get started</a>
  {f'<a class="btn btn-ghost" href="{product["store"]}" rel="noopener">Asset Store {ICON_EXTERNAL}</a>' if product["store"] else ""}
</div>
<div class="callout" id="quick-start">
  <p class="label label-accent">Quick start: {product.get("quick_start_time", "five minutes")}</p>
  <ol>{steps}</ol>
</div>
{"".join(sections_html)}
<h2 id="help">Need help?</h2>
<div class="doc-cards">
  <a class="doc-card" href="troubleshooting.html"><strong>Troubleshooting</strong><span>Answers to the most common problems.</span></a>
  {f'<a class="doc-card" href="{DISCORD_URL}" rel="noopener"><strong>Discord</strong><span>Ask other users and the developer.</span></a>' if DISCORD_URL else ''}
  <a class="doc-card" href="support.html"><strong>Support</strong><span>Report a bug or email the developer.</span></a>
</div>
{f'<p class="muted">If the {html.escape(product["short"])} saves you time, a short review on the <a href="{product["store"]}" rel="noopener">Asset Store</a> helps a lot. Thank you!</p>' if product["store"] else ""}""", toc


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
