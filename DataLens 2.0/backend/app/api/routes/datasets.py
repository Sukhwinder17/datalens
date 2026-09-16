"""Dataset listing, profiling, and read-only preview routes."""
from __future__ import annotations
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.core.exceptions import DatasetNotFoundError
from app.schemas.dataset import DatasetPreview, DatasetProfile, DatasetSummary
from app.services import data_loader, data_profiler
from app.services.profile_visuals import make_plot

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.delete("/session")
def clear_dataset_session() -> dict:
    """Remove all uploaded datasets from the current DataLens session."""
    count = data_loader.clear_datasets()
    return {"deleted": count, "message": "Dataset session cleared."}


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str) -> dict:
    """Remove one uploaded dataset from the current session."""
    if not data_loader.delete_dataset(dataset_id):
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return {"deleted": 1, "dataset_id": dataset_id}

@router.get("", response_model=list[DatasetSummary])
def list_datasets() -> list[DatasetSummary]:
    return [DatasetSummary(
        id=r.id, filename=r.filename, format=r.format, size=r.size,
        status=r.status, sheet_name=r.sheet_name
    ) for r in data_loader.list_datasets()]

@router.get("/{dataset_id}/sheets")
def get_dataset_sheets(dataset_id: str) -> dict:
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return {
        "dataset_id": dataset_id,
        "format": record.format,
        "selected_sheet": record.sheet_name,
        "sheets": data_loader.get_excel_sheets(record),
    }


@router.get("/{dataset_id}/profile", response_model=DatasetProfile)
def get_dataset_profile(dataset_id: str) -> DatasetProfile:
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return data_profiler.profile_dataset(record)

@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
def get_dataset_preview(dataset_id: str, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)) -> DatasetPreview:
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return data_profiler.get_dataset_preview(record, page=page, page_size=page_size)


@router.get("/{dataset_id}/problem-rows")
def get_problem_rows(dataset_id: str, limit: int = Query(100, ge=1, le=500)) -> dict:
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return {"dataset_id": dataset_id, "rows": data_profiler.get_problem_rows(record, limit=limit)}


@router.get("/{dataset_id}/plot")
def get_profile_plot(
    dataset_id: str,
    plot_type: str = Query(..., pattern="^(missing|heatmap|correlation|histogram|boxplot|category|frequency)$"),
    column: str | None = Query(None),
    top_n: int = Query(20, ge=5, le=50),
):
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    try:
        image = make_plot(record, plot_type, column, top_n)
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StreamingResponse(image, media_type="image/png", headers={"Cache-Control": "no-store"})
