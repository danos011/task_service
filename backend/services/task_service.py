"""Сервис для работы с задачами."""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import DBSession
from backend.repository import TaskRepository
from backend.schemas import TaskCreate, TaskListResponse
from backend.models import Task, TaskStatus, TaskPriority
from backend.services.rabbitmq_service import RabbitMQService, RabbitMQServiceDep
from backend.exceptions import TaskNotFoundError, TaskCannotBeCancelledError


class TaskService:
    """Сервис для работы с задачами."""
    
    def __init__(
        self,
        session: AsyncSession,
        rabbitmq_service: Optional[RabbitMQService] = None,
    ):
        """
        Инициализация сервиса.
        
        Args:
            session: Сессия базы данных
            rabbitmq_service: Сервис RabbitMQ (опционально)
        """
        self.session = session
        self.rabbitmq_service = rabbitmq_service
    
    async def create_task(self, task_data: TaskCreate) -> Task:
        """
        Создать новую задачу и отправить её в очередь.
        
        Args:
            task_data: Данные для создания задачи
            
        Returns:
            Созданная задача
            
        Raises:
            Exception: Если не удалось отправить задачу в очередь
        """
        task = await TaskRepository.create(self.session, task_data.model_dump())
        
        task = await TaskRepository.update_status(
            self.session,
            task_id=task.id,
            status=TaskStatus.PENDING,
        )
        
        if self.rabbitmq_service:
            await self.rabbitmq_service.send_task_to_queue(task.id)
        
        return task
    
    async def get_task_by_id(self, task_id: UUID) -> Task:
        """
        Получить задачу по ID.
        
        Args:
            task_id: ID задачи
            
        Returns:
            Задача
            
        Raises:
            TaskNotFoundError: Если задача не найдена
        """
        task = await TaskRepository.get_by_id(self.session, task_id)
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        return task
    
    async def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> TaskListResponse:
        """
        Получить список задач с фильтрацией и пагинацией.
        
        Args:
            status: Фильтр по статусу
            priority: Фильтр по приоритету
            created_from: Фильтр по дате создания (от)
            created_to: Фильтр по дате создания (до)
            page: Номер страницы
            page_size: Размер страницы
            
        Returns:
            Список задач с метаданными пагинации
        """
        tasks, total = await TaskRepository.get_list(
            self.session,
            status=status,
            priority=priority,
            created_from=created_from,
            created_to=created_to,
            page=page,
            page_size=page_size,
        )
        
        pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
    
    async def cancel_task(self, task_id: UUID) -> Task:
        """
        Отменить задачу.
        
        Args:
            task_id: ID задачи
            
        Returns:
            Отмененная задача
            
        Raises:
            TaskNotFoundError: Если задача не найдена
            TaskCannotBeCancelledError: Если задачу нельзя отменить
        """
        task = await TaskRepository.get_by_id(self.session, task_id)
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise TaskCannotBeCancelledError(
                f"Cannot cancel task with status {task.status}"
            )
        
        cancelled_task = await TaskRepository.cancel(self.session, task_id)
        return cancelled_task


def get_task_service(
    db: DBSession,
    rabbitmq_service: RabbitMQServiceDep,
) -> TaskService:
    """Dependency для получения сервиса задач."""
    return TaskService(session=db, rabbitmq_service=rabbitmq_service)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]

