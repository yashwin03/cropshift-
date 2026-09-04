"""
app/api/errors.py — A14 Global Exception Handlers and Error Envelope.

Produces exactly this shape for every error:
{
  "error": {
    "code": "FARM_NOT_FOUND",
    "message": "We could not find your farm. Please check your farm ID.",
    "details": []
  }
}
"""
from __future__ import annotations

import logging
import traceback
from typing import Any, List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("cropshift")

# ── Error code set (frozen per spec) ─────────────────────────────────────────
INVALID_FARM = "INVALID_FARM"
FARM_NOT_FOUND = "FARM_NOT_FOUND"
FARMER_NOT_FOUND = "FARMER_NOT_FOUND"
CROP_NOT_FOUND = "CROP_NOT_FOUND"
INVALID_INPUT = "INVALID_INPUT"
DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
INTERNAL_ERROR = "INTERNAL_ERROR"


def _error_envelope(code: str, message: str, details: List[Any] | None = None) -> dict:
    """Return the canonical error envelope."""
    return {"error": {"code": code, "message": message, "details": details or []}}


def _json(content: dict, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all A14 global exception handlers onto the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """422 — Pydantic request validation errors, field errors surfaced in details."""
        details = [
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
            }
            for error in exc.errors()
        ]
        logger.warning("Validation error on %s: %s", request.url, exc.errors())
        return _json(
            _error_envelope(
                INVALID_INPUT,
                "The request contains invalid or missing fields.",
                details,
            ),
            422,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """400 / 404 / other HTTP exceptions — map to appropriate error code."""
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            # Derive a specific code from detail when available
            detail_lower = str(exc.detail).lower()
            if "farm" in detail_lower and "farmer" not in detail_lower:
                code = FARM_NOT_FOUND
            elif "farmer" in detail_lower:
                code = FARMER_NOT_FOUND
            elif "crop" in detail_lower:
                code = CROP_NOT_FOUND
            else:
                code = FARM_NOT_FOUND
            http_status = status.HTTP_404_NOT_FOUND
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            code = INVALID_INPUT
            http_status = status.HTTP_400_BAD_REQUEST
        elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
            code = UNAUTHORIZED
            http_status = status.HTTP_401_UNAUTHORIZED
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            code = FORBIDDEN
            http_status = status.HTTP_403_FORBIDDEN
        else:
            code = INTERNAL_ERROR
            http_status = exc.status_code

        # Use the original detail as the safe message (already written for API consumers)
        message = str(exc.detail)
        logger.warning("HTTP %s on %s: %s", exc.status_code, request.url, exc.detail)
        return _json(_error_envelope(code, message), http_status)

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """500 — Any unexpected exception. Log full traceback; return safe message."""
        logger.error(
            "Unhandled exception on %s:\n%s", request.url, traceback.format_exc()
        )
        return _json(
            _error_envelope(
                INTERNAL_ERROR,
                "An unexpected error occurred. Please try again or contact support.",
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
