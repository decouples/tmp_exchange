from __future__ import annotations

import io

from PIL import Image


def load_image(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    return img


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def image_size(data: bytes) -> tuple[int, int]:
    img = load_image(data)
    return img.size
