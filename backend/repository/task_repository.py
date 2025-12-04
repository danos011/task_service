"""Репозиторий для работы с задачами."""
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repository.base import BaseRepository
from backend.models import Task, TaskStatus, TaskPriority


class TaskRepository(BaseRepository[Task]):
    """Репозиторий для работы с задачами."""
    
    @staticmethod
    async def create(session: AsyncSession, data: Dict[str, Any]) -> Task:
        """Создать новую задачу."""
        task = Task(**data)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
    
    @staticmethod
    async def get(session: AsyncSession, entity_id: UUID) -> Optional[Task]:
        """Получить задачу по ID."""
        result = await session.execute(
            select(Task).where(Task.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Task], int]:
        """
        Получить список задач с пагинацией и фильтрацией.
        
        Args:
            session: Сессия базы данных
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            filters: Словарь с фильтрами (status, priority, created_from, created_to)
            
        Returns:
            Кортеж (список задач, общее количество)
        """
        query = select(Task)
        count_query = select(func.count()).select_from(Task)
        
        conditions = []
        
        if filters:
            if "status" in filters and filters["status"]:
                conditions.append(Task.status == filters["status"])
            if "priority" in filters and filters["priority"]:
                conditions.append(Task.priority == filters["priority"])
            if "created_from" in filters and filters["created_from"]:
                conditions.append(Task.created_at >= filters["created_from"])
            if "created_to" in filters and filters["created_to"]:
                conditions.append(Task.created_at <= filters["created_to"])
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Task.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks), total
    
    @staticmethod
    async def update(
        session: AsyncSession,
        entity_id: UUID,
        data: Dict[str, Any],
    ) -> Optional[Task]:
        """Обновить задачу."""
        task = await TaskRepository.get(session, entity_id)
        if not task:
            return None
        
        for key, value in data.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        
        await session.commit()
        await session.refresh(task)
        return task
    
    @staticmethod
    async def delete(session: AsyncSession, entity_id: UUID) -> bool:
        """Удалить задачу."""
        task = await TaskRepository.get(session, entity_id)
        if not task:
            return False
        
        await session.delete(task)
        await session.commit()
        return True
    
    @staticmethod
    async def get_by_id(session: AsyncSession, task_id: UUID) -> Optional[Task]:
        """Получить задачу по ID (алиас для get)."""
        return await TaskRepository.get(session, task_id)
    
    @staticmethod
    async def get_list(
        session: AsyncSession,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Task], int]:
        """
        Получить список задач с фильтрацией и пагинацией.
        
        Метод для обратной совместимости, использует get_all внутри.
        """
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
        if created_from:
            filters["created_from"] = created_from
        if created_to:
            filters["created_to"] = created_to
        
        skip = (page - 1) * page_size
        return await TaskRepository.get_all(session, skip=skip, limit=page_size, filters=filters)
    
    @staticmethod
    async def update_status(
        session: AsyncSession,
        task_id: UUID,
        status: TaskStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Task]:
        """Обновить статус задачи."""
        update_data = {"status": status}
        
        if started_at:
            update_data["started_at"] = started_at
        if completed_at:
            update_data["completed_at"] = completed_at
        if result is not None:
            update_data["result"] = result
        if error_message is not None:
            update_data["error_message"] = error_message
        
        return await TaskRepository.update(session, task_id, update_data)
    
    @staticmethod
    async def cancel(session: AsyncSession, task_id: UUID) -> Optional[Task]:
        """Отменить задачу."""
        task = await TaskRepository.get(session, task_id)
        if not task:
            return None
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return task
        
        return await TaskRepository.update(session, task_id, {"status": TaskStatus.CANCELLED})
