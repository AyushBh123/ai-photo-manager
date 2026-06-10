from typing import List
import face_recognition
from app.models import ImageRecord

class FaceGroupingService:
    def __init__(self, threshold: float = 0.55):
        self.threshold = threshold

    def detect_face_encodings(self, image_path: str) -> List[List[float]]:
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            return [encoding.tolist() for encoding in encodings]
        except Exception:
            return []

    def build_groups(self, records: List[ImageRecord]) -> List[dict]:
        groups = []
        representatives = []
        for record in records:
            for encoding in record.face_encodings or []:
                assigned = False
                for i, rep in enumerate(representatives):
                    distances = face_recognition.face_distance([rep], encoding)
                    if distances[0] <= self.threshold:
                        groups[i]["image_ids"].append(record.id)
                        assigned = True
                        break
                if not assigned:
                    representatives.append(encoding)
                    groups.append({"face_id": f"face_{len(groups) + 1}", "image_ids": [record.id]})
        return groups
