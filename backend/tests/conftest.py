"""Конфигурация для unit тестов."""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from backend.models import Task, TaskStatus, TaskPriority


@pytest.fixture
def mock_session():
    """Фикстура для мокирования сессии БД."""
    return Mock()


@pytest.fixture
def mock_rabbitmq_service():
    """Фикстура для мокирования RabbitMQ сервиса."""
    mock = Mock()
    mock.send_task_to_queue = AsyncMock()
    mock.is_connected = Mock(return_value=True)
    return mock


@pytest.fixture
def sample_task():
    """Фикстура для создания тестовой задачи."""
    task = Task(
        id=uuid4(),
        name="Test Task",
        description="Test Description",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.NEW,
        created_at=datetime.utcnow(),
    )
    return task


@pytest.fixture
def sample_task_pending():
    """Фикстура для создания задачи со статусом PENDING."""
    task = Task(
        id=uuid4(),
        name="Pending Task",
        description="Pending Description",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    return task


@pytest.fixture
def sample_task_completed():
    """Фикстура для создания задачи со статусом COMPLETED."""
    task = Task(
        id=uuid4(),
        name="Completed Task",
        description="Completed Description",
        priority=TaskPriority.LOW,
        status=TaskStatus.COMPLETED,
        created_at=datetime.utcnow(),
    )
    return task
