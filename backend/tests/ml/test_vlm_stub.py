from app.ml.vlm_client import StubVLM


def test_stub_vlm_returns_match(sample_png_bytes):
    engine = StubVLM()
    result = engine.locate(image_png=sample_png_bytes, query="hello")
    assert result.engine == "stub"
    assert len(result.matches) == 1
    m = result.matches[0]
    assert "hello" in m.text
    assert 0 <= m.bbox.x <= 1 and 0 <= m.bbox.y <= 1
