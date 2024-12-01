# Flask Project

Этот учебный проект представляет собой веб-приложение на Flask с использованием PostgreSQL в качестве базы данных. Проект упакован в Docker и может быть запущен с помощью Docker Compose.

## Требования

- Docker
- Docker Compose

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <flask-postgres-docker-counter>
   cd flask-postgres-docker-counter
   ```

2. Убедитесь, что Docker и Docker Compose установлены и запущены на компьютере.

## Запуск проекта

1. Соберите и запустите контейнеры с помощью Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Приложение будет доступно по адресу `http://localhost:5000`.

## Остановка проекта

Чтобы остановить контейнеры, выполните: 
```bash
  docker-compose down --volumes
```

## Полезные команды

- **Просмотр логов**: Чтобы просмотреть логи контейнеров, используйте:

  ```bash
  docker-compose logs
  ```

- **Перезапуск контейнеров**: Чтобы перезапустить контейнеры без пересборки, используйте:

  ```bash
  docker-compose restart
  ```

- **Удаление всех контейнеров и данных**: Чтобы удалить все контейнеры и данные, используйте:

  ```bash
  docker-compose down -v
  ```

## Структура проекта

- `app/`: Директория с исходным кодом Flask приложения.
- `Dockerfile`: Файл для сборки Docker образа приложения.
- `docker-compose.yml`: Файл конфигурации Docker Compose.
- `requirements.txt`: Файл с зависимостями Python.
