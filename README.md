# AI Photo Manager

A Python FastAPI-based AI photo management platform for local and Google Photos image indexing, duplicate detection, category tagging, face grouping, and natural language search.

## Features

- Connects to Google Photos and local storage directories
- Supports exact and near-duplicate image detection
- Categorizes images into `documents`, `prescriptions`, `receipts`, `people`, `travel`, `pets`, and `other`
- Groups faces into person-based clusters
- Supports natural language search over indexed images
- Provides a browser-based demo and REST API
- Includes Docker deployment and automated tests

## Quick Start

1. Create and activate a Python 3.11 virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   python -m pip install --upgrade pip 'setuptools<82' wheel
   python -m pip install -r requirements.txt
   ```

3. Start the application locally:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Or use the helper script to clear port 8000 and launch the app:
   ```bash
   ./run.sh
   ```

5. Open the website in a browser:
   ```text
   http://127.0.0.1:8000
   ```

6. Open the interactive API docs:
   ```text
   http://127.0.0.1:8000/docs
   ```

## Docker

Build and run the container:
```bash
docker build -t ai-photo-manager .
docker run --rm -p 8000:8000 ai-photo-manager
```

Or with Compose:
```bash
docker compose up --build
```

## API Endpoints

- `GET /health` – application health and indexed image count
- `POST /scan/local` – scan one or more local folders
- `POST /connect/google-photos` – connect and sync Google Photos
- `GET /images` – list indexed images
- `GET /duplicates` – view duplicate and near-duplicate groups
- `GET /face-groups` – view face clusters
- `POST /search` – natural language search

## Assignment Scope

This repository is scoped to the assignment requirements only. It focuses on photo ingestion, AI analysis, search, and deployment readiness rather than unrelated product features.

The application serves a static frontend from `/static` and the root path `/` so the required flows can be exercised from the browser.

## Google Photos Setup

1. Create OAuth credentials in Google Cloud Console for the Photos Library API.
2. Save the OAuth client secret JSON to `data/client_secret.json`.
3. Open the web UI at `http://127.0.0.1:8000`, use the Google Photos card, and click **Sync Google Photos**.
4. On the first run, the app will prompt for console authorization and write a token file to `data/google_photos_token.json`.
5. You can also call `POST /connect/google-photos` directly with a JSON payload such as:
   ```json
   {
     "client_secrets_path": "data/client_secret.json",
     "token_path": "data/google_photos_token.json"
   }
   ```

## Project Documentation

- `docs/architecture.md` – architecture overview and system diagram
- `docs/design_decisions.md` – reasoning behind framework, search, duplicate detection, and face grouping choices
- `postman_collection.json` – API requests collection for review and manual testing

## Submission Checklist

- [x] Google Photos and local folder ingestion
- [x] Duplicate and near-duplicate detection
- [x] Document, receipt, prescription, travel, people, pets, and other categories
- [x] Face grouping
- [x] Natural language search
- [x] Docker support with `Dockerfile` and `docker-compose.yml`
- [x] Automated tests available and passing
- [x] Architecture and design docs included
- [x] Postman collection included
- [ ] Walkthrough video to be recorded and shared

## Tests

Run tests with:
```bash
pytest
```
