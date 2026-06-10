import os
from typing import List
from sentence_transformers import SentenceTransformer, util
from PIL import Image

class CategoryService:
    categories = {
        "documents": "a photograph of a document, paper, receipt, or form",
        "prescriptions": "a prescription label or pharmacy form",
        "receipts": "a receipt or purchase slip",
        "people": "portraits or selfies with people",
        "travel": "travel photography, landscapes, and landmarks",
        "pets": "pets or animals in the photo",
        "other": "other general photos",
    }

    def __init__(self):
        self.model = SentenceTransformer("clip-ViT-B-32")
        self.category_prompts = list(self.categories.values())
        self.category_keys = list(self.categories.keys())
        self.category_embeddings = self.model.encode(self.category_prompts, convert_to_tensor=True)

    def assign_categories(self, image: Image.Image, path: str) -> List[str]:
        tags = self._filename_tags(path)
        if any(term in path.lower() for term in ["receipt", "bill", "invoice"]):
            return ["receipts"]
        if any(term in path.lower() for term in ["prescription", "rx"]):
            return ["prescriptions"]

        image_embedding = self.model.encode(image, convert_to_tensor=True)
        scores = util.cos_sim(image_embedding, self.category_embeddings)[0]
        ranked = sorted(
            zip(self.category_keys, scores.tolist()), key=lambda item: item[1], reverse=True
        )
        top_category = ranked[0][0]
        categories = [top_category]
        if top_category == "other" and tags:
            categories.extend(tags)
        return categories

    def _filename_tags(self, path: str) -> List[str]:
        base = os.path.basename(path).lower()
        tags = []
        if "pet" in base or "dog" in base or "cat" in base:
            tags.append("pets")
        if "trip" in base or "vacation" in base or "travel" in base:
            tags.append("travel")
        if "document" in base or "doc" in base:
            tags.append("documents")
        return tags
