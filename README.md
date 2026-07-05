# Document Search Service

Сервис для полнотекстового поиска по документам с использованием **PostgreSQL** и **Elasticsearch**.

## Описание

Простой поисковый сервис, который:
- Хранит документы в PostgreSQL (реляционная БД)
- Индексирует тексты в Elasticsearch для быстрого полнотекстового поиска
- Предоставляет REST API для поиска и удаления документов
- Работает асинхронно (FastAPI + async/await)
- Полностью упакован в Docker

## Технологический стек

- **Python 3.11**
- **FastAPI** — асинхронный веб-фреймворк
- **PostgreSQL 15** — реляционная база данных
- **Elasticsearch 8.14** — поисковый движок
- **SQLAlchemy 2.0** — ORM с поддержкой async
- **asyncpg** — асинхронный драйвер для PostgreSQL
- **Pydantic 2.8** — валидация данных
- **Docker & Docker Compose** — контейнеризация
- **Pytest** — тестирование

## Структура проекта

.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение и эндпоинты
│   ├── database.py          # Подключение к PostgreSQL
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   └── es_client.py         # Клиент Elasticsearch
├── scripts/
│   └── import_data.py       # Скрипт импорта данных из CSV
├── tests/
│   └── test_api.py          # Функциональные тесты
├── posts.txt                 # Файл с данными (положи в корень)
├── docker-compose.yml       # Оркестрация контейнеров
├── Dockerfile               # Образ для приложения
├── requirements.txt         # Зависимости Python
└── README.md                # Этот файл

### Предварительные требования

- **Docker Desktop** установлен и запущен
- Файл `data.csv` лежит в корне проекта

### Шаг 1: Клонирование и подготовка

```bash
# Клонируй репозиторий
git clone <your-repo-url>
cd document-search

# Убедись, что файл data.csv лежит в корне
ls posts.txt
```

### Шаг 2: Запуск всех сервисов

```bash
docker-compose up -d --build
```

Эта команда:
- Соберёт Docker-образ с Python и зависимостями
- Запустит PostgreSQL на порту `5432`
- Запустит Elasticsearch на порту `9200`
- Запустит FastAPI на порту `8000`

**Подожди 30-60 секунд**, пока Elasticsearch полностью загрузится.

### Шаг 3: Импорт данных

```bash
docker-compose exec app python scripts/import_data.py
```

Эта команда:
- Создаст таблицу `documents` в PostgreSQL
- Создаст индекс `documents` в Elasticsearch
- Прочитает `data.csv` и заполнит обе базы данных

В консоли ты увидишь:
```
 Successfully imported N documents.
```

### Готово! 

### Способ 1: Swagger UI (рекомендуется)

Открой в браузере:
```
http://localhost:8000/docs
```

Ты увидишь интерактивную документацию, где можно:
- Тестировать все эндпоинты прямо в браузере
- Видеть структуру запросов и ответов
- Скачивать OpenAPI спецификацию

### Способ 2: Командная строка (curl)

#### Поиск документов

```bash
# Поиск по слову "привет"
curl "http://localhost:8000/search?q=привет"

# Поиск по автомобилям
curl "http://localhost:8000/search?q=мерседес"
curl "http://localhost:8000/search?q=ваз"

# Поиск по моделям
curl "http://localhost:8000/search?q=2107"
curl "http://localhost:8000/search?q=спринтер"
```

**Ответ** (пример):
```json
[
  {
    "id": 42,
    "rubrics": [
      "VK-1603736028819866",
      "VK-11879320040"
    ],
    "text": "Всем привет👋.У меня есть вопрос...",
    "created_date": "2019-12-08T15:30:00"
  },
  {
    "id": 15,
    "rubrics": ["VK-1603736028819866", "VK-83173127041"],
    "text": "Всем дратути) Народ,как думаете...",
    "created_date": "2019-12-21T22:32:12"
  }
]
```

**Особенности:**
- Возвращает до **20 документов**
- Отсортированы по дате создания (сначала новые)
- Содержат все поля из БД: `id`, `rubrics`, `text`, `created_date`

#### Удаление документа

```bash
# Удалить документ с id=1
curl -X DELETE "http://localhost:8000/documents/1"
```

**Ответ:**
```json
{
  "status": "ok",
  "message": "Document 1 deleted"
}
```

Документ будет удалён **и из PostgreSQL, и из Elasticsearch**.

