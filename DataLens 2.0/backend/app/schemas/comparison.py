from pydantic import BaseModel
class ComparisonRequest(BaseModel):
    dataset_ids: list[str]
