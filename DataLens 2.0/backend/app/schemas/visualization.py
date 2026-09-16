from pydantic import BaseModel

class ChartRequest(BaseModel):
    dataset_id: str
    chart_type: str = "bar"
    x: str | None = None
    y: str | None = None
    z: str | None = None
