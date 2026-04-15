import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("STORAGE_LOCAL_PATH", "./test_storage")
os.environ.setdefault("VLM_PROVIDER", "stub")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")

import pytest


@pytest.fixture
def sample_png_bytes() -> bytes:
    from io import BytesIO

    from PIL import Image

    img = Image.new("RGB", (200, 100), color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
