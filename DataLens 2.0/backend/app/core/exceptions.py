"""Application-level exceptions.

TODO: Add a FastAPI exception handler (in app/main.py) that maps these
to consistent JSON error responses once routes have real logic.
"""

from __future__ import annotations


class DataLensError(Exception):
    """Base class for all DataLens application errors."""


class DatasetNotFoundError(DataLensError):
    """Raised when a referenced dataset/session does not exist."""


class UnsupportedFileTypeError(DataLensError):
    """Raised when an uploaded file is not CSV/XLSX."""


class EmptyFileError(DataLensError):
    """Raised when an uploaded file has no content."""


class FileTooLargeError(DataLensError):
    """Raised when an uploaded file exceeds the configured size limit."""


class InvalidFileContentError(DataLensError):
    """Raised when a file has an allowed extension but isn't readable as tabular data."""


class InvalidOperationError(DataLensError):
    """Raised when a cleaning/transform operation is malformed."""
