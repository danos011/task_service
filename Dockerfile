FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY backend/ ./backend/

# Создание директории для логов
RUN mkdir -p logs

# Переменные окружения по умолчанию
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Запуск приложения
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


