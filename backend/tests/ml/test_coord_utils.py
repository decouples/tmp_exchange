from app.ml.coord_utils import clamp, normalise_xywh, normalise_xyxy


def test_normalise_xyxy_basic():
    b = normalise_xyxy((10, 20, 110, 70), img_w=200, img_h=100)
    assert b == {"x": 0.05, "y": 0.2, "w": 0.5, "h": 0.5}


def test_normalise_xywh_clamps():
    b = normalise_xywh((-10, -10, 50, 50), img_w=100, img_h=100)
    assert b["x"] == 0.0 and b["y"] == 0.0
    assert 0.0 <= b["w"] <= 1.0


def test_clamp_out_of_range():
    b = clamp({"x": 1.5, "y": -0.2, "w": 2.0, "h": 0.5, "page": 3})
    assert b["x"] == 1.0 and b["y"] == 0.0 and b["w"] == 1.0 and b["page"] == 3
