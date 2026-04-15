"""Vision-language model client.

Supports:
- `stub`:         deterministic fake output (no ML deps) — used in tests & CI.
- `qwen-vl-local`: local Qwen2-VL via `transformers` — used in prod / dev.

The Qwen-VL code path is guarded by lazy imports so the backend can boot
without torch installed (e.g. pure API layer container).
"""
from __future__ import annotations

import json
import re
import time
from functools import lru_cache

from app.core.config import settings
from app.core.logging import get_logger
from app.ml.base import OCREngine
from app.ml.coord_utils import clamp, normalise_xyxy
from app.schemas.ocr import BoundingBox, OCRMatch, OCRResult
from app.utils.image import image_size, load_image

log = get_logger(__name__)


_QWEN_PROMPT = """You are a precise document locator.
The user will provide an image and a query. Return **JSON only**, no prose, with shape:
{{"matches": [{{"text": "<matched text>", "bbox": [x1, y1, x2, y2]}}]}}
Coordinates are absolute pixel values in the image. If nothing matches, return
{{"matches": []}}. Query: {query}"""


class StubVLM(OCREngine):
    name = "stub"

    def locate(self, *, image_png: bytes, query: str, page: int = 1) -> OCRResult:
        w, h = image_size(image_png)
        bbox = BoundingBox(x=0.25, y=0.25, w=0.5, h=0.1, page=page)
        return OCRResult(
            matches=[OCRMatch(text=f"[stub] {query}", confidence=0.5, bbox=bbox)],
            engine=self.name,
        )


class QwenVLLocal(OCREngine):
    name = "qwen-vl-local"

    def __init__(self):
        self._model = None
        self._processor = None

    def _load(self):
        if self._model is not None:
            return
        import torch  # type: ignore
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration  # type: ignore

        log.info("Loading Qwen-VL model: %s (device=%s)", settings.vlm_model, settings.vlm_device)
        dtype = torch.float16 if settings.vlm_device != "cpu" else torch.float32
        self._model = Qwen2VLForConditionalGeneration.from_pretrained(
            settings.vlm_model, torch_dtype=dtype
        ).to(settings.vlm_device)
        self._processor = AutoProcessor.from_pretrained(settings.vlm_model)

    def locate(self, *, image_png: bytes, query: str, page: int = 1) -> OCRResult:
        self._load()
        import torch  # type: ignore

        img = load_image(image_png)
        w, h = img.size
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": _QWEN_PROMPT.format(query=query)},
                ],
            }
        ]
        text = self._processor.apply_chat_template(  # type: ignore[union-attr]
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(  # type: ignore[misc]
            text=[text], images=[img], padding=True, return_tensors="pt"
        ).to(settings.vlm_device)

        t0 = time.time()
        with torch.inference_mode():
            output_ids = self._model.generate(  # type: ignore[union-attr]
                **inputs, max_new_tokens=settings.vlm_max_new_tokens, do_sample=False
            )
        trimmed = [o[len(i):] for i, o in zip(inputs.input_ids, output_ids)]
        raw = self._processor.batch_decode(  # type: ignore[union-attr]
            trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        elapsed = int((time.time() - t0) * 1000)
        matches = _parse_matches(raw, img_w=w, img_h=h, page=page)
        return OCRResult(matches=matches, engine=self.name, elapsed_ms=elapsed)


def _parse_matches(raw: str, *, img_w: int, img_h: int, page: int) -> list[OCRMatch]:
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    out: list[OCRMatch] = []
    for item in data.get("matches", []):
        bbox_raw = item.get("bbox")
        if not isinstance(bbox_raw, (list, tuple)) or len(bbox_raw) != 4:
            continue
        norm = normalise_xyxy(tuple(float(x) for x in bbox_raw), img_w, img_h)
        norm["page"] = page
        out.append(
            OCRMatch(
                text=str(item.get("text", "")),
                confidence=float(item.get("confidence", 0.8)),
                bbox=BoundingBox(**clamp(norm)),
            )
        )
    return out


@lru_cache
def get_vlm() -> OCREngine:
    if settings.vlm_provider == "qwen-vl-local":
        return QwenVLLocal()
    return StubVLM()
