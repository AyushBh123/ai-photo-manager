# Design Decisions

## Language and Framework

Python with FastAPI was selected for rapid API delivery, strong typing, and good support for asynchronous endpoints.

## Search and AI

The solution uses the `sentence-transformers` CLIP model for both category classification and natural language search. This enables image-text similarity without requiring a separate expensive model for each feature.

## Duplicate Detection

Exact duplicates are identified using `imagehash.phash`. Near-duplicates are discovered by comparing perceptual hashes with a small Hamming distance threshold.

## Face Grouping

Face detection and encoding are handled by `face_recognition`. Faces are clustered by distance threshold to group similar individuals.

## Google Photos Integration

A separate connector service handles OAuth, token persistence, and media item enumeration to keep API logic decoupled from Google Photos access.

## Assignment Scope

The implementation stays focused on the required capabilities: Google Photos and local ingestion, duplicate detection, category tagging, face grouping, natural language search, Docker deployment, and automated tests. Extra product features were intentionally omitted so the repository matches the problem statement closely.
