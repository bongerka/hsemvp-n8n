# 04. Web Chat Workflow

## Цель

Дать фронтенду простой JSON webhook без отдельного backend сервиса.

## Endpoint

`POST /webhook/web-chat`

## Ноды

1. `Webhook`
2. `Code`
   Нормализует payload:
   - `sessionId`
   - `message`
   - `source = web`

3. `HTTP Request -> Select/create conversation`
   Ищет conversation по:
   - `source = web`
   - `external_user_id = sessionId`

4. `HTTP Request -> Insert user message`

5. `HTTP Request -> Insert event_logs`
   Если conversation новая:
   - `chat_started`

6. `OpenAI -> Embeddings`

7. `HTTP Request -> RPC match_knowledge_chunks`

8. `Code -> build-rag-context.js`

9. `OpenAI -> Chat`

10. `HTTP Request -> Insert assistant message`

11. `Respond to Webhook`

### Response пример

```json
{
  "answer": "Первичный прием стоит 3 500 ₽.",
  "conversationId": "uuid",
  "leadCreated": false
}
```

## Рекомендация

Если хотите общий flow без дублирования, основную логику retrieval + answer удобно вынести в отдельный sub-workflow и вызывать из Telegram и Web Chat.
