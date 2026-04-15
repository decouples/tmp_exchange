"""BBox coordinate utilities.

Canonical format: normalised `[x, y, w, h]` in [0, 1], origin **top-left**.
PDFs use bottom-left origin — callers are responsible for flipping Y before
entering this module (we render PDFs to raster first, which gives top-left).
"""
from __future__ import annotations


def normalise_xyxy(xyxy: tuple[float, float, float, float], img_w: int, img_h: int) -> dict:
    x1, y1, x2, y2 = xyxy
    x1, x2 = sorted([max(0.0, x1), min(float(img_w), x2)])
    y1, y2 = sorted([max(0.0, y1), min(float(img_h), y2)])
    return {
        "x": x1 / img_w,
        "y": y1 / img_h,
        "w": max(0.0, (x2 - x1) / img_w),
        "h": max(0.0, (y2 - y1) / img_h),
    }


def normalise_xywh(xywh: tuple[float, float, float, float], img_w: int, img_h: int) -> dict:
    x, y, w, h = xywh
    return normalise_xyxy((x, y, x + w, y + h), img_w, img_h)


def denormalise(bbox: dict, img_w: int, img_h: int) -> tuple[int, int, int, int]:
    return (
        int(bbox["x"] * img_w),
        int(bbox["y"] * img_h),
        int(bbox["w"] * img_w),
        int(bbox["h"] * img_h),
    )


def clamp(bbox: dict) -> dict:
    out = {k: max(0.0, min(1.0, float(v))) for k, v in bbox.items() if k in ("x", "y", "w", "h")}
    if "page" in bbox:
        out["page"] = int(bbox["page"])
    return out
