from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.core.exceptions import DatasetNotFoundError
from app.schemas.visualization import ChartRequest
from app.services.visualization_engine import chart, make_chart_plot

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.post("")
def get_chart(req: ChartRequest):
    result = chart(req.dataset_id, req.chart_type, req.x, req.y, req.z)
    if result is None:
        raise DatasetNotFoundError(f"No dataset found with id '{req.dataset_id}'.")
    return result

@router.get("/plot")
def get_chart_plot(
    dataset_id: str = Query(...),
    chart_type: str = Query("bar", pattern="^(bar|line|area|pie|donut|scatter|histogram|boxplot|scatter3d|violin|kde|regression|countplot)$"),
    x: str | None = Query(None),
    y: str | None = Query(None),
    z: str | None = Query(None),
):
    image = make_chart_plot(dataset_id, chart_type, x, y, z)
    if image is None:
        raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return StreamingResponse(image, media_type="image/png", headers={"Cache-Control": "no-store"})
