from fastapi import APIRouter
from app.core.exceptions import DatasetNotFoundError
from app.schemas.cleaning import CleaningRequest
from app.services import data_cleaner
router=APIRouter(prefix="/cleaning",tags=["cleaning"])
@router.post("/preview")
def preview(req:CleaningRequest):
    result=data_cleaner.preview(req.dataset_id,req.operation,req.column,req.value)
    if result is None: raise DatasetNotFoundError(f"No dataset found with id '{req.dataset_id}'.")
    return result
@router.post("/apply")
def apply(req:CleaningRequest):
    result=data_cleaner.apply(req.dataset_id,req.operation,req.column,req.value)
    if result is None: raise DatasetNotFoundError(f"No dataset found with id '{req.dataset_id}'.")
    return result
