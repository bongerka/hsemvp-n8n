# Webhook Contracts

## `POST /webhook/web-chat`

Используется публичной страницей `/chat` из web-репы.

### Request

```json
{
  "source": "web",
  "sessionId": "browser-session-uuid",
  "message": "Сколько стоит первичный прием?",
  "metadata": {
    "page": "/chat"
  }
}
```

### Response

```json
{
  "answer": "Первичный прием стоит 3 500 ₽. Могу еще помочь оформить заявку.",
  "conversationId": "uuid",
  "leadCreated": false
}
```

## `POST /webhook/public-event`

Опциональный webhook для событий с лендинга.

### Request

```json
{
  "eventName": "landing_view",
  "source": "web",
  "pathname": "/"
}
```

### Поведение

- whitelist по `eventName`
- запись в `event_logs`
- ответ `204 No Content`

Допустимые события:

- `landing_view`
- `telegram_open_click`
- `chat_started`
- `lead_started`
- `lead_created`

## `POST /webhook/knowledge-ingest`

Вход для базы знаний.

### Request

```json
{
  "title": "Подготовка к анализам",
  "category": "preparation",
  "text": "За 8 часов до анализа не ешьте ..."
}
```

### Response

```json
{
  "documentId": "uuid",
  "chunksCreated": 6
}
```
