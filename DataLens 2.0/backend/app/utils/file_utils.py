"""Shared filesystem helpers for dataset/output storage.

Every stored filename is derived from a generated dataset id, never
from the client-supplied filename. This is what actually prevents
path traversal and filename collisions — see save_upload().
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.core.config import settings

# Only used to pull a clean extension out of the original filename —
# the rest of the client-supplied name is discarded, not sanitized.
_EXTENSION_RE = re.compile(r"[^a-z0-9]+")


def generate_dataset_id() -> str:
    """A short, URL-safe, unique id for one uploaded dataset."""
    return uuid.uuid4().hex


def sanitize_extension(filename: str) -> str:
    """Return a lowercase, alphanumeric-only extension (no leading dot)."""
    suffix = Path(filename or "").suffix.lower().lstrip(".")
    return _EXTENSION_RE.sub("", suffix)


def get_raw_dir() -> Path:
    """Resolve (and ensure) the datasets/raw directory from settings."""
    raw_dir = Path(settings.datasets_raw_dir).resolve()
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir


def save_upload(content: bytes, dataset_id: str, extension: str) -> Path:
    """Write raw upload bytes to datasets/raw under a generated filename.

    The stored filename is always f"{dataset_id}.{extension}" — fully
    generated server-side, so a malicious original filename (e.g.
    "../../etc/passwd") never influences where the file lands, and two
    uploads with the same original filename never collide.
    """
    raw_dir = get_raw_dir()
    stored_name = f"{dataset_id}.{extension}"
    dest = (raw_dir / stored_name).resolve()

    # Defense in depth: confirm the resolved path really is inside
    # raw_dir before writing, even though stored_name is our own id.
    if raw_dir not in dest.parents:
        raise ValueError("Resolved upload path escaped the raw dataset directory.")

    dest.write_bytes(content)
    return dest
