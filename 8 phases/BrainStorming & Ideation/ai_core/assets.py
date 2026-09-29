from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import IMAGE_DIR, LOGO_PATH, INVERSE_LOGO_PATH


def _get_font(size: int):
    """
    Try to use a common font. If unavailable, use Pillow's default font.
    """
    possible_fonts = [
        "arial.ttf",
        "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue

    return ImageFont.load_default()


def _create_logo(path: Path, background: str, foreground: str):
    """
    Create a simple LegalEase logo automatically.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    width = 900
    height = 260

    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)

    title_font = _get_font(72)
    subtitle_font = _get_font(30)

    title = "LegalEase"
    subtitle = "AI-Powered Legal Document Generator"

    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_box[2] - title_box[0]
    title_height = title_box[3] - title_box[1]

    title_x = (width - title_width) // 2
    title_y = 55

    draw.text(
        (title_x, title_y),
        title,
        fill=foreground,
        font=title_font,
    )

    subtitle_box = draw.textbbox(
        (0, 0),
        subtitle,
        font=subtitle_font,
    )

    subtitle_width = subtitle_box[2] - subtitle_box[0]

    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + title_height + 25

    draw.text(
        (subtitle_x, subtitle_y),
        subtitle,
        fill=foreground,
        font=subtitle_font,
    )

    image.save(path)


def ensure_logo_assets():
    """
    Create the required logo files if they don't already exist.
    """

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    if not LOGO_PATH.exists():
        _create_logo(
            LOGO_PATH,
            background="white",
            foreground="black",
        )

    if not INVERSE_LOGO_PATH.exists():
        _create_logo(
            INVERSE_LOGO_PATH,
            background="black",
            foreground="white",
        )

    return {
        "logo": LOGO_PATH,
        "inverse_logo": INVERSE_LOGO_PATH,
    }