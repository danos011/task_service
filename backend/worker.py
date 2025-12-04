"""Worker для обработки задач из RabbitMQ."""
import asyncio
import json
import logging
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.services.task_processing_service import TaskProcessingService
from backend.exceptions import TaskNotFoundError

logger = logging.getLogger(__name__)


async def handle_message(message: AbstractIncomingMessage):
    """Обработчик сообщения из очереди с retry логикой."""
    max_retries = 3
    retry_count = message.headers.get("x-retry-count", 0) if message.headers else 0
    
    try:
        body = json.loads(message.body.decode())
        task_id = UUID(body["task_id"])
        
        logger.info(f"Processing task {task_id} (attempt {retry_count + 1}/{max_retries + 1})")
        
        async with AsyncSessionLocal() as session:
            processing_service = TaskProcessingService(session)
            
            try:
                await processing_service.start_processing(task_id)
                
                result = await processing_service.process_task(task_id)
                
                await processing_service.complete_processing(task_id, result)
                
                logger.info(f"Task {task_id} completed successfully")
                await message.ack()
                
            except TaskNotFoundError:
                logger.error(f"Task {task_id} not found")
                await message.ack()
                return
                
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {e}")
                
                if retry_count < max_retries:
                    logger.info(f"Retrying task {task_id} (attempt {retry_count + 1}/{max_retries})")
                    await message.nack(requeue=True)
                    return
                
                await processing_service.fail_processing(
                    task_id,
                    f"Failed after {max_retries + 1} attempts: {str(e)}",
                )
                await message.ack()
                
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.ack()


async def main():
    """Главная функция worker."""
    logger.info("Starting worker...")
    
    connection = await aio_pika.connect_robust(
        settings.rabbitmq_url
    )
    
    channel = await connection.channel()
    
    queue = await channel.declare_queue(
        settings.rabbitmq_queue,
        durable=True,
    )
    
    logger.info(f"Waiting for messages in queue '{settings.rabbitmq_queue}'...")
    
    await queue.consume(handle_message)
    
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Stopping worker...")
        await connection.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(),
        ],
    )
    asyncio.run(main())

