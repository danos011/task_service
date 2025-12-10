"""Схемы для фильтрации и пагинации."""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, Field

from backend.models import TaskStatus, TaskPriority


class TaskFilterQueryParams(BaseModel):
    """Параметры фильтрации и пагинации для списка задач."""
    
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(10, ge=1, le=100, description="Размер страницы")


TaskFilterDepends = Annotated[TaskFilterQueryParams, Depends()]



