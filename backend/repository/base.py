"""Базовый абстрактный репозиторий."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(ABC, Generic[ModelType]):
    """Абстрактный базовый репозиторий с общими методами CRUD."""
    
    @staticmethod
    @abstractmethod
    async def create(session: AsyncSession, data: Dict[str, Any]) -> ModelType:
        """
        Создать новую запись.
        
        Args:
            session: Сессия базы данных
            data: Словарь с данными для создания
            
        Returns:
            Созданная модель
        """
        pass
    
    @staticmethod
    @abstractmethod
    async def get(session: AsyncSession, entity_id: UUID) -> Optional[ModelType]:
        """
        Получить запись по ID.
        
        Args:
            session: Сессия базы данных
            entity_id: ID записи
            
        Returns:
            Модель или None, если не найдена
        """
        pass
    
    @staticmethod
    @abstractmethod
    async def get_all(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[ModelType], int]:
        """
        Получить список записей с пагинацией и фильтрацией.
        
        Args:
            session: Сессия базы данных
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            filters: Словарь с фильтрами
            
        Returns:
            Кортеж (список записей, общее количество)
        """
        pass
    
    @staticmethod
    @abstractmethod
    async def update(
        session: AsyncSession,
        entity_id: UUID,
        data: Dict[str, Any],
    ) -> Optional[ModelType]:
        """
        Обновить запись.
        
        Args:
            session: Сессия базы данных
            entity_id: ID записи
            data: Словарь с данными для обновления
            
        Returns:
            Обновленная модель или None, если не найдена
        """
        pass
    
    @staticmethod
    @abstractmethod
    async def delete(session: AsyncSession, entity_id: UUID) -> bool:
        """
        Удалить запись.
        
        Args:
            session: Сессия базы данных
            entity_id: ID записи
            
        Returns:
            True, если удалено успешно, False если запись не найдена
        """
        pass
