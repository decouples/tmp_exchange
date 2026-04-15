from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.ocr import OCRResult


class OCREngine(ABC):
    name: str = "base"

    @abstractmethod
    def locate(self, *, image_png: bytes, query: str, page: int = 1) -> OCRResult:
        """Find `query` inside `image_png` and return normalised bboxes."""
