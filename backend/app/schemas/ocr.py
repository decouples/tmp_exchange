from __future__ import annotations

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalised bbox in [0, 1] range, origin top-left."""
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    w: float = Field(..., ge=0.0, le=1.0)
    h: float = Field(..., ge=0.0, le=1.0)
    page: int = 1


class OCRMatch(BaseModel):
    text: str
    confidence: float = 1.0
    bbox: BoundingBox


class OCRResult(BaseModel):
    matches: list[OCRMatch] = []
    engine: str = "stub"
    elapsed_ms: int = 0


class OCRRequest(BaseModel):
    file_id: int
    query: str = Field(..., min_length=1, max_length=2000)
    priority: str = Field("default", pattern="^(high|default|batch)$")
