"""Traditional OCR fallback (PaddleOCR)."""
from __future__ import annotations

from functools import lru_cache

from app.core.logging import get_logger
from app.ml.base import OCREngine
from app.ml.coord_utils import clamp, normalise_xyxy
from app.schemas.ocr import BoundingBox, OCRMatch, OCRResult
from app.utils.image import image_size

log = get_logger(__name__)


class PaddleOCREngine(OCREngine):
    name = "paddleocr"

    def __init__(self):
        self._ocr = None

    def _load(self):
        if self._ocr is not None:
            return
        from paddleocr import PaddleOCR  # type: ignore

        log.info("Loading PaddleOCR …")
        self._ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

    def locate(self, *, image_png: bytes, query: str, page: int = 1) -> OCRResult:
        try:
            self._load()
        except Exception as e:
            log.warning("PaddleOCR unavailable: %s — returning empty.", e)
            return OCRResult(matches=[], engine=self.name)

        import numpy as np

        from app.utils.image import load_image

        img = load_image(image_png)
        w, h = img.size
        arr = np.array(img)

        raw = self._ocr.ocr(arr, cls=True)  # type: ignore[union-attr]
        lines = raw[0] if raw and isinstance(raw, list) else []
        q = query.strip().lower()
        matches: list[OCRMatch] = []
        for entry in lines or []:
            box_pts, (text, score) = entry
            if q and q not in str(text).lower():
                continue
            xs = [p[0] for p in box_pts]
            ys = [p[1] for p in box_pts]
            norm = normalise_xyxy((min(xs), min(ys), max(xs), max(ys)), w, h)
            norm["page"] = page
            matches.append(
                OCRMatch(
                    text=str(text),
                    confidence=float(score),
                    bbox=BoundingBox(**clamp(norm)),
                )
            )
        return OCRResult(matches=matches, engine=self.name)


@lru_cache
def get_paddle() -> OCREngine:
    return PaddleOCREngine()


def get_fallback_engine() -> OCREngine:
    return get_paddle()
