from __future__ import annotations

import hashlib
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.file import file_crud
from app.models.file import File
from app.utils.storage import get_storage

ALLOWED_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}
MAX_SIZE = 50 * 1024 * 1024  # 50 MiB


class FileValidationError(ValueError):
    pass


def _guess_page_count(content_type: str, data: bytes) -> int:
    if content_type != "application/pdf":
        return 1
    try:
        import pymupdf  # type: ignore

        doc = pymupdf.open(stream=data, filetype="pdf")
        return doc.page_count
    except Exception:
        return 1


async def save_upload(
    db: AsyncSession,
    *,
    owner_id: int,
    filename: str,
    content_type: str,
    data: bytes,
) -> File:
    if content_type not in ALLOWED_TYPES:
        raise FileValidationError(f"Unsupported content type: {content_type}")
    if len(data) > MAX_SIZE:
        raise FileValidationError(f"File too large: {len(data)} bytes")

    md5 = hashlib.md5(data).hexdigest()
    existing = await file_crud.get_by_md5(db, owner_id=owner_id, md5=md5)
    if existing:
        return existing

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    storage_key = f"uploads/{owner_id}/{md5}.{ext}"
    await get_storage().put(storage_key, data, content_type=content_type)

    return await file_crud.create(
        db,
        obj_in={
            "owner_id": owner_id,
            "filename": filename,
            "content_type": content_type,
            "size": len(data),
            "md5": md5,
            "storage_key": storage_key,
            "page_count": _guess_page_count(content_type, data),
        },
    )


async def read_file_bytes(file: File) -> bytes:
    return await get_storage().get(file.storage_key)


def new_task_id() -> str:
    return uuid.uuid4().hex
