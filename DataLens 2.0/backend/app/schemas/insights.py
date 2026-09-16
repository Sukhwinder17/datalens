from pydantic import BaseModel
class InsightRequest(BaseModel):
    dataset_id: str
