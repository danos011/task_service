"""Unit тесты для TaskService."""
import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from backend.services.task_service import TaskService
from backend.schemas import TaskCreate
from backend.models import Task, TaskStatus, TaskPriority
from backend.exceptions import TaskNotFoundError, TaskCannotBeCancelledError


class TestTaskService:
    """Тесты для TaskService."""
    
    def test_init(self, mock_session, mock_rabbitmq_service):
        """Тест инициализации сервиса."""
        service = TaskService(
            session=mock_session,
            rabbitmq_service=mock_rabbitmq_service
        )
        
        assert service.session == mock_session
        assert service.rabbitmq_service == mock_rabbitmq_service
    
    def test_init_without_rabbitmq(self, mock_session):
        """Тест инициализации без RabbitMQ сервиса."""
        service = TaskService(session=mock_session)
        
        assert service.session == mock_session
        assert service.rabbitmq_service is None
    
    def test_create_task(self, mock_session, mock_rabbitmq_service, sample_task):
        """Тест создания задачи."""
        task_data = TaskCreate(
            name="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH
        )
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            task_new = Task(
                id=sample_task.id,
                name=task_data.name,
                description=task_data.description,
                priority=task_data.priority,
                status=TaskStatus.NEW,
                created_at=datetime.utcnow(),
            )
            
            task_pending = Task(
                id=sample_task.id,
                name=task_data.name,
                description=task_data.description,
                priority=task_data.priority,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow(),
            )
            
            mock_repo.create = AsyncMock(return_value=task_new)
            mock_repo.update_status = AsyncMock(return_value=task_pending)
            
            service = TaskService(
                session=mock_session,
                rabbitmq_service=mock_rabbitmq_service
            )
            
            result = asyncio.run(service.create_task(task_data))
            
            mock_repo.create.assert_called_once()
            mock_repo.update_status.assert_called_once()
            mock_rabbitmq_service.send_task_to_queue.assert_called_once_with(sample_task.id)
            
            assert result.status == TaskStatus.PENDING
            assert result.name == task_data.name
    
    def test_create_task_without_rabbitmq(self, mock_session, sample_task):
        """Тест создания задачи без RabbitMQ."""
        task_data = TaskCreate(
            name="Test Task",
            priority=TaskPriority.MEDIUM
        )
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            task_new = Task(
                id=sample_task.id,
                name=task_data.name,
                priority=task_data.priority,
                status=TaskStatus.NEW,
                created_at=datetime.utcnow(),
            )
            task_pending = Task(
                id=sample_task.id,
                name=task_data.name,
                priority=task_data.priority,
                status=TaskStatus.PENDING,
                created_at=datetime.utcnow(),
            )
            
            mock_repo.create = AsyncMock(return_value=task_new)
            mock_repo.update_status = AsyncMock(return_value=task_pending)
            
            service = TaskService(session=mock_session)
            
            result = asyncio.run(service.create_task(task_data))
            
            assert result.status == TaskStatus.PENDING
            mock_repo.create.assert_called_once()
            mock_repo.update_status.assert_called_once()
    
    def test_get_task_by_id(self, mock_session, sample_task):
        """Тест получения задачи по ID."""
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=sample_task)
            
            service = TaskService(session=mock_session)
            
            result = asyncio.run(service.get_task_by_id(sample_task.id))
            
            assert result == sample_task
            mock_repo.get_by_id.assert_called_once_with(mock_session, sample_task.id)
    
    def test_get_task_by_id_not_found(self, mock_session):
        """Тест получения несуществующей задачи."""
        task_id = uuid4()
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)
            
            service = TaskService(session=mock_session)
            
            with pytest.raises(TaskNotFoundError):
                asyncio.run(service.get_task_by_id(task_id))
            
            mock_repo.get_by_id.assert_called_once_with(mock_session, task_id)
    
    def test_get_tasks(self, mock_session, sample_task, sample_task_pending):
        """Тест получения списка задач."""
        tasks_list = [sample_task, sample_task_pending]
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_list = AsyncMock(return_value=(tasks_list, 2))
            
            service = TaskService(session=mock_session)
            
            result = asyncio.run(service.get_tasks(page=1, page_size=10))
            
            assert result.total == 2
            assert len(result.items) == 2
            assert result.page == 1
            assert result.page_size == 10
            assert result.pages == 1
            mock_repo.get_list.assert_called_once()
    
    def test_get_tasks_with_filters(self, mock_session, sample_task):
        """Тест получения списка задач с фильтрами."""
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_list = AsyncMock(return_value=([sample_task], 1))
            
            service = TaskService(session=mock_session)
            
            result = asyncio.run(service.get_tasks(
                status=TaskStatus.NEW,
                priority=TaskPriority.MEDIUM,
                page=1,
                page_size=10
            ))
            
            assert result.total == 1
            mock_repo.get_list.assert_called_once_with(
                mock_session,
                status=TaskStatus.NEW,
                priority=TaskPriority.MEDIUM,
                created_from=None,
                created_to=None,
                page=1,
                page_size=10
            )
    
    def test_cancel_task(self, mock_session, sample_task_pending):
        """Тест отмены задачи."""
        cancelled_task = Task(
            id=sample_task_pending.id,
            name=sample_task_pending.name,
            priority=sample_task_pending.priority,
            status=TaskStatus.CANCELLED,
            created_at=datetime.utcnow(),
        )
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=sample_task_pending)
            mock_repo.cancel = AsyncMock(return_value=cancelled_task)
            
            service = TaskService(session=mock_session)
            
            result = asyncio.run(service.cancel_task(sample_task_pending.id))
            
            assert result.status == TaskStatus.CANCELLED
            mock_repo.get_by_id.assert_called_once_with(mock_session, sample_task_pending.id)
            mock_repo.cancel.assert_called_once_with(mock_session, sample_task_pending.id)
    
    def test_cancel_task_not_found(self, mock_session):
        """Тест отмены несуществующей задачи."""
        task_id = uuid4()
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)
            
            service = TaskService(session=mock_session)
            
            with pytest.raises(TaskNotFoundError):
                asyncio.run(service.cancel_task(task_id))
    
    def test_cancel_task_already_completed(self, mock_session, sample_task_completed):
        """Тест отмены уже завершенной задачи."""
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=sample_task_completed)
            
            service = TaskService(session=mock_session)
            
            with pytest.raises(TaskCannotBeCancelledError):
                asyncio.run(service.cancel_task(sample_task_completed.id))
            
            mock_repo.get_by_id.assert_called_once()
            mock_repo.cancel.assert_not_called()
    
    def test_cancel_task_already_failed(self, mock_session, sample_task):
        """Тест отмены задачи со статусом FAILED."""
        failed_task = Task(
            id=sample_task.id,
            name=sample_task.name,
            priority=sample_task.priority,
            status=TaskStatus.FAILED,
            created_at=datetime.utcnow(),
        )
        
        with patch('backend.services.task_service.TaskRepository') as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=failed_task)
            
            service = TaskService(session=mock_session)
            
            with pytest.raises(TaskCannotBeCancelledError):
                asyncio.run(service.cancel_task(failed_task.id))

