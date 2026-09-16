"""DataLens backend entry point.

Thin by design: app creation, middleware, and router registration
only. All real logic lives in app/services/ behind app/api/routes/.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import DataLensError, DatasetNotFoundError, InvalidFileContentError
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="DataLens API",
    description="Universal multi-dataset data preparation and analysis platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Maps our domain exceptions to HTTP status codes. Anything not listed
# here falls back to 400 — most DataLensErrors are "bad input" cases.
_ERROR_STATUS_CODES: dict[type[DataLensError], int] = {
    DatasetNotFoundError: 404,
    InvalidFileContentError: 400,
}


@app.exception_handler(DataLensError)
def handle_datalens_error(request: Request, exc: DataLensError) -> JSONResponse:
    """Turn a domain exception into a consistent JSON error response.

    Lets route handlers just raise (e.g. DatasetNotFoundError) instead
    of building HTTPException/status-code logic themselves.
    """
    status_code = _ERROR_STATUS_CODES.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Basic liveness check — used to verify the server is running."""
    return {"status": "ok", "app": "DataLens", "env": settings.app_env}
