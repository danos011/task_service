"""Обработчики исключений для API."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.exceptions import (
    TaskNotFoundError,
    TaskCannotBeCancelledError,
    TaskServiceError,
)


async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    """Обработчик для TaskNotFoundError."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def task_cannot_be_cancelled_handler(
    request: Request,
    exc: TaskCannotBeCancelledError,
) -> JSONResponse:
    """Обработчик для TaskCannotBeCancelledError."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def task_service_error_handler(
    request: Request,
    exc: TaskServiceError,
) -> JSONResponse:
    """Обработчик для общих ошибок TaskServiceError."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрирует все обработчики исключений в приложении FastAPI.
    
    Args:
        app: Экземпляр приложения FastAPI
    """
    app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
    app.add_exception_handler(TaskCannotBeCancelledError, task_cannot_be_cancelled_handler)
    app.add_exception_handler(TaskServiceError, task_service_error_handler)

