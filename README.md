# ФСТР API - Система управления перевалами

REST API для мобильного приложения ФСТР по управлению базой горных перевалов.

## Описание проекта

Система позволяет туристам отправлять данные о перевалах через мобильное приложение, а модераторам ФСТР - верифицировать и управлять этими данными.

## Функциональность

- **POST /submitData** - отправка данных о перевале
- **GET /pereval/{id}** - получение данных о перевале по ID
- **GET /health** - проверка состояния API
- **GET /** - информация о API

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Установите переменные окружения для подключения к PostgreSQL:

```bash
export FSTR_DB_HOST=127.0.0.1
export FSTR_DB_PORT=5432
export FSTR_DB_LOGIN=pereval_user
export FSTR_DB_PASS=password
export FSTR_DB_NAME=pereval
```

**Примечание:** Убедитесь, что PostgreSQL запущен и пользователь `pereval_user` создан с паролем `password`.

### 3. Инициализация базы данных

```bash
python init_db.py
```

### 4. Запуск API

```bash
python main.py
```

Или с помощью uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API будет доступен по адресу: http://localhost:8000

## Структура проекта

```
├── database/
│   ├── schema.sql          # Схема базы данных
│   └── db_manager.py       # Класс для работы с БД
├── models/
│   └── pereval_models.py   # Pydantic модели
├── main.py                 # Основной файл FastAPI
├── init_db.py             # Скрипт инициализации БД
├── requirements.txt       # Зависимости Python
├── env.example           # Пример переменных окружения
└── README.md            # Документация
```

## API Endpoints

### POST /submitData

Отправка данных о перевале.

**Тело запроса:**
```json
{
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22 13:18:13",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525",
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {"data": "<картинка1>", "title": "Седловина"},
    {"data": "<картинка>", "title": "Подъём"}
  ]
}
```

**Ответы:**
- `200` - Успешно: `{"status": 200, "message": null, "id": 42}`
- `400` - Ошибка валидации: `{"status": 400, "message": "Отсутствует обязательное поле: title", "id": null}`
- `500` - Ошибка сервера: `{"status": 500, "message": "Ошибка подключения к базе данных", "id": null}`

### GET /pereval/{id}

Получение данных о перевале по ID.

**Ответ:** Данные о перевале в формате JSON

### GET /health

Проверка состояния API и подключения к БД.

**Ответ:**
```json
{
  "status": "ok",
  "message": "API и база данных работают корректно"
}
```

## Улучшения структуры БД

По сравнению с оригинальной схемой ФСТР:

1. **Добавлено поле `status`** для модерации (new, pending, accepted, rejected)
2. **Нормализация данных пользователей** - отдельная таблица `pereval_users`
3. **Правильные типы данных** для координат (decimal вместо string)
4. **Индексы** для улучшения производительности
5. **Foreign Key constraints** для целостности данных
6. **ENUM типы** для статусов модерации

## Технологии

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **psycopg2** - драйвер PostgreSQL
- **python-dotenv** - управление переменными окружения

## Разработка

Проект использует Git с веткой `submitData` для разработки.

### Команды Git:
```bash
git checkout -b submitData
git add .
git commit -m "Описание изменений"
git push origin submitData
```
