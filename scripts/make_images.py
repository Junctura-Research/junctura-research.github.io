"""Make the web versions of the intersection images from the Getty originals.

The full-resolution originals are licensed and stay in the private research
repository (lab/site-images/). Only the resized, compressed versions made here
are committed to this public repository. Run locally, not in CI:

    python3 scripts/make_images.py /path/to/lab/site-images

Writes, for each <name>.jpg (e.g. ai-bio.jpg), into images/intersections/:
  <name>-banner.jpg  1400 x 700  (2:1, top of the intersection page)   <= 120 KB
  <name>-og.jpg      1200 x 630  (social-share preview)                <= 110 KB
  <name>-thumb.jpg    240 x 120  (home-page list, shown at 120 x 60)   <=  12 KB
Each is a centre crop. Needs Pillow.
"""

import io
import sys
from pathlib import Path

from PIL import Image

SIZES = [  # suffix, aspect ratio, pixel size, size limit in KB
    ("banner", 2.0, (1400, 700), 120),
    ("og", 1200 / 630, (1200, 630), 110),
    ("thumb", 2.0, (240, 120), 12),
]


def centre_crop(im: Image.Image, ratio: float) -> Image.Image:
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio)
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def main(src: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.glob("*.jpg")):
        im = Image.open(path).convert("RGB")
        for suffix, ratio, size, limit_kb in SIZES:
            img = centre_crop(im, ratio).resize(size, Image.LANCZOS)
            for quality in range(82, 50, -4):  # highest quality under the limit
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
                if buf.tell() <= limit_kb * 1024:
                    break
            (out / f"{path.stem}-{suffix}.jpg").write_bytes(buf.getvalue())
        print("made", path.stem)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), Path(__file__).resolve().parent.parent / "images" / "intersections")
