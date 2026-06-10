from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    indexed_images: int

class LocalScanRequest(BaseModel):
    paths: List[str]

class GooglePhotosSyncRequest(BaseModel):
    client_secrets_path: str
    token_path: str = "data/google_photos_token.json"


class GooglePhotosSyncResult(BaseModel):
    scanned_images: int
    indexed_images: int
    source: str = "google_photos"

class SearchRequest(BaseModel):
    query: str
    top_n: int = 20

class ImageResult(BaseModel):
    id: str
    path: str
    uri: str
    source: str
    categories: List[str]
    tags: List[str]
    face_ids: List[str]
    created_at: float
    modified_at: float

    @classmethod
    def from_record(cls, record):
        return cls(
            id=record.id,
            path=record.path,
            uri=record.uri,
            source=record.source,
            categories=record.categories,
            tags=record.tags,
            face_ids=record.face_ids,
            created_at=record.created_at,
            modified_at=record.modified_at,
        )

class ScanResponse(BaseModel):
    scanned_images: int
    indexed_images: int

class DuplicateGroup(BaseModel):
    reason: str
    images: List[ImageResult]

    @classmethod
    def from_group(cls, group):
        return cls(
            reason=group["reason"],
            images=[ImageResult.from_record(r) for r in group["images"]],
        )

class FaceGroup(BaseModel):
    face_id: str
    image_ids: List[str]

class FaceGroupResponse(BaseModel):
    groups: List[FaceGroup]

class SearchResults(BaseModel):
    query: str
    total: int
    results: List[ImageResult]
