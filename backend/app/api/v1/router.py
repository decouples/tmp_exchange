from fastapi import APIRouter

from app.api.v1.endpoints import auth, files, ocr, tasks, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(ws.router, tags=["ws"])
