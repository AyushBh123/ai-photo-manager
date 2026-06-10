import json
import os
import time
import uuid
from pathlib import Path
from typing import List
from PIL import Image, UnidentifiedImageError
import imagehash

from app.models import ImageRecord
from app.services.category import CategoryService
from app.services.duplicates import DuplicateDetector
from app.services.face_grouping import FaceGroupingService
from app.services.search import SearchService
from app.services.google_photos import GooglePhotosService

SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "webp", "tiff"}

class ImageIndex:
    def __init__(self, index_path: str = "data/index.json"):
        self.index_path = Path(index_path)
        self.records: dict[str, ImageRecord] = {}
        self.category_service = CategoryService()
        self.search_service = SearchService()
        self.face_service = FaceGroupingService()
        self.duplicate_detector = DuplicateDetector()
        self.load_index()

    def load_index(self):
        if not self.index_path.exists():
            self.records = {}
            return
        try:
            with open(self.index_path, "r", encoding="utf-8") as index_file:
                data = json.load(index_file)
            self.records = {
                item["id"]: ImageRecord.from_dict(item) for item in data.get("images", [])
            }
            self._refresh_duplicate_index()
        except Exception:
            self.records = {}

    def save_index(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = {"images": [record.as_dict() for record in self.records.values()]}
        with open(self.index_path, "w", encoding="utf-8") as index_file:
            json.dump(serialized, index_file, indent=2)

    def scan_local(self, paths: List[str]) -> int:
        image_count = 0
        for base_path in paths:
            for root, _, files in os.walk(base_path):
                for filename in files:
                    if self._is_image_file(filename):
                        full_path = os.path.join(root, filename)
                        if self._index_image(full_path, source="local"):
                            image_count += 1
        self.save_index()
        return image_count

    def sync_google_photos(self, client_secrets_path: str, token_path: str) -> int:
        service = GooglePhotosService(client_secrets_path, token_path)
        items = service.fetch_library()
        count = 0
        for item in items:
            if item.get("mimeType", "").startswith("image"):
                asset_uri = item.get("baseUrl")
                name = item.get("filename", "google_photo")
                pseudo_path = f"google_photos://{name}"
                if self._index_image(pseudo_path, source="google_photos", uri=asset_uri, metadata=item):
                    count += 1
        self.save_index()
        return count

    def _is_image_file(self, filename: str) -> bool:
        return filename.lower().split(".")[-1] in SUPPORTED_EXTENSIONS

    def _find_record_by_path(self, path: str):
        for record in self.records.values():
            if record.path == path:
                return record
        return None

    def _index_image(self, path: str, source: str, uri: str | None = None, metadata: dict | None = None) -> bool:
        existing = self._find_record_by_path(path)
        if existing and os.path.exists(existing.path):
            modified = os.path.getmtime(existing.path)
            if modified == existing.modified_at:
                return False

        uri = uri or path
        image = None
        if source == "local":
            try:
                image = Image.open(path)
            except (FileNotFoundError, UnidentifiedImageError):
                return False
        else:
            image = None

        embedding = []
        categories = []
        face_encodings = []
        if image is not None:
            with image:
                image_hash = str(imagehash.phash(image))
                image_phash = image_hash
                embedding = self.category_service.model.encode(image, convert_to_tensor=False).tolist()
                categories = self.category_service.assign_categories(image, path)
                face_encodings = self.face_service.detect_face_encodings(path)
        else:
            image_hash = ""
            image_phash = ""
            categories = ["other"]

        face_ids = [f"face_{i + 1}" for i in range(len(face_encodings))]
        record = ImageRecord(
            id=str(uuid.uuid4()),
            path=path,
            uri=uri,
            source=source,
            categories=categories,
            tags=metadata.get("description", "").split() if metadata else [],
            hash=image_hash,
            phash=image_phash,
            embedding=embedding,
            face_encodings=face_encodings,
            face_ids=face_ids,
            created_at=time.time(),
            modified_at=os.path.getmtime(path) if os.path.exists(path) else time.time(),
            metadata=metadata or {},
        )
        self.records[record.id] = record
        self.duplicate_detector.register(record)
        return True

    def _refresh_duplicate_index(self):
        self.duplicate_detector = DuplicateDetector()
        for record in self.records.values():
            self.duplicate_detector.register(record)

    def find_duplicate_groups(self) -> List[dict]:
        self._refresh_duplicate_index()
        return self.duplicate_detector.summarize()

    def group_faces(self) -> List[dict]:
        return self.face_service.build_groups(list(self.records.values()))

    def search(self, query: str, top_n: int = 20) -> List[ImageRecord]:
        return self.search_service.search(query, list(self.records.values()), top_n=top_n)
