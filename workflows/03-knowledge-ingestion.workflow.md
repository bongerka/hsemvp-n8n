# 03. Knowledge Ingestion Workflow

## Цель

Загружать документы клиники в RAG-хранилище.

Подходит для:

- FAQ
- прайса
- подготовки к приему
- правил записи

## Вход

Webhook:

```json
{
  "title": "FAQ по записи",
  "category": "faq",
  "text": "..."
}
```

## Ноды

1. `Webhook` или `Manual Trigger`
2. `HTTP Request -> Insert knowledge_document`
3. `Code -> chunk-text.js`
4. `Loop Over Items`
5. `OpenAI -> Embeddings`
6. `HTTP Request -> Insert knowledge_chunk`
7. `HTTP Request -> Insert event_logs`

## Параметры chunking

- размер чанка: 700–900 символов
- overlap: 120–180 символов

Сниппет:

- [workflows/snippets/chunk-text.js](./snippets/chunk-text.js)

## Что хранить в metadata

Рекомендуемо:

```json
{
  "chunk_index": 0,
  "source_title": "FAQ по записи",
  "category": "faq"
}
```
