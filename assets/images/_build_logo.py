"""
One-shot logo processing for dcr_logo_2026.png:
 - flood-fill the beige background from corners → transparent
 - crop to bounding box
 - export sized variants for header, footer, favicon, and a mark-only crop
Run once when the source logo changes.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
SRC = HERE / "dcr_logo_2026.png"
OUT = HERE  # write siblings into assets/images/


def load_transparent(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    # Flood-fill from all four corners — only contiguous bg pixels
    # become transparent, so copper + navy letterforms are preserved.
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(im, seed, (0, 0, 0, 0), thresh=42)
    # Crop to content bbox
    bbox = im.getbbox()
    return im.crop(bbox)


def save_resized(im: Image.Image, width: int, path: Path) -> None:
    ratio = width / im.size[0]
    new_h = int(round(im.size[1] * ratio))
    resized = im.resize((width, new_h), Image.LANCZOS)
    resized.save(path, optimize=True)
    print(f"  wrote {path.name}  {resized.size}")


def save_square(im: Image.Image, size: int, path: Path, pad: int = 8) -> None:
    """Fit the image into a transparent square of `size`×`size` with padding."""
    scale = (size - 2 * pad) / max(im.size)
    new_w = int(round(im.size[0] * scale))
    new_h = int(round(im.size[1] * scale))
    scaled = im.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(scaled, (x, y), scaled)
    canvas.save(path, optimize=True)
    print(f"  wrote {path.name}  {canvas.size}")


def main() -> None:
    print(f"loading {SRC.name} …")
    logo = load_transparent(SRC)
    print(f"  transparent bbox: {logo.size}")

    # Full brand mark (houses + D.C.R + subscript line)
    save_resized(logo, 1600, OUT / "logo.png")
    save_resized(logo, 800,  OUT / "logo@1x.png")
    save_resized(logo,  400, OUT / "logo@sm.png")

    # Mark only — crop the "DeAngelo's Construction & Remodeling, Inc."
    # subscript off the bottom so the houses + D.C.R stand on their own.
    # By inspection the subscript occupies the lower ~22%.
    w, h = logo.size
    mark = logo.crop((0, 0, w, int(h * 0.78)))
    # Trim any residual transparent margin
    mark = mark.crop(mark.getbbox())
    save_resized(mark, 800, OUT / "logo-mark.png")

    # Favicons — square, from the mark
    save_square(mark,  32, OUT / "favicon-32.png",  pad=1)
    save_square(mark,  48, OUT / "favicon-48.png",  pad=2)
    save_square(mark, 192, OUT / "favicon-192.png", pad=8)
    save_square(mark, 512, OUT / "favicon-512.png", pad=16)

    # Multi-res .ico
    ico_src = Image.open(OUT / "favicon-192.png")
    ico_src.save(
        OUT / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (192, 192)],
    )
    print(f"  wrote favicon.ico")

    # OG / social share image — 1200x630, logo centered on paper-cream
    og = Image.new("RGBA", (1200, 630), (236, 228, 208, 255))  # #ece4d0
    scale = min((1200 - 160) / logo.size[0], (630 - 120) / logo.size[1])
    lw = int(round(logo.size[0] * scale))
    lh = int(round(logo.size[1] * scale))
    logo_resized = logo.resize((lw, lh), Image.LANCZOS)
    og.paste(logo_resized, ((1200 - lw) // 2, (630 - lh) // 2), logo_resized)
    og.convert("RGB").save(OUT / "og-image.jpg", quality=88, optimize=True)
    print(f"  wrote og-image.jpg  {og.size}")


if __name__ == "__main__":
    main()
