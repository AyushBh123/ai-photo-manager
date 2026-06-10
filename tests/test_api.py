import os
import tempfile
from pathlib import Path
from PIL import Image
import pytest
from httpx import AsyncClient
import app.main as main_module
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_scan_local_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path = Path(tmpdir) / "test_image.jpg"
        Image.new("RGB", (64, 64), color="blue").save(image_path)

        async with AsyncClient(app=app, base_url="http://test") as client:
            scan_response = await client.post("/scan/local", json={"paths": [tmpdir]})
            assert scan_response.status_code == 200
            result = scan_response.json()
            assert result["scanned_images"] >= 1

            list_response = await client.get("/images")
            assert list_response.status_code == 200
            images = list_response.json()
            assert any("test_image.jpg" in item["path"] for item in images)

            search_response = await client.post("/search", json={"query": "blue picture", "top_n": 5})
            assert search_response.status_code == 200
            assert search_response.json()["query"] == "blue picture"


@pytest.mark.asyncio
async def test_google_photos_sync_endpoint(monkeypatch):
    monkeypatch.setattr(main_module.indexer, "sync_google_photos", lambda client_secrets_path, token_path: 3)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/connect/google-photos",
            json={
                "client_secrets_path": "data/client_secret.json",
                "token_path": "data/google_photos_token.json",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scanned_images"] == 3
    assert payload["source"] == "google_photos"
