"""API маршруты."""
from uuid import UUID

from fastapi import APIRouter, status

from backend.services.task_service import TaskServiceDep
from backend.schemas import (
    TaskCreate,
    TaskResponse,
    TaskStatusResponse,
    TaskListResponse,
    TaskFilterDepends,
    NotFoundErrorResponse,
    BadRequestErrorResponse,
    InternalServerErrorResponse,
    ValidationErrorResponse,
)

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую задачу",
    description=(
        "Создает новую задачу и отправляет её в очередь для асинхронной обработки.\n\n"
        "Параметры запроса:\n"
        "- **name** (обязательный) — название задачи (1-255 символов).\n"
        "- **description** (опциональный) — описание задачи.\n"
        "- **priority** (опциональный) — приоритет задачи: LOW, MEDIUM, HIGH (по умолчанию MEDIUM).\n\n"
        "После создания задача получает статус PENDING и отправляется в очередь RabbitMQ для обработки. "
        "Если RabbitMQ недоступен, задача останется в статусе PENDING до восстановления соединения."
    ),
    responses={
        201: {
            "description": "Задача успешно создана",
            "model": TaskResponse,
        },
        422: {
            "description": "Ошибка валидации входных данных",
            "model": ValidationErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": InternalServerErrorResponse,
        },
    },
)
async def create_task(
    task_data: TaskCreate,
    service: TaskServiceDep,
):
    """Создать новую задачу."""
    return await service.create_task(task_data)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Получить список задач",
    description=(
        "Возвращает список задач с возможностью фильтрации и пагинации.\n\n"
        "Параметры фильтрации:\n"
        "- **status** (опциональный) — фильтр по статусу: NEW, PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED.\n"
        "- **priority** (опциональный) — фильтр по приоритету: LOW, MEDIUM, HIGH.\n"
        "- **created_from** (опциональный) — фильтр по дате создания (от), формат ISO 8601.\n"
        "- **created_to** (опциональный) — фильтр по дате создания (до), формат ISO 8601.\n\n"
        "Параметры пагинации:\n"
        "- **page** (по умолчанию: 1) — номер страницы (минимум 1).\n"
        "- **page_size** (по умолчанию: 10) — количество задач на странице (от 1 до 100).\n\n"
        "Результат включает общее количество задач, количество страниц и список задач на текущей странице."
    ),
    responses={
        200: {
            "description": "Список задач успешно получен",
            "model": TaskListResponse,
        },
        422: {
            "description": "Ошибка валидации параметров запроса",
            "model": ValidationErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_tasks(
    service: TaskServiceDep,
    filters: TaskFilterDepends,
):
    """Получить список задач с фильтрацией и пагинацией."""
    return await service.get_tasks(
        status=filters.status,
        priority=filters.priority,
        created_from=filters.created_from,
        created_to=filters.created_to,
        page=filters.page,
        page_size=filters.page_size,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Получить информацию о задаче",
    description=(
        "Возвращает полную информацию о задаче по её идентификатору.\n\n"
        "Параметры пути:\n"
        "- **task_id** (обязательный) — UUID задачи.\n\n"
        "Возвращает полную информацию о задаче, включая статус, приоритет, даты создания, "
        "начала и завершения, результат выполнения и сообщение об ошибке (если есть)."
    ),
    responses={
        200: {
            "description": "Информация о задаче успешно получена",
            "model": TaskResponse,
        },
        404: {
            "description": "Задача с указанным ID не найдена",
            "model": NotFoundErrorResponse,
        },
        422: {
            "description": "Ошибка валидации UUID",
            "model": ValidationErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_task(
    task_id: UUID,
    service: TaskServiceDep,
):
    """Получить информацию о задаче."""
    return await service.get_task_by_id(task_id)


@router.get(
    "/{task_id}/status",
    response_model=TaskStatusResponse,
    summary="Получить статус задачи",
    description=(
        "Возвращает текущий статус задачи и информацию о времени её выполнения.\n\n"
        "Параметры пути:\n"
        "- **task_id** (обязательный) — UUID задачи.\n\n"
        "Возвращает упрощенную информацию о задаче, включая только статус и временные метки "
        "(создания, начала и завершения выполнения). Полезно для проверки статуса без загрузки "
        "полной информации о задаче."
    ),
    responses={
        200: {
            "description": "Статус задачи успешно получен",
            "model": TaskStatusResponse,
        },
        404: {
            "description": "Задача с указанным ID не найдена",
            "model": NotFoundErrorResponse,
        },
        422: {
            "description": "Ошибка валидации UUID",
            "model": ValidationErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": InternalServerErrorResponse,
        },
    },
)
async def get_task_status(
    task_id: UUID,
    service: TaskServiceDep,
):
    """Получить статус задачи."""
    return await service.get_task_by_id(task_id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отменить задачу",
    description=(
        "Отменяет выполнение задачи, если она еще не завершена.\n\n"
        "Параметры пути:\n"
        "- **task_id** (обязательный) — UUID задачи.\n\n"
        "Задачу можно отменить только если её статус: NEW, PENDING или IN_PROGRESS. "
        "Задачи со статусами COMPLETED, FAILED или CANCELLED отменить нельзя.\n\n"
        "После отмены задача получает статус CANCELLED. Если задача уже обрабатывается, "
        "она будет отменена, но обработка может продолжиться до завершения текущей операции."
    ),
    responses={
        204: {
            "description": "Задача успешно отменена",
        },
        400: {
            "description": "Задачу нельзя отменить (уже завершена, провалена или отменена)",
            "model": BadRequestErrorResponse,
        },
        404: {
            "description": "Задача с указанным ID не найдена",
            "model": NotFoundErrorResponse,
        },
        422: {
            "description": "Ошибка валидации UUID",
            "model": ValidationErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": InternalServerErrorResponse,
        },
    },
)
async def cancel_task(
    task_id: UUID,
    service: TaskServiceDep,
):
    """Отменить задачу."""
    await service.cancel_task(task_id)
    return None


