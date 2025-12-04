# Task Service

Асинхронный сервис управления задачами: создание задач через REST API, обработка в фоновом режиме через RabbitMQ, система приоритетов, статусная модель задач.

Оркестрация через Docker Compose, запуск всех сервисов через `manage.sh`, мониторинг через RabbitMQ Management UI.

---

## Содержание

- <a href="#sec-arch">Архитектура</a>
- <a href="#sec-reqs">Требования</a>
- <a href="#sec-run">Установка и запуск</a>
- <a href="#sec-env">Конфигурация (env)</a>
- <a href="#sec-manage">Команды manage.sh</a>
- <a href="#sec-api">Эндпоинты API и примеры</a>
- <a href="#sec-rabbitmq">Очереди и задачи RabbitMQ</a>
- <a href="#sec-monitor">Мониторинг</a>

---

## Архитектура

<a id="sec-arch"></a>

Сервисы:

- `backend` — FastAPI/Uvicorn (REST API).
- `postgres` — PostgreSQL 14 (база данных).
- `rabbitmq` — RabbitMQ 3 (брокер сообщений, очередь задач).
- `worker` — Python worker (обработка задач из очереди).

Volumes:

- `./logs` → `/app/logs` — логи приложений (backend и worker).
- `postgres_data` — данные PostgreSQL.
- `rabbitmq_data` — данные RabbitMQ.

Сеть:

- bridge‑сеть Docker Compose (default).

Порты:

- API: `8000`
- RabbitMQ Management: `15672`
- RabbitMQ AMQP: `5672`
- PostgreSQL: `5432`

---

## Требования

<a id="sec-reqs"></a>

- Docker, Docker Compose
- Открытые порты 8000/15672/5672/5432

---

## Установка и запуск

<a id="sec-run"></a>

1) Клонирование:

```bash
git clone <repository-url>
cd task_service
```

2) Создать файл `.env` в корне:

```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=task_service

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=tasks

LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

3) Права на manage.sh:

```bash
chmod +x manage.sh
```

4) Запуск с пересборкой:

```bash
./manage.sh up --build
```

Запуск без пересборки:

```bash
./manage.sh up
```

Остановка:

```bash
./manage.sh down
```

Проверка:

- Swagger: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672 (логин `guest`, пароль `guest`)

Примечание:

- Backend стартует через `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`.
- Worker обрабатывает задачи из очереди `tasks` в RabbitMQ.
- Логи сохраняются в `./logs/app.log` (backend) и `./logs/worker.log` (worker).

---

## Конфигурация (env)

<a id="sec-env"></a>

Переменные окружения (`.env`):

**База данных:**
- `POSTGRES_HOST` — хост PostgreSQL (по умолчанию: `postgres`)
- `POSTGRES_PORT` — порт PostgreSQL (по умолчанию: `5432`)
- `POSTGRES_USER` — пользователь PostgreSQL (по умолчанию: `postgres`)
- `POSTGRES_PASSWORD` — пароль PostgreSQL (по умолчанию: `postgres`)
- `POSTGRES_DB` — имя базы данных (по умолчанию: `task_service`)

**RabbitMQ:**
- `RABBITMQ_HOST` — хост RabbitMQ (по умолчанию: `rabbitmq`)
- `RABBITMQ_PORT` — порт RabbitMQ (по умолчанию: `5672`)
- `RABBITMQ_USER` — пользователь RabbitMQ (по умолчанию: `guest`)
- `RABBITMQ_PASSWORD` — пароль RabbitMQ (по умолчанию: `guest`)
- `RABBITMQ_QUEUE` — имя очереди (по умолчанию: `tasks`)

**Приложение:**
- `LOG_LEVEL` — уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE` — путь к файлу логов (по умолчанию: `logs/app.log`)

---

## Команды manage.sh

<a id="sec-manage"></a>

**Docker команды:**
- `./manage.sh up [--build] [--logs]` — запустить все сервисы
- `./manage.sh down` — остановить все сервисы
- `./manage.sh restart` — перезапустить все сервисы
- `./manage.sh build` — собрать Docker образы
- `./manage.sh logs` — показать логи всех сервисов
- `./manage.sh logs-backend` — показать логи backend
- `./manage.sh logs-worker` — показать логи worker
- `./manage.sh status` — показать статус всех сервисов

**Тестирование:**
- `./manage.sh test` — запустить тесты локально
- `./manage.sh test-cov` — запустить тесты с покрытием
- `./manage.sh test-docker` — запустить тесты в Docker
- `./manage.sh test-docker-clean` — запустить тесты в Docker с очисткой

**Миграции:**
- `./manage.sh migrate` / `./manage.sh migrate-up` — применить миграции
- `./manage.sh migrate-down` — откатить последнюю миграцию
- `MESSAGE="описание" ./manage.sh migrate-create` — создать новую миграцию
- `./manage.sh migrate-docker` — применить миграции в Docker контейнере

**Утилиты:**
- `./manage.sh shell-backend` — открыть shell в backend контейнере
- `./manage.sh shell-db` — открыть psql в базе данных
- `./manage.sh help` — показать справку

---

## Эндпоинты API и примеры

<a id="sec-api"></a>

Swagger/OpenAPI:

- http://localhost:8000/docs

Основные ручки:

- `POST /api/v1/tasks`
    - Вход:
  ```json
  {
     "name": "Task name",
     "description": "Task description",
     "priority": "HIGH"
  }
  ```
    - Действие: создает задачу в БД, отправляет в очередь RabbitMQ, возвращает `task_id`.
    - Приоритет: `LOW`, `MEDIUM`, `HIGH` (по умолчанию `MEDIUM`).

- `GET /api/v1/tasks`
    - Параметры: `status`, `priority`, `created_from`, `created_to`, `page`, `page_size`
    - Действие: возвращает список задач с фильтрацией и пагинацией.

- `GET /api/v1/tasks/{task_id}`
    - Действие: возвращает полную информацию о задаче.

- `GET /api/v1/tasks/{task_id}/status`
    - Действие: возвращает статус задачи (упрощенная информация).

- `DELETE /api/v1/tasks/{task_id}`
    - Действие: отменяет задачу (если статус NEW, PENDING или IN_PROGRESS).

Примеры:

Создать задачу

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Process data",
    "description": "Process large dataset",
    "priority": "HIGH"
  }'
```

Получить список задач

```bash
curl "http://localhost:8000/api/v1/tasks?status=PENDING&page=1&page_size=10"
```

Получить задачу по ID

```bash
curl http://localhost:8000/api/v1/tasks/<task_id>
```

Получить статус задачи

```bash
curl http://localhost:8000/api/v1/tasks/<task_id>/status
```

Отменить задачу

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/<task_id>
```

---

## Очереди и задачи RabbitMQ

<a id="sec-rabbitmq"></a>

Очередь:

- `tasks` — очередь для обработки задач (worker читает из этой очереди).

Обработка задач:

- Worker получает сообщение из очереди `tasks` с `task_id`.
- Обновляет статус задачи на `IN_PROGRESS`.
- Выполняет обработку (симуляция работы).
- Обновляет статус на `COMPLETED` (успех) или `FAILED` (ошибка).
- Сохраняет результат или сообщение об ошибке в БД.

Статусы задач:

- `NEW` — новая задача (создана, но еще не отправлена в очередь).
- `PENDING` — ожидает обработки (отправлена в очередь).
- `IN_PROGRESS` — в процессе выполнения.
- `COMPLETED` — завершена успешно.
- `FAILED` — завершена с ошибкой.
- `CANCELLED` — отменена.

Приоритеты:

- `LOW` — низкий приоритет.
- `MEDIUM` — средний приоритет (по умолчанию).
- `HIGH` — высокий приоритет.

---

## Мониторинг

<a id="sec-monitor"></a>

**RabbitMQ Management UI:**

- URL: http://localhost:15672
- Логин: `guest`
- Пароль: `guest`

Возможности:

- Просмотр очередей и сообщений
- Мониторинг соединений и каналов
- Статистика по обменам и очередям
- Управление пользователями и правами

**Логи приложения:**

- Backend: `./logs/app.log`
- Worker: `./logs/worker.log`

Просмотр логов:

```bash
./manage.sh logs
./manage.sh logs-backend
./manage.sh logs-worker
```

**Статус сервисов:**

```bash
./manage.sh status
```

---

## Тестирование

Проект использует pytest для unit-тестирования. Все тесты синхронные и используют моки для изоляции.

### Запуск тестов в Docker (рекомендуется)

**Основная команда:**

```bash
./manage.sh test-docker
```

Эта команда:
- Запускает PostgreSQL и RabbitMQ для тестов
- Собирает Docker образ с тестами
- Запускает pytest в контейнере
- Автоматически останавливается после завершения тестов
- Возвращает код выхода тестов (0 - успех, не 0 - ошибка)

**С очисткой после завершения:**

```bash
./manage.sh test-docker-clean
```

Эта команда делает то же самое, но также:
- Удаляет контейнеры после завершения
- Удаляет volumes (очищает данные тестовой БД)

**Альтернатива (напрямую через docker compose):**

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

**Для просмотра логов во время выполнения:**

```bash
docker compose -f docker-compose.test.yml up --build
```

(без `--abort-on-container-exit`, чтобы контейнеры не останавливались автоматически)

**Очистка после тестов:**

```bash
docker compose -f docker-compose.test.yml down -v
```

### Локальный запуск тестов

**Базовый запуск:**

```bash
./manage.sh test
```

**С покрытием кода:**

```bash
./manage.sh test-cov
```

Эта команда:
- Запускает тесты с измерением покрытия
- Выводит отчет в терминал
- Создает HTML отчет в `htmlcov/`

**Примечание:** Для локального запуска тестов необходимо установить зависимости:

```bash
pip install -r requirements.txt
```

### Структура тестов

Тесты находятся в `backend/tests/`:

- `test_task_service.py` - unit-тесты для TaskService
- `test_task_processing_service.py` - unit-тесты для TaskProcessingService
- `conftest.py` - конфигурация и фикстуры для тестов

Все тесты используют моки для изоляции и не требуют реальных зависимостей (БД, RabbitMQ).

---

## Миграции БД

Создание новой миграции:

```bash
MESSAGE="добавить поле" ./manage.sh migrate-create
```

Применение миграций:

```bash
./manage.sh migrate-up
```

Откат миграции:

```bash
./manage.sh migrate-down
```

Применение миграций в Docker:

```bash
./manage.sh migrate-docker
```

---

## Структура проекта

```
task_service/
├── backend/
│   ├── api/              # API endpoints
│   ├── repository/       # Слой доступа к данным
│   ├── schemas/          # Pydantic схемы
│   ├── services/        # Бизнес-логика
│   ├── alembic/         # Миграции БД
│   ├── tests/           # Тесты
│   ├── main.py          # Точка входа API
│   ├── worker.py        # Worker для обработки задач
│   └── ...
├── docker-compose.yml
├── docker-compose.test.yml
├── manage.sh            # Скрипт управления
├── requirements.txt
└── README.md
```

---

## Лицензия

См. файл LICENSE
