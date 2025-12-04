"""Схемы для API."""
from backend.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatusResponse,
    TaskListResponse,
)
from backend.schemas.errors import (
    ErrorResponse,
    NotFoundErrorResponse,
    BadRequestErrorResponse,
    InternalServerErrorResponse,
    ValidationErrorResponse,
)
from backend.schemas.filters import (
    TaskFilterQueryParams,
    TaskFilterDepends,
)

__all__ = [
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskStatusResponse",
    "TaskListResponse",
    "ErrorResponse",
    "NotFoundErrorResponse",
    "BadRequestErrorResponse",
    "InternalServerErrorResponse",
    "ValidationErrorResponse",
    "TaskFilterQueryParams",
    "TaskFilterDepends",
]

