# Credentials в n8n

## 1. OpenAI API

Нужен для:

- Chat completion / Responses
- Embeddings
- Speech-to-text

Используйте один credential для всех OpenAI нод.

## 2. Telegram Bot API

Нужен для:

- `Telegram Trigger`
- `Telegram -> Send Message`
- `Telegram -> Get File`

Создание:

1. Создайте бота через BotFather.
2. Возьмите `TELEGRAM_BOT_TOKEN`.
3. Вставьте token в credential.

## 3. Supabase Service Role через HTTP Header Auth

Самый прагматичный вариант для MVP — ходить в Supabase REST API через `HTTP Request`.

Базовый URL:

```text
{{$env.SUPABASE_URL}}/rest/v1
```

Заголовки:

```text
apikey: {{$env.SUPABASE_SERVICE_ROLE_KEY}}
Authorization: Bearer {{$env.SUPABASE_SERVICE_ROLE_KEY}}
Content-Type: application/json
Prefer: return=representation
```

## 4. Когда лучше использовать RPC

Для similarity search по `knowledge_chunks` используйте:

```text
POST {{$env.SUPABASE_URL}}/rest/v1/rpc/match_knowledge_chunks
```

Тело:

```json
{
  "query_embedding": [0.01, 0.02, 0.03],
  "match_count": 5,
  "category_filter": null
}
```

## 5. Что не делать

- не вызывать OpenAI с фронта
- не писать в `knowledge_chunks` из браузера
- не давать public web-страницам service role key
