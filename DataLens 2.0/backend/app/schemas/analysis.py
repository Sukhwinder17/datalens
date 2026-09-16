from pydantic import BaseModel
class AnalysisRequest(BaseModel):
    dataset_id: str
