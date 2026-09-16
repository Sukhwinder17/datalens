from fastapi import APIRouter
from app.core.exceptions import DatasetNotFoundError
from app.schemas.analysis import AnalysisRequest
from app.services.data_analyzer import analyze
router=APIRouter(prefix="/analysis",tags=["analysis"])
@router.post("")
def get_analysis(req:AnalysisRequest):
    result=analyze(req.dataset_id)
    if result is None: raise DatasetNotFoundError(f"No dataset found with id '{req.dataset_id}'.")
    return result
