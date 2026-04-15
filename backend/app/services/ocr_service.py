"""High-level OCR orchestration: run VLM, optionally merge with fallback."""
from __future__ import annotations

from app.core.logging import get_logger
from app.ml.vlm_client import get_vlm
from app.schemas.ocr import OCRResult
from app.services.pdf_service import render_pdf_pages

log = get_logger(__name__)


def run_single_image(*, image_png: bytes, query: str, page: int = 1) -> OCRResult:
    engine = get_vlm()
    result = engine.locate(image_png=image_png, query=query, page=page)

    if not result.matches:
        try:
            from app.ml.ocr_engine import get_fallback_engine

            fb = get_fallback_engine().locate(image_png=image_png, query=query, page=page)
            if fb.matches:
                log.info("VLM returned 0 matches; using fallback (%d)", len(fb.matches))
                return fb
        except Exception as e:
            log.debug("Fallback engine unavailable: %s", e)
    return result


def run_pdf(*, pdf_bytes: bytes, query: str) -> OCRResult:
    engine = get_vlm()
    pages = render_pdf_pages(pdf_bytes)
    all_matches = []
    total_elapsed = 0
    for p in pages:
        res = engine.locate(image_png=p.png, query=query, page=p.page_number)
        all_matches.extend(res.matches)
        total_elapsed += res.elapsed_ms
    return OCRResult(matches=all_matches, engine=engine.name, elapsed_ms=total_elapsed)
