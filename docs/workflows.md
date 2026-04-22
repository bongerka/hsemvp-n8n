# Workflows

Ниже описан минимальный, но рабочий набор workflow для MVP.

## 1. Telegram Bot Q&A

Файл: [workflows/01-telegram-bot.workflow.md](../workflows/01-telegram-bot.workflow.md)

Что делает:

1. Принимает входящее сообщение из Telegram.
2. Определяет: текст или голос.
3. Если голос:
   - скачивает файл из Telegram
   - отправляет в OpenAI speech-to-text
   - получает текст вопроса
4. Ищет или создает `conversation`.
5. Сохраняет сообщение пользователя в `messages`.
6. Получает embedding вопроса.
7. Ищет top-k чанки через `match_knowledge_chunks`.
8. Формирует grounded prompt.
9. Вызывает OpenAI chat.
10. Сохраняет ответ в `messages`.
11. Пишет события в `event_logs`.
12. Возвращает ответ в Telegram.
13. При необходимости вызывает Lead Capture workflow.

## 2. Lead Capture

Файл: [workflows/02-lead-capture.workflow.md](../workflows/02-lead-capture.workflow.md)

Что делает:

1. Получает текст диалога или последнее сообщение.
2. Просит модель извлечь JSON:
   - patient_name
   - phone
   - service_interest
   - desired_date
   - notes
   - is_ready_to_create
3. Если данных достаточно:
   - создает lead
   - логирует `lead_created`
4. Если данных не хватает:
   - логирует `lead_started`
   - возвращает follow-up вопрос

## 3. Knowledge Ingestion

Файл: [workflows/03-knowledge-ingestion.workflow.md](../workflows/03-knowledge-ingestion.workflow.md)

Что делает:

1. Принимает документ через webhook или manual trigger.
2. Создает запись в `knowledge_documents`.
3. Делит текст на chunks.
4. Для каждого chunk получает embedding.
5. Пишет чанки в `knowledge_chunks`.
6. Пишет событие об успешной загрузке документа.

## 4. Optional Web Chat

Файл: [workflows/04-web-chat.workflow.md](../workflows/04-web-chat.workflow.md)

Что делает:

1. Принимает вопрос с веб-страницы.
2. Использует тот же retrieval + answer path, что и Telegram.
3. Возвращает JSON.
4. Сохраняет диалог и события в Supabase.

## 5. Optional Public Event Logger

Файл: [workflows/05-public-event.workflow.md](../workflows/05-public-event.workflow.md)

Что делает:

1. Принимает public событие из web.
2. Проверяет, что `eventName` в белом списке.
3. Пишет запись в `event_logs`.
4. Возвращает `204`.
