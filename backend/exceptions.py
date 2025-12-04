"""Кастомные исключения приложения."""


class TaskServiceError(Exception):
    """Базовое исключение для сервиса задач."""
    pass


class TaskNotFoundError(TaskServiceError):
    """Исключение, когда задача не найдена."""
    pass


class TaskCannotBeCancelledError(TaskServiceError):
    """Исключение, когда задачу нельзя отменить."""
    pass


