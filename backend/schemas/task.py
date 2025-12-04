"""Pydantic схемы для задач."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.models import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Базовая схема задачи."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Схема для создания задачи."""
    pass


class TaskUpdate(BaseModel):
    """Схема для обновления задачи."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(TaskBase):
    """Схема ответа с информацией о задаче."""
    id: UUID
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """Схема ответа со статусом задачи."""
    id: UUID
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Схема ответа со списком задач."""
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int


