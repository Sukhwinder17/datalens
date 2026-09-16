from pydantic import BaseModel
class CleaningRequest(BaseModel):
    dataset_id: str
    operation: str
    column: str | None = None
    value: str | float | int | None = None
