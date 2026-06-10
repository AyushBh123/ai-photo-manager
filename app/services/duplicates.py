from collections import defaultdict
from typing import List
from app.models import ImageRecord

class DuplicateDetector:
    def __init__(self, near_threshold: int = 10):
        self.near_threshold = near_threshold
        self.hash_groups: dict[str, List[ImageRecord]] = defaultdict(list)
        self.phash_groups: dict[str, List[ImageRecord]] = defaultdict(list)

    def register(self, record: ImageRecord):
        self.hash_groups[record.hash].append(record)
        self.phash_groups[record.phash].append(record)

    def find_exact_duplicates(self):
        return [group for group in self.hash_groups.values() if len(group) > 1]

    def find_near_duplicates(self):
        clusters = []
        visited = set()

        def hamming_distance(a: str, b: str) -> int:
            return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))

        for records in self.phash_groups.values():
            for first in records:
                if first.id in visited:
                    continue
                cluster = [first]
                visited.add(first.id)
                for second in records:
                    if second.id in visited:
                        continue
                    if hamming_distance(first.phash, second.phash) <= self.near_threshold:
                        cluster.append(second)
                        visited.add(second.id)
                if len(cluster) > 1:
                    clusters.append(cluster)
        return clusters

    def summarize(self):
        results = []
        for exact in self.find_exact_duplicates():
            results.append({"reason": "exact", "images": exact})
        for near in self.find_near_duplicates():
            results.append({"reason": "near", "images": near})
        return results
