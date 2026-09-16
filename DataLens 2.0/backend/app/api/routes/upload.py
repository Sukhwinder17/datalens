"""Routes for uploading datasets (CSV/XLSX).

Thin by design — all parsing/validation/storage logic lives in
app/services/data_loader.py.
"""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.dataset import UploadResponse
from app.services import data_loader

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_datasets(files: list[UploadFile] = File(...)) -> UploadResponse:
    """Accept one or more CSV/XLSX files and store them under datasets/raw.

    Per-file errors (wrong type, empty, unreadable, too large) are
    collected in the response's `errors` list rather than failing the
    whole request — the other files in the batch still upload.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")
    return await data_loader.process_upload(files)
