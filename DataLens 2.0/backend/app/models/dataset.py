"""Domain model for an uploaded dataset."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DatasetRecord:
    id: str
    filename: str
    format: str  # csv | xlsx
    size: int
    status: str
    path: Path
    # For workbooks, the best non-empty sheet is selected automatically.
    # A default keeps backwards compatibility with existing tests/records.
    sheet_name: str | None = None
