"""Cuts the home page's pictures from the product pictures already on the site.

    python tools/site_images.py

Writes assets/img/home/<slug>-card.jpg (the product card), <slug>-main.jpg and <slug>-inset.jpg (the "closer look"
row). Every picture is a crop of a real capture in assets/img/<slug>/; nothing is drawn. When a product's pictures
change, change its entry below and run this again, then python tools/build.py.

Product icons (assets/img/<slug>/icon.png, 160 x 160) are copied by hand from each product's final store icon.
"""
import pathlib

from PIL import Image

SITE = pathlib.Path(__file__).resolve().parent.parent
IMG = SITE / "assets" / "img"
OUT = IMG / "home"

# slug: {"card" | "main" | "inset": (source picture, crop box as fractions of the source: left, top, right, bottom)}
CROPS = {
    "shipready": {
        "card": ("shipready/hero-main-menu.jpg", (0, 0, 1, 1)),
        "main": ("shipready/04-save-quit-continue.jpg", (0.099, 0.262, 0.901, 0.925)),
        "inset": ("shipready/06-player-settings-ready.jpg", (0.169, 0.262, 0.830, 0.925)),
    },
    "bearing": {
        "card": ("bearing/hero.jpg", (0, 0, 1, 1)),
        "main": ("bearing/full-map.jpg", (0.268, 0.152, 0.961, 0.835)),
        "inset": ("bearing/chart-table.jpg", (0.259, 0.235, 0.897, 0.747)),
    },
    "snapbuild": {
        "card": ("snapbuild/world.jpg", (0, 0, 1, 1)),
        "main": ("snapbuild/02-prefabs.jpg", (0.040, 0.202, 0.747, 0.905)),
        "inset": ("snapbuild/02-prefabs.jpg", (0.771, 0.2, 0.965, 0.716)),
    },
    "interactra": {
        "card": ("interactra/01-hero.jpg", (0, 0, 1, 1)),
        "main": ("interactra/02-build.jpg", (0, 0, 1, 1)),
        "inset": ("interactra/03-wire.jpg", (0.3, 0.1, 1, 0.8)),
    },
    "responsive-fx": {
        "card": ("responsive-fx/volley.jpg", (0, 0, 1, 1)),
        "main": ("responsive-fx/glass.jpg", (0, 0, 1, 1)),
        "inset": ("responsive-fx/impact-lab.jpg", (0.28, 0, 0.72, 0.62)),
    },
}

# Output: (width, height or None to keep the crop's own shape)
SIZES = {"card": (720, 450), "main": (1200, None), "inset": (640, None)}


def cover(im, width, height):
    """Scales and centre-crops to exactly width x height."""
    scale = max(width / im.width, height / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - width) // 2, (im.height - height) // 2
    return im.crop((left, top, left + width, top + height))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, parts in CROPS.items():
        for part, (source, box) in parts.items():
            im = Image.open(IMG / source).convert("RGB")
            w, h = im.size
            im = im.crop((round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)))
            width, height = SIZES[part]
            if height:
                im = cover(im, width, height)
            elif im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            out = OUT / f"{slug}-{part}.jpg"
            im.save(out, quality=84, optimize=True, progressive=True)
            print("wrote", out.relative_to(SITE).as_posix(), im.size, f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
