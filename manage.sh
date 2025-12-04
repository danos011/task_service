#!/bin/bash

COMPOSE_FILE="docker-compose.yml"
COMPOSE_TEST_FILE="docker-compose.test.yml"
PYTHON="python3"

show_help() {
    echo "Использование: $0 [команда] [опции]"
    echo ""
    echo "Команды:"
    echo "  up              Запустить все сервисы"
    echo "  down            Остановить все сервисы"
    echo "  restart         Перезапустить все сервисы"
    echo "  build           Собрать Docker образы"
    echo "  logs            Показать логи всех сервисов"
    echo "  logs-backend    Показать логи backend"
    echo "  logs-worker     Показать логи worker"
    echo "  status          Показать статус всех сервисов"
    echo "  test            Запустить тесты локально"
    echo "  test-cov        Запустить тесты с покрытием"
    echo "  test-docker     Запустить тесты в Docker"
    echo "  test-docker-clean  Запустить тесты в Docker с очисткой"
    echo "  migrate         Применить миграции"
    echo "  migrate-up      Применить миграции"
    echo "  migrate-down    Откатить последнюю миграцию"
    echo "  migrate-create  Создать новую миграцию (требует MESSAGE='описание')"
    echo "  migrate-docker  Применить миграции в Docker контейнере"
    echo "  shell-backend   Открыть shell в backend контейнере"
    echo "  shell-db        Открыть psql в базе данных"
    echo "  help            Показать эту справку"
    echo ""
    echo "Опции для команды 'up':"
    echo "  --build         Пересобрать образы перед запуском"
    echo "  --logs          Показать логи после запуска"
}

cmd_up() {
    BUILD=false
    LOGS=false
    
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --build) BUILD=true ;;
            --logs) LOGS=true ;;
            *) echo "Неизвестный флаг: $1"; exit 1 ;;
        esac
        shift
    done
    
    if [ "$BUILD" = true ]; then
        docker compose -f $COMPOSE_FILE build
    fi
    
    docker compose -f $COMPOSE_FILE up -d
    docker compose -f $COMPOSE_FILE ps
    
    if [ "$LOGS" = true ]; then
        echo "Показываю логи..."
        docker compose -f $COMPOSE_FILE logs -f
    else
        echo "Стек запущен успешно!"
    fi
}

cmd_down() {
    docker compose -f $COMPOSE_FILE down
}

cmd_restart() {
    docker compose -f $COMPOSE_FILE restart
}

cmd_build() {
    docker compose -f $COMPOSE_FILE build
}

cmd_logs() {
    docker compose -f $COMPOSE_FILE logs -f
}

cmd_logs_backend() {
    docker compose -f $COMPOSE_FILE logs -f backend
}

cmd_logs_worker() {
    docker compose -f $COMPOSE_FILE logs -f worker
}

cmd_status() {
    docker compose -f $COMPOSE_FILE ps
}

cmd_test() {
    $PYTHON -m pytest backend/tests/ -v
}

cmd_test_cov() {
    $PYTHON -m pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term
}

cmd_test_docker() {
    docker compose -f $COMPOSE_TEST_FILE up --build --abort-on-container-exit
}

cmd_test_docker_clean() {
    docker compose -f $COMPOSE_TEST_FILE up --build --abort-on-container-exit
    docker compose -f $COMPOSE_TEST_FILE down -v
}

cmd_migrate() {
    cmd_migrate_up
}

cmd_migrate_up() {
    cd backend && alembic upgrade head
}

cmd_migrate_down() {
    cd backend && alembic downgrade -1
}

cmd_migrate_create() {
    if [ -z "$MESSAGE" ]; then
        echo "Ошибка: требуется переменная MESSAGE с описанием миграции"
        echo "Использование: MESSAGE='описание' $0 migrate-create"
        exit 1
    fi
    cd backend && alembic revision --autogenerate -m "$MESSAGE"
}

cmd_migrate_docker() {
    docker compose -f $COMPOSE_FILE exec backend alembic upgrade head
}

cmd_shell_backend() {
    docker compose -f $COMPOSE_FILE exec backend /bin/bash
}

cmd_shell_db() {
    docker compose -f $COMPOSE_FILE exec postgres psql -U postgres -d task_service
}

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND=$1
shift

case $COMMAND in
    up)
        cmd_up "$@"
        ;;
    down)
        cmd_down
        ;;
    restart)
        cmd_restart
        ;;
    build)
        cmd_build
        ;;
    logs)
        cmd_logs
        ;;
    logs-backend)
        cmd_logs_backend
        ;;
    logs-worker)
        cmd_logs_worker
        ;;
    status)
        cmd_status
        ;;
    test)
        cmd_test
        ;;
    test-cov)
        cmd_test_cov
        ;;
    test-docker)
        cmd_test_docker
        ;;
    test-docker-clean)
        cmd_test_docker_clean
        ;;
    migrate)
        cmd_migrate
        ;;
    migrate-up)
        cmd_migrate_up
        ;;
    migrate-down)
        cmd_migrate_down
        ;;
    migrate-create)
        cmd_migrate_create
        ;;
    migrate-docker)
        cmd_migrate_docker
        ;;
    shell-backend)
        cmd_shell_backend
        ;;
    shell-db)
        cmd_shell_db
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Неизвестная команда: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac

