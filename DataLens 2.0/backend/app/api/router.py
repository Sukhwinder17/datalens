"""Central API router — aggregates every route module under /api.

Keeps main.py free of route wiring. Add a new feature's router here,
not directly in main.py.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    analysis,
    cleaning,
    comparison,
    datasets,
    export,
    insights,
    upload,
    visualization,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(upload.router)
api_router.include_router(datasets.router)
api_router.include_router(cleaning.router)
api_router.include_router(analysis.router)
api_router.include_router(visualization.router)
api_router.include_router(comparison.router)
api_router.include_router(insights.router)
api_router.include_router(export.router)
