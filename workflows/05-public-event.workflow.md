# 05. Public Event Workflow

## Цель

Писать публичные продуктовые события из лендинга и web chat без открытия прямой записи в Supabase из браузера.

## Endpoint

`POST /webhook/public-event`

## Белый список событий

- `landing_view`
- `telegram_open_click`
- `chat_started`
- `lead_started`
- `lead_created`

## Ноды

1. `Webhook`
2. `Code`
   Проверяет `eventName` по whitelist.
3. `HTTP Request -> Insert event_logs`
4. `Respond to Webhook`
   Возвращает `204`

## Если webhook не нужен

Этот workflow можно не поднимать. Тогда счетчики `landing_view` и `telegram_open_click` просто не будут заполняться, а основная воронка `chat_started -> lead_created` все равно продолжит работать через Telegram/Web Chat flows.
