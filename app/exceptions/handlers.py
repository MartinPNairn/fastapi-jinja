from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.base import ServiceError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ServiceError)
    async def handle_service_error(request: Request, exception: ServiceError):
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error."}
        )