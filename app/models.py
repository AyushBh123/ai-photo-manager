from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ImageRecord:
    id: str
    path: str
    uri: str
    source: str
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    hash: str = ""
    phash: str = ""
    embedding: Optional[List[float]] = field(default_factory=list)
    face_encodings: Optional[List[List[float]]] = field(default_factory=list)
    face_ids: List[str] = field(default_factory=list)
    created_at: float = 0.0
    modified_at: float = 0.0
    metadata: dict = field(default_factory=dict)

    def as_dict(self):
        return {
            "id": self.id,
            "path": self.path,
            "uri": self.uri,
            "source": self.source,
            "categories": self.categories,
            "tags": self.tags,
            "hash": self.hash,
            "phash": self.phash,
            "embedding": self.embedding,
            "face_encodings": self.face_encodings,
            "face_ids": self.face_ids,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data):
        return ImageRecord(
            id=data["id"],
            path=data["path"],
            uri=data["uri"],
            source=data.get("source", "local"),
            categories=data.get("categories", []),
            tags=data.get("tags", []),
            hash=data.get("hash", ""),
            phash=data.get("phash", ""),
            embedding=data.get("embedding", []),
            face_encodings=data.get("face_encodings", []),
            face_ids=data.get("face_ids", []),
            created_at=data.get("created_at", 0.0),
            modified_at=data.get("modified_at", 0.0),
            metadata=data.get("metadata", {}),
        )
