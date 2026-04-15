from fastapi.testclient import TestClient


def test_health_ok():
    # Import inside test so env vars from conftest apply first.
    from app.main import create_app

    app = create_app()
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
