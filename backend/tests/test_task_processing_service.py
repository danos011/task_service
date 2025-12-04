"""Unit тесты для TaskProcessingService."""
import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from backend.services.task_processing_service import TaskProcessingService
from backend.models import Task, TaskStatus
from backend.exceptions import TaskNotFoundError


class TestTaskProcessingService:
    """Тесты для TaskProcessingService."""
    
    def test_init(self, mock_session):
        """Тест инициализации сервиса."""
        service = TaskProcessingService(session=mock_session)
        
        assert service.session == mock_session
    
    def test_process_task(self, mock_session):
        """Тест обработки задачи."""
        task_id = uuid4()
        
        service = TaskProcessingService(session=mock_session)
        
        result = asyncio.run(service.process_task(task_id))
        
        assert result["task_id"] == str(task_id)
        assert "processed_at" in result
        assert result["message"] == "Task processed successfully"
    
    def test_start_processing(self, mock_session, sample_task):
        """Тест начала обработки задачи."""
        in_progress_task = Task(
            id=sample_task.id,
            name=sample_task.name,
            priority=sample_task.priority,
            status=TaskStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
        )
        
        with patch('backend.services.task_processing_service.TaskRepository') as mock_repo:
            mock_repo.update_status = AsyncMock(return_value=in_progress_task)
            
            service = TaskProcessingService(session=mock_session)
            
            asyncio.run(service.start_processing(sample_task.id))
            
            mock_repo.update_status.assert_called_once()
            call_args = mock_repo.update_status.call_args
            assert call_args[0][0] == mock_session
            assert call_args[1]["task_id"] == sample_task.id
            assert call_args[1]["status"] == TaskStatus.IN_PROGRESS
            assert "started_at" in call_args[1]
    
    def test_start_processing_not_found(self, mock_session):
        """Тест начала обработки несуществующей задачи."""
        task_id = uuid4()
        
        with patch('backend.services.task_processing_service.TaskRepository') as mock_repo:
            mock_repo.update_status = AsyncMock(return_value=None)
            
            service = TaskProcessingService(session=mock_session)
            
            with pytest.raises(TaskNotFoundError):
                asyncio.run(service.start_processing(task_id))
            
            mock_repo.update_status.assert_called_once()
    
    def test_complete_processing(self, mock_session, sample_task):
        """Тест успешного завершения обработки."""
        result = {
            "task_id": str(sample_task.id),
            "message": "Task completed"
        }
        
        with patch('backend.services.task_processing_service.TaskRepository') as mock_repo:
            mock_repo.update_status = AsyncMock()
            
            service = TaskProcessingService(session=mock_session)
            
            asyncio.run(service.complete_processing(sample_task.id, result))
            
            mock_repo.update_status.assert_called_once()
            call_args = mock_repo.update_status.call_args
            assert call_args[0][0] == mock_session
            assert call_args[1]["task_id"] == sample_task.id
            assert call_args[1]["status"] == TaskStatus.COMPLETED
            assert call_args[1]["result"] == result
            assert "completed_at" in call_args[1]
    
    def test_fail_processing(self, mock_session, sample_task):
        """Тест завершения обработки с ошибкой."""
        error_message = "Processing failed"
        
        with patch('backend.services.task_processing_service.TaskRepository') as mock_repo:
            mock_repo.update_status = AsyncMock()
            
            service = TaskProcessingService(session=mock_session)
            
            asyncio.run(service.fail_processing(sample_task.id, error_message))
            
            mock_repo.update_status.assert_called_once()
            call_args = mock_repo.update_status.call_args
            assert call_args[0][0] == mock_session
            assert call_args[1]["task_id"] == sample_task.id
            assert call_args[1]["status"] == TaskStatus.FAILED
            assert call_args[1]["error_message"] == error_message
            assert "completed_at" in call_args[1]

