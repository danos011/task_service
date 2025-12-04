"""Сервис для обработки задач в worker."""
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repository import TaskRepository
from backend.models import TaskStatus
from backend.exceptions import TaskNotFoundError

logger = logging.getLogger(__name__)


class TaskProcessingService:
    """Сервис для обработки задач в worker."""
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса обработки.
        
        Args:
            session: Сессия базы данных
        """
        self.session = session
    
    async def process_task(self, task_id: UUID) -> dict:
        """
        Обработка задачи.
        
        В данном случае просто симулируем обработку:
        - Задача записывается в БД
        - Обрабатывается в очереди
        - Результат сохраняется обратно в БД
        
        Args:
            task_id: ID задачи для обработки
            
        Returns:
            Результат обработки задачи
        """
        await asyncio.sleep(2)
        
        result = {
            "task_id": str(task_id),
            "processed_at": datetime.utcnow().isoformat(),
            "message": "Task processed successfully",
        }
        
        return result
    
    async def start_processing(self, task_id: UUID) -> None:
        """
        Начать обработку задачи (обновить статус на IN_PROGRESS).
        
        Args:
            task_id: ID задачи
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = await TaskRepository.update_status(
            self.session,
            task_id=task_id,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
        )
        
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
    
    async def complete_processing(self, task_id: UUID, result: dict) -> None:
        """
        Завершить обработку задачи успешно.
        
        Args:
            task_id: ID задачи
            result: Результат обработки
        """
        await TaskRepository.update_status(
            self.session,
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            result=result,
        )
    
    async def fail_processing(self, task_id: UUID, error_message: str) -> None:
        """
        Завершить обработку задачи с ошибкой.
        
        Args:
            task_id: ID задачи
            error_message: Сообщение об ошибке
        """
        await TaskRepository.update_status(
            self.session,
            task_id=task_id,
            status=TaskStatus.FAILED,
            completed_at=datetime.utcnow(),
            error_message=error_message,
        )

