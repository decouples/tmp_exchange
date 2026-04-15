"""Import all models so Alembic's autogenerate sees them."""
from app.models.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.file import File  # noqa: F401
from app.models.ocr_record import OCRRecord  # noqa: F401
