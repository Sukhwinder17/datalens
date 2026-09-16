from fastapi import APIRouter, Query
from app.core.exceptions import DatasetNotFoundError
from app.services.insight_engine import get_insights
router=APIRouter(prefix="/insights",tags=["insights"])
@router.get("")
def insights(dataset_id:str=Query(...)):
    result=get_insights(dataset_id)
    if result is None: raise DatasetNotFoundError(f"No dataset found with id '{dataset_id}'.")
    return result
