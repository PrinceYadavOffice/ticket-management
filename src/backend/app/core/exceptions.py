"""Application errors and FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict | None = None,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


def _error_response(status_code: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or {})
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields: dict[str, str] = {}
        for err in exc.errors():
            loc = err.get("loc", ())
            # Skip 'body' prefix for field paths
            parts = [str(p) for p in loc if p not in ("body", "query", "path")]
            key = ".".join(parts) if parts else "request"
            fields[key] = err.get("msg", "Invalid value")
        return _error_response(
            422,
            "VALIDATION_ERROR",
            "Request validation failed",
            {"fields": fields},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return _error_response(500, "INTERNAL_ERROR", "An unexpected error occurred")
