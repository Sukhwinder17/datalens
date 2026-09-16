"""Shared input validation helpers.

Phase 1 only needs upload-time checks (extension, empty, size). These
are deliberately pandas-free — the "is this actually readable tabular
data" check lives in the DataLoader service, since that's where pandas
is used to read files.
"""

from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import EmptyFileError, FileTooLargeError, UnsupportedFileTypeError
from app.utils.file_utils import sanitize_extension


def validate_extension(filename: str) -> str:
    """Return the file's extension if it's an allowed type, else raise."""
    extension = sanitize_extension(filename)
    if extension not in settings.allowed_upload_extensions:
        raise UnsupportedFileTypeError(
            "Unsupported file type. Please upload CSV or XLSX files."
        )
    return extension


def validate_not_empty(content: bytes) -> None:
    if len(content) == 0:
        raise EmptyFileError("This file appears to be empty.")


def validate_size(content: bytes) -> None:
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise FileTooLargeError(
            f"File exceeds the {settings.max_upload_size_mb}MB upload limit."
        )
