# Тестирование
Для тестирования создается отдельная тестовая БД в докере. Тестирование на деплое - это надо заказывать отдельную БД, поэтому не сделал. Все пока только локально.

0. не забываем запустить Докер, а также ```poetry install```
1. ```docker compose -f docker-compose.test.yml up -d```
2. ```pytest --cov=app --cov-report=term-missing --cov-report=html tests```
3. после завершения тестирования ```docker compose -f docker-compose.test.yml down -v```

# Нагрузочное тестирование

1. Сперва поднимаем сервис: :```docker compose up```
2. ```locust -f load/locustfile.py -H http://localhost:8000``` можно тестировать и нагрузку на проде: ```locust -f load/locustfile.py -H https://shortlink-mialbarinov.onrender.com``` главное осторожно, чтобы не решили что это ДДОС и не словить 429
3. http://127.0.0.1:8089/
4. Указываем параметры и смотрим как покажет себя сервис

# Shortlink API Service

Сервис сокращения ссылок с аналитикой и управлением ссылками.

Пример работающего сервиса:
https://shortlink-mialbarinov.onrender.com

---

# Описание API

## Создание короткой ссылки

```
POST /links/shorten
```

Создает короткую ссылку для указанного URL.

### Request

```json
{
  "original_url": "https://example.com",
  "custom_alias": "my-link",
  "expires_at": "2026-03-20T10:00:00"
}
```

### Response

```json
{
  "short_code": "abc123"
}
```

Короткая ссылка будет доступна по адресу:

```
https://shortlink-mialbarinov.onrender.com/abc123
```

---

## Переход по короткой ссылке

```
GET /{short_code}
```

Перенаправляет пользователя на оригинальный URL.

Пример:

```
GET /abc123
```

---

## Получение статистики

```
GET /links/{short_code}/stats
```

Возвращает информацию о ссылке.

### Response

```json
{
  "original_url": "https://example.com",
  "created_at": "2026-03-15T20:00:00",
  "clicks": 10,
  "last_accessed": "2026-03-15T21:10:00"
}
```

---

## Поиск ссылки по URL

```
GET /links/search?fragment=example
```

Возвращает все ссылки, содержащие указанный фрагмент URL.

### Response

```json
[
  {
    "short_code": "abc123",
    "original_url": "https://example.com/page"
  }
]
```

Минимальная длина фрагмента — 4 символа.

---

## Изменение ссылки

```
PUT /links/{short_code}
```

### Request

```json
{
  "original_url": "https://new-url.com"
}
```

---

## Удаление ссылки

```
DELETE /links/{short_code}
```

Удаляет ссылку.

---

## Удаление неиспользуемых ссылок

```
DELETE /links/cleanup?days=30
```

Удаляет ссылки, которые не использовались указанное количество дней.

---

# Авторизация

## Регистрация

```
POST /auth/register
```

### Request

```json
{
  "login": "user1",
  "password": "password"
}
```

---

## Вход

```
POST /auth/login
```

### Request

```json
{
  "login": "user1",
  "password": "password"
}
```

---

## Текущий пользователь

```
GET /auth/me
```

Возвращает информацию о текущем пользователе.

---

# Инструкция по запуску

## Docker

```
docker compose up --build
```

После запуска сервис будет доступен по адресу:

```
http://localhost:8000
```

---

# Переменные окружения

```
DATABASE_URL
REDIS_URL
```

Пример:

```
DATABASE_URL=postgresql://user:password@host/db
REDIS_URL=redis://host:6379
```

---

# Используемые технологии

* FastAPI
* PostgreSQL
* Redis
* SQLAlchemy
* Docker
* Poetry

---

# База данных

Основные таблицы:

## users

```
id
login
password_hash
created_at
```

## links

```
id
original_url
short_code
custom_alias
clicks
created_at
expires_at
last_accessed
user_id
```

---

# Кэширование

Для ускорения редиректов используется Redis.

Кэшируются:

```
short_code -> original_url
```

При обновлении или удалении ссылки кэш очищается.

---

# Дополнительные функции

Реализованы:

* удаление неиспользуемых ссылок
* поиск по фрагменту URL
* пользовательская авторизация
* кастомные alias
* статистика переходов

* мини-админка с возможностью сбросить Редис 
```
POST /admin/redis/flush
```

---
