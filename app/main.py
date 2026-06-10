from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.services.indexer import ImageIndex
from app.schemas import (
    ImageResult,
    ScanResponse,
    DuplicateGroup,
    SearchResults,
    FaceGroupResponse,
    LocalScanRequest,
    GooglePhotosSyncRequest,
    GooglePhotosSyncResult,
    SearchRequest,
    HealthResponse,
)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="AI Photo Manager",
    description="Photo indexing, duplicate detection, face grouping, category tagging, and search.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static"), html=True),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

indexer = ImageIndex(index_path="data/index.json")

@app.on_event("startup")
async def startup_event():
    indexer.load_index()

@app.get("/", response_class=FileResponse)
def homepage():
    return str(BASE_DIR / "static" / "index.html")


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "indexed_images": len(indexer.records)}

@app.post("/scan/local", response_model=ScanResponse)
def scan_local(request: LocalScanRequest):
    scanned = indexer.scan_local(request.paths)
    return {"scanned_images": scanned, "indexed_images": len(indexer.records)}

@app.post("/connect/google-photos", response_model=GooglePhotosSyncResult)
def sync_google_photos(request: GooglePhotosSyncRequest):
    try:
        scanned = indexer.sync_google_photos(request.client_secrets_path, request.token_path)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"scanned_images": scanned, "indexed_images": len(indexer.records), "source": "google_photos"}

@app.get("/images", response_model=list[ImageResult])
def list_images(limit: int = 50, offset: int = 0):
    records = list(indexer.records.values())[offset : offset + limit]
    return [ImageResult.from_record(r) for r in records]

@app.get("/duplicates", response_model=list[DuplicateGroup])
def get_duplicates():
    groups = indexer.find_duplicate_groups()
    return [DuplicateGroup.from_group(g) for g in groups]

@app.get("/face-groups", response_model=FaceGroupResponse)
def get_face_groups():
    groups = indexer.group_faces()
    return FaceGroupResponse(groups=groups)

@app.post("/search", response_model=SearchResults)
def search(request: SearchRequest):
    results = indexer.search(request.query, top_n=request.top_n)
    return SearchResults(query=request.query, total=len(results), results=[ImageResult.from_record(r) for r in results])
