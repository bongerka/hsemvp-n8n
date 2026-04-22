# clinic-admin-assistant-n8n

Self-hosted n8n-репозиторий для MVP AI-помощника администратора клиники.

Основной принцип: не строим отдельный Node/Nest/FastAPI backend. Вся оркестрация живет в n8n, а данные хранятся в Supabase.

## Что здесь есть

- `docker-compose.yml` для запуска n8n на VPS
- `.env.example` с обязательными переменными
- `docs/` с пошаговым описанием workflow и webhook контрактов
- `workflows/` с blueprint-описаниями нод
- `workflows/snippets/` с JS для Code nodes

## Стек

- n8n self-hosted
- Docker Compose
- OpenAI API
- Telegram Bot API
- Supabase REST / RPC / DB

## Быстрый запуск на VPS

```bash
cp .env.example .env
docker compose pull
docker compose up -d
docker compose logs -f
```

Проверка:

- n8n editor: `http(s)://<N8N_HOST>:5678` или через ваш reverse proxy
- webhook base: `${WEBHOOK_URL}`

Важно:

- локальный PostgreSQL не поднимаем
- n8n пишет сразу в Supabase cloud DB
- для продовой HTTPS-ссылки лучше использовать reverse proxy перед контейнером

## Обязательные env

```env
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
N8N_HOST=
N8N_PROTOCOL=
WEBHOOK_URL=
GENERIC_TIMEZONE=
```

Для текущего MVP `docker-compose.yml` также включает:

- `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
- `NODE_FUNCTION_ALLOW_BUILTIN=https,crypto,url`
- `N8N_RUNNERS_ENABLED=false`

Это сделано специально для быстрого MVP, где часть логики живет в `Code` nodes и использует встроенный модуль `https`.

## Какие credentials создать в n8n

1. `OpenAI API`
   Используется для Chat, Embeddings и Speech-to-Text.

2. `Telegram Bot API`
   Используется для `Telegram Trigger`, `Get File`, `Send Message`.

3. `HTTP Header Auth` или `Generic Credential` для Supabase
   Заголовки:

```text
apikey: {{$env.SUPABASE_SERVICE_ROLE_KEY}}
Authorization: Bearer {{$env.SUPABASE_SERVICE_ROLE_KEY}}
Content-Type: application/json
Prefer: return=representation
```

## Что должно жить в n8n

1. Telegram incoming message workflow
2. Lead capture workflow
3. Knowledge ingestion workflow
4. Optional web chat webhook workflow
5. Optional public event webhook workflow

Подробно:

- [docs/workflows.md](./docs/workflows.md)
- [docs/credentials.md](./docs/credentials.md)
- [docs/webhook-contracts.md](./docs/webhook-contracts.md)

## Рекомендуемые webhook endpoints

- `POST /webhook/web-chat`
- `POST /webhook/public-event`
- `POST /webhook/knowledge-ingest`

Telegram-входящий сценарий удобнее делать через `Telegram Trigger`, а не через обычный webhook endpoint руками.

## Как фронтенд связан с этой репой

Во frontend-репе используются такие env:

- `NEXT_PUBLIC_TELEGRAM_BOT_URL`
- `NEXT_PUBLIC_N8N_CHAT_WEBHOOK_URL`
- `NEXT_PUBLIC_N8N_EVENT_WEBHOOK_URL` — опционально

Веб-чат шлет сообщения напрямую в `POST /webhook/web-chat`.

## Supabase endpoints, которые обычно вызываются из n8n

- `POST /rest/v1/conversations`
- `POST /rest/v1/messages`
- `POST /rest/v1/leads`
- `POST /rest/v1/event_logs`
- `POST /rest/v1/knowledge_documents`
- `POST /rest/v1/knowledge_chunks`
- `POST /rest/v1/rpc/match_knowledge_chunks`

## RAG схема

1. Получить текст документа.
2. Порезать на chunks по 500–1000 символов с overlap.
3. Для каждого chunk получить embedding моделью `text-embedding-3-small`.
4. Сохранить в `knowledge_chunks`.
5. При вопросе пользователя:
   - получить embedding вопроса
   - вызвать Supabase RPC `match_knowledge_chunks`
   - собрать system prompt + context
   - вызвать OpenAI Chat

## Минимальный порядок сборки

1. Применить Supabase schema из web-репы.
2. Поднять n8n.
3. Завершить owner setup в UI n8n.
4. При необходимости задеплоить базовые workflow скриптом `python3 scripts/deploy_workflows.py`.
5. Загрузить FAQ/price list через `POST /webhook/knowledge-ingest`.
6. Подключить web chat и telemetry webhook со стороны frontend.
7. Собрать Telegram workflow или polling-сценарий.
8. Проверить, что в Supabase появляются `conversations`, `messages`, `leads`, `event_logs`.
