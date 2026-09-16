"""Tests for GET /api/datasets and GET /api/datasets/{id}/profile."""

from __future__ import annotations

import io

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services import data_loader

client = TestClient(app)


def _upload_csv(content: bytes, filename: str = "data.csv") -> str:
    files = [("files", (filename, io.BytesIO(content), "text/csv"))]
    response = client.post("/api/upload", files=files)
    return response.json()["uploaded"][0]["id"]


def _upload_xlsx(df: pd.DataFrame, filename: str = "data.xlsx") -> str:
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    files = [
        (
            "files",
            (
                filename,
                io.BytesIO(buf.getvalue()),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        )
    ]
    response = client.post("/api/upload", files=files)
    return response.json()["uploaded"][0]["id"]


def test_profile_valid_csv():
    dataset_id = _upload_csv(b"name,age\nAlice,30\nBob,25\nCarol,40\n")

    response = client.get(f"/api/datasets/{dataset_id}/profile")
    body = response.json()

    assert response.status_code == 200
    assert body["dataset_id"] == dataset_id
    assert body["rows"] == 3
    assert body["columns"] == 2


def test_profile_valid_xlsx():
    df = pd.DataFrame({"product": ["A", "B", "C"], "price": [10.5, 20.0, 15.25]})
    dataset_id = _upload_xlsx(df)

    response = client.get(f"/api/datasets/{dataset_id}/profile")
    body = response.json()

    assert response.status_code == 200
    assert body["rows"] == 3
    assert body["columns"] == 2


def test_profile_dataset_with_missing_values():
    dataset_id = _upload_csv(b"name,age\nAlice,30\nBob,\n,25\n")

    body = client.get(f"/api/datasets/{dataset_id}/profile").json()

    assert body["missing_data"]["total_missing"] >= 2
    assert body["missing_data"]["missing_percentage"] > 0


def test_profile_dataset_with_duplicate_rows():
    dataset_id = _upload_csv(b"name,age\nAlice,30\nAlice,30\nBob,25\n")

    body = client.get(f"/api/datasets/{dataset_id}/profile").json()

    assert body["duplicates"]["duplicate_rows"] == 1
    assert body["duplicates"]["duplicate_percentage"] > 0


def test_profile_numerical_columns_include_statistics():
    dataset_id = _upload_csv(b"score\n1\n2\n3\n4\n5\n")

    body = client.get(f"/api/datasets/{dataset_id}/profile").json()
    score_col = next(c for c in body["column_profiles"] if c["name"] == "score")

    assert score_col["dtype"] == "numerical"
    assert score_col["numeric_stats"]["mean"] == 3.0
    assert score_col["numeric_stats"]["min"] == 1.0
    assert score_col["numeric_stats"]["max"] == 5.0


def test_profile_categorical_columns_include_frequency_info():
    dataset_id = _upload_csv(b"city\nDelhi\nDelhi\nMumbai\n")

    body = client.get(f"/api/datasets/{dataset_id}/profile").json()
    city_col = next(c for c in body["column_profiles"] if c["name"] == "city")

    assert city_col["dtype"] == "categorical"
    assert city_col["categorical_stats"]["top_value"] == "Delhi"
    assert city_col["categorical_stats"]["top_value_frequency"] == 2


def test_profile_datetime_column_is_detected():
    dataset_id = _upload_csv(b"joined_on\n2023-01-01\n2023-02-15\n2023-03-30\n")

    body = client.get(f"/api/datasets/{dataset_id}/profile").json()
    date_col = next(c for c in body["column_profiles"] if c["name"] == "joined_on")

    assert date_col["dtype"] == "datetime"


def test_profile_dataset_not_found_returns_404():
    response = client.get("/api/datasets/does-not-exist/profile")
    assert response.status_code == 404


def test_profile_empty_dataset_headers_only():
    dataset_id = _upload_csv(b"name,age\n")

    response = client.get(f"/api/datasets/{dataset_id}/profile")
    body = response.json()

    assert response.status_code == 200
    assert body["rows"] == 0
    assert body["missing_data"]["missing_percentage"] == 0.0


def test_profiling_does_not_modify_raw_file():
    raw_bytes = b"name,age\nAlice,30\nBob,\n"
    dataset_id = _upload_csv(raw_bytes)

    client.get(f"/api/datasets/{dataset_id}/profile")
    client.get(f"/api/datasets/{dataset_id}/profile")

    record = data_loader.get_dataset(dataset_id)
    assert record.path.read_bytes() == raw_bytes


def test_list_datasets_returns_uploaded_datasets():
    dataset_id = _upload_csv(b"a,b\n1,2\n")

    response = client.get("/api/datasets")
    body = response.json()

    assert response.status_code == 200
    assert any(d["id"] == dataset_id for d in body)
