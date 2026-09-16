from fastapi import APIRouter
from app.schemas.comparison import ComparisonRequest
from app.services.comparison_engine import compare
router=APIRouter(prefix="/comparison",tags=["comparison"])
@router.post("")
def compare_route(req:ComparisonRequest): return compare(req.dataset_ids)
