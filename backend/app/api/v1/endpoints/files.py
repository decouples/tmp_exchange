from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import DB, CurrentUser
from app.crud.file import file_crud
from app.schemas.file import FileRead
from app.services.file_service import FileValidationError, read_file_bytes, save_upload

router = APIRouter()


@router.post("", response_model=FileRead)
async def upload_file(
    db: DB,
    user: CurrentUser,
    file: UploadFile = File(...),
) -> FileRead:
    data = await file.read()
    try:
        f = await save_upload(
            db,
            owner_id=user.id,
            filename=file.filename or "upload.bin",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileRead.model_validate(f)


@router.get("", response_model=list[FileRead])
async def list_files(db: DB, user: CurrentUser) -> list[FileRead]:
    files = await file_crud.list_for_owner(db, owner_id=user.id)
    return [FileRead.model_validate(f) for f in files]


@router.get("/{file_id}/raw")
async def download_file(file_id: int, db: DB, user: CurrentUser):
    f = await file_crud.get(db, file_id)
    if f is None or f.owner_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")
    data = await read_file_bytes(f)
    return Response(content=data, media_type=f.content_type)
