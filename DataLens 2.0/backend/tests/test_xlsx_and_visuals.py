import io
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _workbook_bytes():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, sheet_name="Questions", index=False)
        pd.DataFrame({"Category": ["A", "B", "A"], "Sales": [10, 20, 30]}).to_excel(writer, sheet_name="Data", index=False)
    return buf.getvalue()


def test_xlsx_chooses_best_nonempty_sheet():
    response = client.post("/api/upload", files=[("files", ("book.xlsx", io.BytesIO(_workbook_bytes()), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))])
    assert response.status_code == 200
    item = response.json()["uploaded"][0]
    assert item["sheet_name"] == "Data"

    profile = client.get(f"/api/datasets/{item['id']}/profile")
    assert profile.status_code == 200
    assert profile.json()["rows"] == 3
    assert profile.json()["columns"] == 2
    assert "Questions" in profile.json()["available_sheets"]


def test_matplotlib_visualization_endpoint_returns_png():
    response = client.post("/api/upload", files=[("files", ("plot.csv", io.BytesIO(b"Category,Sales\\nA,10\\nB,20\\nA,30\\n"), "text/csv"))])
    dataset_id = response.json()["uploaded"][0]["id"]
    image = client.get(f"/api/visualization/plot?dataset_id={dataset_id}&chart_type=bar")
    assert image.status_code == 200
    assert image.headers["content-type"].startswith("image/png")
    assert len(image.content) > 1000


def test_csv_with_bad_physical_row_is_recovered_without_profile_crash(tmp_path: Path):
    path = tmp_path / "messy.csv"
    path.write_text("A,B,Category\n1,10,A\n2,20,B,EXTRA\n3,30,A\n", encoding="utf-8")
    record = __import__("app.models.dataset", fromlist=["DatasetRecord"]).DatasetRecord(
        id="messy", filename="messy.csv", format="csv", size=path.stat().st_size,
        status="uploaded", path=path,
    )
    from app.services.data_profiler import profile_dataset
    profile = profile_dataset(record)
    assert profile.rows >= 2
    assert profile.columns == 3


def test_duplicate_headers_are_kept_and_safe(tmp_path: Path):
    path = tmp_path / "duplicate.csv"
    path.write_text("Score,Score,Name\n10,20,A\n30,40,B\n", encoding="utf-8")
    record = __import__("app.models.dataset", fromlist=["DatasetRecord"]).DatasetRecord(
        id="duplicate", filename="duplicate.csv", format="csv", size=path.stat().st_size,
        status="uploaded", path=path,
    )
    from app.services.data_profiler import profile_dataset
    profile = profile_dataset(record)
    assert profile.columns == 3
    assert len({c.name for c in profile.column_profiles}) == 3
