"""Routes for exporting cleaned datasets / reports / charts.

TODO: Export cleaned data as CSV/XLSX, export reports, export chart
images, writing into the outputs/ directory tree.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/export", tags=["export"])

# TODO: implement GET/POST /api/export
