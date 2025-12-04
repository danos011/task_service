"""Сервис для работы с RabbitMQ."""
import json
import logging
from collections.abc import AsyncGenerator
from typing import Annotated, Optional
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection
from fastapi import Depends

from backend.config import settings

logger = logging.getLogger(__name__)


class RabbitMQService:
    """Сервис для работы с RabbitMQ."""
    
    def __init__(self):
        """Инициализация сервиса RabbitMQ."""
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._queue_name = settings.rabbitmq_queue
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """
        Подключиться к RabbitMQ.
        
        Raises:
            Exception: Если не удалось подключиться
        """
        if self._connection is None or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url
                )
                self._channel = await self._connection.channel()
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Error connecting to RabbitMQ: {e}")
                raise
    
    async def disconnect(self) -> None:
        """Отключиться от RabbitMQ."""
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
            self._channel = None
        
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            self._connection = None
        
        logger.info("Disconnected from RabbitMQ")
    
    async def get_channel(self) -> Optional[AbstractChannel]:
        """
        Получить канал RabbitMQ. Если канал не создан, попытается создать подключение.
        
        Returns:
            Канал RabbitMQ или None, если не удалось подключиться
            
        Note:
            Не пробрасывает исключения, чтобы не нарушать работу приложения.
        """
        if self._channel is None or self._channel.is_closed:
            try:
                await self.connect()
            except Exception as e:
                logger.warning(f"Failed to connect to RabbitMQ: {e}")
                return None
        
        return self._channel
    
    async def send_task_to_queue(self, task_id: UUID) -> None:
        """
        Отправить задачу в очередь RabbitMQ.
        
        Args:
            task_id: ID задачи для отправки
            
        Note:
            Если не удалось отправить задачу, ошибка логируется, но не пробрасывается,
            чтобы не нарушать работу приложения при недоступности RabbitMQ.
        """
        try:
            channel = await self.get_channel()
            
            if channel is None:
                logger.warning(
                    f"Cannot send task {task_id} to queue: RabbitMQ is not available. "
                    f"Task will remain in PENDING status."
                )
                return
            
            queue = await channel.declare_queue(
                self._queue_name,
                durable=True,
            )
            
            message_body = json.dumps({"task_id": str(task_id)})
            
            await channel.default_exchange.publish(
                aio_pika.Message(
                    message_body.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=self._queue_name,
            )
            
            logger.info(f"Task {task_id} sent to queue '{self._queue_name}'")
            
        except Exception as e:
            logger.warning(
                f"Failed to send task {task_id} to queue '{self._queue_name}': {e}. "
                f"Task will remain in PENDING status."
            )
    
    async def declare_queue(self, queue_name: Optional[str] = None) -> None:
        """
        Объявить очередь в RabbitMQ.
        
        Args:
            queue_name: Имя очереди (если None, используется очередь по умолчанию)
        """
        channel = await self.get_channel()
        queue = queue_name or self._queue_name
        
        await channel.declare_queue(
            queue,
            durable=True,
        )
        
        logger.info(f"Queue '{queue}' declared")
    
    def is_connected(self) -> bool:
        """
        Проверить, подключен ли сервис к RabbitMQ.
        
        Returns:
            True, если подключен, False иначе
        """
        return (
            self._connection is not None
            and not self._connection.is_closed
            and self._channel is not None
            and not self._channel.is_closed
        )


async def get_rabbitmq_service() -> AsyncGenerator[RabbitMQService, None]:
    """Dependency для получения сервиса RabbitMQ."""
    async with RabbitMQService() as service:
        yield service


RabbitMQServiceDep = Annotated[RabbitMQService, Depends(get_rabbitmq_service)]


