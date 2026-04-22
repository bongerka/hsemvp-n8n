# 01. Telegram Bot Workflow

## Цель

Сделать основной пользовательский канал через Telegram без отдельного custom backend.

## Ноды

1. `Telegram Trigger`
   Слушает новые сообщения бота.

2. `Code -> normalize-telegram.js`
   Нормализует payload и определяет:
   - `messageType`
   - `chatId`
   - `telegramUserId`
   - `telegramUsername`
   - `text`

3. `Switch`
   Ветвление:
   - `text`
   - `voice`

4. `Telegram -> Get File`
   Для голосового сообщения получает путь к файлу.

5. `HTTP Request -> Download Voice`
   Скачивает файл из Telegram.

6. `OpenAI -> Transcription`
   Расшифровывает голос в текст.

7. `HTTP Request -> Supabase select/create conversation`
   Ищет conversation по:
   - `source = telegram`
   - `external_user_id = telegramUserId`

   Если нет conversation, создает новую.

8. `HTTP Request -> Insert user message`
   Сохраняет user message в `messages`.

9. `OpenAI -> Embeddings`
   Модель: `text-embedding-3-small`

10. `HTTP Request -> RPC match_knowledge_chunks`
    Возвращает top-k chunks.

11. `Code -> build-rag-context.js`
    Собирает:
    - system prompt
    - user prompt
    - short sources list

12. `OpenAI -> Chat`
    Инструкция должна явно запрещать:
    - медицинские диагнозы
    - клинические рекомендации как врача

    И разрешать:
    - FAQ
    - цены
    - подготовку к визиту
    - правила записи
    - сбор контактов

13. `HTTP Request -> Insert assistant message`
    Сохраняет ответ модели.

14. `HTTP Request -> Insert event_logs`
    Минимум:
    - `telegram_message_received`
    - `voice_transcribed` при голосовом сообщении
    - `chat_started` если conversation новый

15. `Telegram -> Send Message`
    Возвращает текст пользователю.

16. `If/Execute Workflow`
    Если модель определила намерение записи, запускается `02-lead-capture`.

## Нормализация Telegram

Сниппет для Code node:

- [workflows/snippets/normalize-telegram.js](./snippets/normalize-telegram.js)

## Что важно

- хранить весь диалог в Supabase
- не отвечать как врач
- если данных для lead не хватает, бот задает уточняющий вопрос, а не создает пустую заявку
