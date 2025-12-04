"""Схемы для ошибок API."""
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Базовая схема ошибки."""
    detail: str = Field(..., description="Описание ошибки")


class NotFoundErrorResponse(ErrorResponse):
    """Схема ошибки 404 - ресурс не найден."""
    pass


class BadRequestErrorResponse(ErrorResponse):
    """Схема ошибки 400 - некорректный запрос."""
    pass


class ValidationErrorResponse(BaseModel):
    """Схема ошибки 422 - ошибка валидации."""
    detail: list[dict] = Field(..., description="Список ошибок валидации")


class InternalServerErrorResponse(ErrorResponse):
    """Схема ошибки 500 - внутренняя ошибка сервера."""
    pass


