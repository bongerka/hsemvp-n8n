# 02. Lead Capture Workflow

## Цель

Создавать lead в Supabase, когда пользователь готов оставить заявку на запись.

## Входные данные

- `conversationId`
- `source`
- `externalUserId`
- `telegramUsername`
- `latestUserMessage`
- `recentMessages[]`

## Ноды

1. `Execute Workflow Trigger` или `Webhook`
   Принимает подготовленные данные из основного диалога.

2. `OpenAI -> Structured extraction`
   Попросить модель вернуть JSON вида:

```json
{
  "patient_name": "Анна",
  "phone": "+79991234567",
  "service_interest": "первичный прием терапевта",
  "desired_date": "следующая неделя",
  "notes": "предпочтительно утром",
  "is_ready_to_create": true,
  "followup_question": null
}
```

3. `If`
   Проверяет `is_ready_to_create`.

4. `HTTP Request -> Insert lead`
   Пишет запись в `leads`.

5. `HTTP Request -> Insert event_logs`
   Пишет:
   - `lead_started` если сценарий начался
   - `lead_created` если запись реально создана

6. `Return / Telegram Send Message`
   Возвращает:
   - подтверждение создания заявки
   - либо уточняющий вопрос

## Важное правило

Lead — это request, а не реальный booking.

Никакой интеграции с расписанием врачей и календарем в MVP не нужно.
