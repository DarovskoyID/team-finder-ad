from hashlib import sha256
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def create_avatar(name):
    letter = name.strip()[:1].upper() or "У"
    colors = ("#475569", "#334155", "#3f6212", "#075985", "#6b21a8")
    index = sha256(name.encode()).digest()[0] % len(colors)
    image = Image.new("RGB", (256, 256), colors[index])
    font_path = (
        settings.BASE_DIR
        / "static"
        / "fonts"
        / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    )
    font = ImageFont.truetype(str(font_path), 144)
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox(
        (0, 0), letter, font=font
    )
    position = (
        (256 - right - left) / 2,
        (256 - bottom - top) / 2,
    )
    draw.text(position, letter, font=font, fill="white")
    output = BytesIO()
    image.save(output, format="PNG")
    return ContentFile(output.getvalue(), name=f"{uuid4().hex}.png")
