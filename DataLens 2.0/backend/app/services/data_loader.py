"""Universal dataset loader with session-scoped storage and robust XLSX support.

CSV files are read with pandas. XLSX workbooks are inspected sheet-by-sheet and
DataLens automatically chooses the most useful non-empty sheet instead of blindly
using Excel's first tab (which is often a title, questions, or empty sheet).
""" 
from __future__ import annotations
import csv
import logging
from io import BytesIO
from pathlib import Path
import pandas as pd
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import DataLensError, InvalidFileContentError
from app.models.dataset import DatasetRecord
from app.schemas.dataset import DatasetSummary, UploadError, UploadResponse
from app.utils import file_utils, validation

logger = logging.getLogger(__name__)
_DATASETS: dict[str, DatasetRecord] = {}
_ACTIVE_FRAMES: dict[str, pd.DataFrame] = {}
def _excel_sheet_inventory(path_or_buffer) -> list[dict]:
    """Return lightweight metadata for every workbook sheet.

    Reading only headers/metadata keeps upload validation cheap while still
    allowing us to skip empty/title sheets. Each entry is safe for JSON/UI use.
    """
    try:
        xl = pd.ExcelFile(path_or_buffer, engine="openpyxl")
        inventory = []
        for sheet in xl.sheet_names:
            try:
                sample = pd.read_excel(xl, sheet_name=sheet, nrows=5, engine="openpyxl")
                # A sheet can have formatting but no real cells.
                nonempty = int(sample.notna().any(axis=1).sum()) if not sample.empty else 0
                cols = int(sample.shape[1])
                inventory.append({"name": str(sheet), "columns": cols, "sample_rows": nonempty})
            except Exception:
                inventory.append({"name": str(sheet), "columns": 0, "sample_rows": 0})
        return inventory
    except Exception as exc:
        raise InvalidFileContentError("Could not inspect the Excel workbook. Make sure it is a valid .xlsx file.") from exc


def _select_best_sheet(path_or_buffer) -> tuple[str, list[str]]:
    """Select the most data-rich sheet, preferring real tabular sheets."""
    try:
        xl = pd.ExcelFile(path_or_buffer, engine="openpyxl")
        candidates = []
        for order, sheet in enumerate(xl.sheet_names):
            try:
                df = pd.read_excel(xl, sheet_name=sheet, engine="openpyxl")
                rows, cols = int(len(df)), int(len(df.columns))
                nonempty_cells = int(df.notna().sum().sum()) if rows and cols else 0
                # Score by actual populated cells, then rows/columns. This makes
                # an empty "Questions" tab lose to the 300x20 data tab.
                candidates.append((nonempty_cells, rows, cols, -order, str(sheet)))
            except Exception:
                continue
        if not candidates:
            raise InvalidFileContentError("The Excel workbook has no readable worksheets.")
        candidates.sort(reverse=True)
        selected = candidates[0][-1]
        return selected, [str(x) for x in xl.sheet_names]
    except InvalidFileContentError:
        raise
    except Exception as exc:
        raise InvalidFileContentError("Could not inspect the Excel workbook. Make sure it is a valid .xlsx file.") from exc


def _make_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make duplicate headers safe without dropping any user data.

    Pandas permits duplicate labels, but many DataFrame operations then return
    a DataFrame where a Series is expected. That can make an otherwise valid
    CSV/XLSX crash deep profiling. We preserve every column and only disambiguate
    repeated display names as ``name [2]``, ``name [3]``, etc.
    """
    seen: dict[str, int] = {}
    new_columns: list[str] = []
    for raw in df.columns:
        name = str(raw).strip() if str(raw).strip() else f"Unnamed: {len(new_columns)}"
        count = seen.get(name, 0) + 1
        seen[name] = count
        new_columns.append(name if count == 1 else f"{name} [{count}]")
    out = df.copy()
    out.columns = new_columns
    return out


def _detect_csv_delimiter(sample: bytes) -> str:
    text = sample.decode("utf-8-sig", errors="ignore")
    try:
        dialect = csv.Sniffer().sniff(text[:10000], delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def _read_csv_robust(path: Path) -> pd.DataFrame:
    """Read common CSV variants without requiring a dataset-specific schema."""
    last_error: Exception | None = None
    sample = path.read_bytes()[:100_000]
    delimiter = _detect_csv_delimiter(sample)
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return _make_unique_columns(pd.read_csv(
                path, sep=delimiter, encoding=encoding, low_memory=False,
                on_bad_lines="error",
            ))
        except (UnicodeDecodeError, pd.errors.ParserError, LookupError) as exc:
            last_error = exc
    # Last-resort parser: keep the dataset usable rather than turning a
    # recoverable malformed row into a server error. Pandas reports skipped
    # physical lines to the backend log.
    try:
        return _make_unique_columns(pd.read_csv(
            path, sep=delimiter, encoding="latin1", engine="python",
            on_bad_lines="warn",
        ))
    except Exception as exc:
        raise InvalidFileContentError(
            "Could not parse this CSV. Check the delimiter, quoting, and row structure."
        ) from (last_error or exc)


def _read_excel_robust(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    selected = sheet_name
    if not selected:
        selected, _ = _select_best_sheet(path)
    try:
        df = pd.read_excel(path, sheet_name=selected, engine="openpyxl")
        return _make_unique_columns(df)
    except Exception as exc:
        raise InvalidFileContentError(
            f"Could not read worksheet '{selected}'. Make sure the workbook is not corrupt."
        ) from exc


def get_dataset(dataset_id: str) -> DatasetRecord | None:
    return _DATASETS.get(dataset_id)


def list_datasets() -> list[DatasetRecord]:
    return list(reversed(list(_DATASETS.values())))


def get_excel_sheets(record: DatasetRecord) -> list[str]:
    if record.format != "xlsx":
        return []
    try:
        return [x["name"] for x in _excel_sheet_inventory(record.path)]
    except InvalidFileContentError:
        return []


def read_dataframe(record: DatasetRecord, sheet_name: str | None = None) -> pd.DataFrame:
    if record.id in _ACTIVE_FRAMES and sheet_name is None:
        return _ACTIVE_FRAMES[record.id].copy()
    if record.format == "csv":
        return _read_csv_robust(record.path)
    selected = sheet_name or record.sheet_name
    if not selected:
        selected, _ = _select_best_sheet(record.path)
        record.sheet_name = selected
    return _read_excel_robust(record.path, selected)


def set_active_dataframe(dataset_id: str, df: pd.DataFrame) -> None:
    _ACTIVE_FRAMES[dataset_id] = df.copy()


def reset_active_dataframe(dataset_id: str) -> None:
    _ACTIVE_FRAMES.pop(dataset_id, None)


def delete_dataset(dataset_id: str) -> bool:
    """Delete one dataset from the current session and remove its stored file."""
    record = _DATASETS.pop(dataset_id, None)
    _ACTIVE_FRAMES.pop(dataset_id, None)
    if record is None:
        return False
    try:
        record.path.unlink(missing_ok=True)
    except OSError:
        logger.warning("Could not remove stored dataset file %s", record.path)
    return True


def clear_datasets() -> int:
    """Clear every dataset in the current session and remove stored raw files."""
    ids = list(_DATASETS.keys())
    for dataset_id in ids:
        delete_dataset(dataset_id)
    _DATASETS.clear()
    _ACTIVE_FRAMES.clear()
    return len(ids)


def _check_readable(content: bytes, extension: str) -> str | None:
    try:
        if extension == "csv":
            sample = content[:100_000]
            delimiter = _detect_csv_delimiter(sample)
            last_error: Exception | None = None
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
                try:
                    pd.read_csv(
                        BytesIO(content), sep=delimiter, encoding=encoding,
                        nrows=10, low_memory=False, on_bad_lines="error",
                    )
                    return None
                except (UnicodeDecodeError, pd.errors.ParserError, LookupError) as exc:
                    last_error = exc
            pd.read_csv(
                BytesIO(content), sep=delimiter, encoding="latin1",
                nrows=10, engine="python", on_bad_lines="warn",
            )
            return None
        selected, _ = _select_best_sheet(BytesIO(content))
        return selected
    except Exception as exc:
        raise InvalidFileContentError(
            "Could not read this file as a valid dataset. Please check the file format and Excel worksheets."
        ) from exc


async def _process_one(file: UploadFile) -> DatasetSummary:
    extension = validation.validate_extension(file.filename)
    content = await file.read()
    validation.validate_not_empty(content)
    validation.validate_size(content)
    selected_sheet = _check_readable(content, extension)
    dataset_id = file_utils.generate_dataset_id()
    stored_path = file_utils.save_upload(content, dataset_id, extension)
    record = DatasetRecord(
        id=dataset_id, filename=file.filename or "dataset", format=extension,
        size=len(content), status="uploaded", path=stored_path, sheet_name=selected_sheet,
    )
    _DATASETS[dataset_id] = record
    return DatasetSummary(
        id=record.id, filename=record.filename, format=record.format,
        size=record.size, status=record.status, sheet_name=record.sheet_name,
    )


async def process_upload(files: list[UploadFile]) -> UploadResponse:
    uploaded, errors = [], []
    for file in files:
        filename = file.filename or "unknown"
        try:
            uploaded.append(await _process_one(file))
        except DataLensError as exc:
            errors.append(UploadError(filename=filename, error=str(exc)))
        except Exception:
            logger.exception("Unexpected error while uploading %s", filename)
            errors.append(UploadError(filename=filename, error="Something went wrong while uploading the dataset. Please try again."))
    return UploadResponse(uploaded=uploaded, errors=errors)


