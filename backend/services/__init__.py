"""Сервисный слой приложения."""
from backend.database import DBSession
from backend.services.task_service import (
    TaskService,
    TaskServiceDep,
    get_task_service,
)
from backend.services.task_processing_service import TaskProcessingService
from backend.services.rabbitmq_service import (
    RabbitMQService,
    RabbitMQServiceDep,
    get_rabbitmq_service,
)

__all__ = [
    "TaskService",
    "TaskProcessingService",
    "RabbitMQService",
    "DBSession",
    "RabbitMQServiceDep",
    "TaskServiceDep",
    "get_rabbitmq_service",
    "get_task_service",
]
