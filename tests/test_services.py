import os
import tempfile
from pathlib import Path
from PIL import Image
import pytest
from app.services.duplicates import DuplicateDetector
from app.services.category import CategoryService
from app.services.google_photos import GooglePhotosService


def test_duplicate_detector_exact_and_near():
    class FakeRecord:
        def __init__(self, id, hash, phash):
            self.id = id
            self.hash = hash
            self.phash = phash

    detector = DuplicateDetector(near_threshold=5)
    detector.register(FakeRecord("1", "aaa", "0011"))
    detector.register(FakeRecord("2", "aaa", "0011"))
    detector.register(FakeRecord("3", "bbb", "0010"))
    results = detector.summarize()
    assert any(group["reason"] == "exact" for group in results)
    assert any(group["reason"] == "near" for group in results)


def test_category_service_assigns_relevant_tag():
    service = CategoryService()
    with tempfile.TemporaryDirectory() as tmpdir:
        image_path = Path(tmpdir) / "receipt.png"
        Image.new("RGB", (32, 32), color="white").save(image_path)
        image = Image.open(image_path)
        categories = service.assign_categories(image, str(image_path))
        assert "receipts" in categories or "other" in categories


def test_google_photos_service_requires_client_secret_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        token_path = Path(tmpdir) / "token.json"

        with pytest.raises(FileNotFoundError):
            GooglePhotosService(str(Path(tmpdir) / "missing_client_secret.json"), str(token_path))
