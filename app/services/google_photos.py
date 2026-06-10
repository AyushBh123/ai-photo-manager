import json
from pathlib import Path
from typing import List
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

class GooglePhotosService:
    def __init__(self, client_secrets_path: str, token_path: str):
        self.client_secrets_path = Path(client_secrets_path)
        self.token_path = Path(token_path)
        if not self.client_secrets_path.exists():
            raise FileNotFoundError(f"Google Photos client secrets file not found: {self.client_secrets_path}")
        self.credentials = self._load_credentials()
        self.service = build("photoslibrary", "v1", credentials=self.credentials, static_discovery=False)

    def _load_credentials(self):
        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secrets_path), SCOPES)
            credentials = flow.run_console()
            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(credentials.to_json())
            return credentials

        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                with open(self.token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(credentials.to_json())
            except RefreshError as error:
                raise RuntimeError("Google Photos token refresh failed") from error
        return credentials

    def list_media_items(self, page_size: int = 100) -> List[dict]:
        items = []
        request = self.service.mediaItems().list(pageSize=page_size)
        while request is not None:
            response = request.execute()
            items.extend(response.get("mediaItems", []))
            request = self.service.mediaItems().list_next(request, response)
        return items

    def fetch_library(self) -> List[dict]:
        return self.list_media_items()

    def save_snapshot(self, output_path: str):
        content = self.fetch_library()
        Path(output_path).write_text(json.dumps(content, indent=2), encoding="utf-8")
        return output_path
