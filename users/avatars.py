from hashlib import sha256
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_COLORS,
    AVATAR_SIZE,
    AVATAR_FONT_SIZE,
)


def create_avatar(name):
    letter = name.strip()[:1].upper() or "У"
    index = sha256(name.encode()).digest()[0] % len(AVATAR_COLORS)
    image = Image.new(
        "RGB", (AVATAR_SIZE, AVATAR_SIZE), AVATAR_COLORS[index]
    )
    font_path = (
        settings.BASE_DIR
        / "static"
        / "fonts"
        / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    )
    font = ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox(
        (0, 0), letter, font=font
    )
    position = (
        (AVATAR_SIZE - right - left) / 2,
        (AVATAR_SIZE - bottom - top) / 2,
    )
    draw.text(position, letter, font=font, fill="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return ContentFile(output.getvalue(), name=f"{uuid4().hex}.png")
