from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RenderedPage:
    page_number: int  # 1-indexed
    png: bytes
    width: int
    height: int


def render_pdf_pages(data: bytes, dpi: int = 144) -> list[RenderedPage]:
    """Render every page of a PDF to PNG bytes."""
    import pymupdf  # type: ignore

    doc = pymupdf.open(stream=data, filetype="pdf")
    zoom = dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)
    pages: list[RenderedPage] = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pages.append(
            RenderedPage(
                page_number=i,
                png=pix.tobytes("png"),
                width=pix.width,
                height=pix.height,
            )
        )
    doc.close()
    return pages
