"""Tests for the /api/upload routes."""

from __future__ import annotations

import io

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CSV_BYTES = b"name,age\nAlice,30\nBob,25\n"


def _xlsx_bytes() -> bytes:
    buf = io.BytesIO()
    pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_excel(buf, index=False)
    return buf.getvalue()


def test_health_check_still_works():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_single_csv():
    files = [("files", ("sales.csv", io.BytesIO(CSV_BYTES), "text/csv"))]
    response = client.post("/api/upload", files=files)
    body = response.json()

    assert response.status_code == 200
    assert body["errors"] == []
    assert len(body["uploaded"]) == 1
    assert body["uploaded"][0]["filename"] == "sales.csv"
    assert body["uploaded"][0]["format"] == "csv"
    assert body["uploaded"][0]["status"] == "uploaded"
    assert body["uploaded"][0]["id"]


def test_upload_multiple_csv_and_xlsx_together():
    files = [
        ("files", ("customers.csv", io.BytesIO(CSV_BYTES), "text/csv")),
        (
            "files",
            (
                "products.xlsx",
                io.BytesIO(_xlsx_bytes()),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        ),
    ]
    response = client.post("/api/upload", files=files)
    body = response.json()

    assert response.status_code == 200
    assert len(body["uploaded"]) == 2
    assert {d["format"] for d in body["uploaded"]} == {"csv", "xlsx"}


def test_unsupported_file_type_is_rejected():
    files = [("files", ("malware.exe", io.BytesIO(b"junk"), "application/octet-stream"))]
    response = client.post("/api/upload", files=files)
    body = response.json()

    assert response.status_code == 200
    assert body["uploaded"] == []
    assert "Unsupported file type" in body["errors"][0]["error"]


def test_empty_file_is_rejected():
    files = [("files", ("empty.csv", io.BytesIO(b""), "text/csv"))]
    response = client.post("/api/upload", files=files)
    body = response.json()

    assert body["uploaded"] == []
    assert "empty" in body["errors"][0]["error"].lower()


def test_duplicate_filenames_get_distinct_ids_and_do_not_overwrite():
    files_a = [("files", ("dup.csv", io.BytesIO(CSV_BYTES), "text/csv"))]
    files_b = [("files", ("dup.csv", io.BytesIO(CSV_BYTES), "text/csv"))]

    response_a = client.post("/api/upload", files=files_a)
    response_b = client.post("/api/upload", files=files_b)

    id_a = response_a.json()["uploaded"][0]["id"]
    id_b = response_b.json()["uploaded"][0]["id"]

    assert id_a != id_b


def test_no_files_field_returns_422():
    # FastAPI's own request validation rejects this before our route
    # code runs, since `files` is a required field.
    response = client.post("/api/upload")
    assert response.status_code == 422
