from typing import List
import torch
from sentence_transformers import SentenceTransformer, util
from app.models import ImageRecord

class SearchService:
    def __init__(self):
        self.model = SentenceTransformer("clip-ViT-B-32")

    def search(self, query: str, records: List[ImageRecord], top_n: int = 20) -> List[ImageRecord]:
        if not records:
            return []

        query_embedding = self.model.encode(query, convert_to_tensor=True)
        candidates = [record for record in records if record.embedding]
        if not candidates:
            return []

        tensor_embeddings = torch.tensor(
            [record.embedding for record in candidates],
            device=query_embedding.device,
        )
        scores = util.cos_sim(query_embedding, tensor_embeddings)[0].tolist()
        ranked = sorted(zip(candidates, scores), key=lambda item: item[1], reverse=True)
        return [record for record, _ in ranked[:top_n]]
