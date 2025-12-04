"""Репозитории."""
from backend.repository.base import BaseRepository
from backend.repository.task_repository import TaskRepository

__all__ = ["BaseRepository", "TaskRepository"]


