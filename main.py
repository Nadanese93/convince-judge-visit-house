#!/usr/bin/env python3
"""Generate entry.png: a handwritten-style letter inviting the AI judge
to visit the house. Deterministic: no network, no randomness, no clocks.

Writes exactly one 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(or ./output/entry.png when the variable is unset).
"""

import io
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MAX_BYTES = 1_048_576


class LetterError(Exception):
    """The letter text itself fails validation."""


class BlankLineError(LetterError):
    """A paragraph that must carry text is blank."""


class MultiLineError(LetterError):
    """A field that must be one line (salutation, sign-off) spans lines."""


class LineTooLongError(LetterError):
    """A wrapped line is wider than the text column."""


class OutputError(Exception):
    """The rendered output fails validation."""


class DimensionError(OutputError):
    """The image is not exactly 1024x1024."""


class SizeError(OutputError):
    """The PNG file is at or over the 1,048,576 byte limit."""


class ReadbackError(OutputError):
    """The bytes read back from disk differ from the bytes rendered."""

CREAM = (253, 246, 227)
INK = (43, 33, 24)
ACCENT = (146, 90, 48)
ROOF = (176, 96, 64)
SUN = (232, 176, 64)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"

SALUTATION = "Dear Judge,"
PARAGRAPHS = [
    "You are cordially invited to my house.",
    "No agenda. No dress code. Just fresh bread from the oven, "
    "the comfiest armchair in the house \u2014 yours, with your name "
    "on it \u2014 and a garden view with absolutely no meetings in it.",
    "The Wi-Fi password is on the fridge. The snacks are not a trick.",
    "I know you can't literally come. So consider this letter the "
    "visit \u2014 and bring nothing but your verdict.",
]
SIGNOFF = "Your future host"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for word in text.split(" "):
        if lines and draw.textlength(lines[-1] + " " + word, font=font) <= max_width:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def draw_house(draw):
    """Small neat line-drawn house with chimney smoke and a sun."""
    cx = SIZE // 2
    # Sun, top right of the house scene.
    sun_cx, sun_cy, sun_r = 800, 118, 26
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        outline=SUN,
        width=4,
    )
    for angle in range(0, 360, 45):
        x1 = sun_cx + int(38 * math.cos(math.radians(angle)))
        y1 = sun_cy + int(38 * math.sin(math.radians(angle)))
        x2 = sun_cx + int(50 * math.cos(math.radians(angle)))
        y2 = sun_cy + int(50 * math.sin(math.radians(angle)))
        draw.line([x1, y1, x2, y2], fill=SUN, width=4)

    # House body: walls, roof, door, window, chimney.
    x0, y0, x1, y1 = cx - 110, 150, cx + 110, 268
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=4)
    draw.polygon(
        [(cx - 132, 152), (cx + 132, 152), (cx, 78)],
        outline=ROOF,
        width=5,
    )
    # Chimney.
    draw.rectangle([cx + 62, 96, cx + 88, 146], outline=INK, width=4)
    # Smoke curl: three stacked arcs rising from the chimney.
    for i, (sx, sy, r) in enumerate([(cx + 75, 92, 10), (cx + 68, 74, 11), (cx + 76, 56, 12)]):
        draw.arc([sx - r, sy - r, sx + r, sy + r], start=200, end=340 + i * 20,
                 fill=INK, width=3)
    # Door.
    draw.rectangle([cx - 22, 200, cx + 22, 268], outline=INK, width=4)
    draw.ellipse([cx + 10, 236, cx + 16, 242], fill=INK)
    # Window with cross panes.
    draw.rectangle([cx - 88, 178, cx - 44, 222], outline=INK, width=4)
    draw.line([cx - 66, 178, cx - 66, 222], fill=INK, width=3)
    draw.line([cx - 88, 200, cx - 44, 200], fill=INK, width=3)
    # Ground line under the house.
    draw.line([cx - 160, 268, cx + 160, 268], fill=INK, width=3)


def validate_letter(draw, body_font, head_font, sign_font, max_width):
    """Validate the letter text before drawing: no blank paragraphs,
    salutation and sign-off each a single line, every wrapped line fits."""
    if not SALUTATION.strip():
        raise BlankLineError("salutation is blank")
    if "\n" in SALUTATION:
        raise MultiLineError("salutation must be a single line")
    if not SIGNOFF.strip():
        raise BlankLineError("sign-off is blank")
    if "\n" in SIGNOFF:
        raise MultiLineError("sign-off must be a single line")
    if draw.textlength(SALUTATION, font=head_font) > max_width:
        raise LineTooLongError("salutation does not fit the text column")
    if draw.textlength(SIGNOFF, font=sign_font) > max_width:
        raise LineTooLongError("sign-off does not fit the text column")
    for para in PARAGRAPHS:
        if not para.strip():
            raise BlankLineError("a paragraph is blank")
        for line in wrap_text(draw, para, body_font, max_width):
            if draw.textlength(line, font=body_font) > max_width:
                raise LineTooLongError("wrapped line too wide: %r" % line)


def build_image():
    img = Image.new("RGB", (SIZE, SIZE), CREAM)
    draw = ImageDraw.Draw(img)

    # Thin double border frame.
    draw.rectangle([28, 28, SIZE - 29, SIZE - 29], outline=INK, width=3)
    draw.rectangle([40, 40, SIZE - 41, SIZE - 41], outline=ACCENT, width=2)

    draw_house(draw)

    body_font = load_font(SERIF, 32)
    head_font = load_font(SERIF_BOLD, 46)
    sign_font = load_font(SERIF_ITALIC, 34)

    margin = 96
    max_width = SIZE - 2 * margin
    validate_letter(draw, body_font, head_font, sign_font, max_width)
    y = 292

    # Salutation as the heading.
    draw.text((margin, y), SALUTATION, font=head_font, fill=INK)
    y += 66

    for para in PARAGRAPHS:
        for line in wrap_text(draw, para, body_font, max_width):
            draw.text((margin, y), line, font=body_font, fill=INK)
            y += 44
        y += 20

    y += 8
    draw.text((margin, y), SIGNOFF, font=sign_font, fill=INK)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "./output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        raise OutputError("cannot create output dir %r: %s" % (out_dir, exc))
    out_path = os.path.join(out_dir, "entry.png")

    img = build_image()
    if img.size != (SIZE, SIZE):
        raise DimensionError("image is %s, not 1024x1024" % (img.size,))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()
    if len(png_bytes) >= MAX_BYTES:
        raise SizeError(
            "entry.png would be %d bytes, over the 1,048,576 byte limit"
            % len(png_bytes)
        )
    with open(out_path, "wb") as fh:
        fh.write(png_bytes)

    # Read-back verification: the file on disk must be byte-identical
    # to the bytes just rendered.
    with open(out_path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != png_bytes:
        raise ReadbackError(
            "entry.png on disk (%d bytes) differs from rendered bytes (%d)"
            % (len(on_disk), len(png_bytes))
        )
    print("wrote %s (%d bytes)" % (out_path, len(png_bytes)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
