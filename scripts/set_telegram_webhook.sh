#!/usr/bin/env bash
# Register a Telegram Bot webhook pointed at the n8n telegram-bot workflow.
#
# Usage:
#   TELEGRAM_BOT_TOKEN=xxx WEBHOOK_URL=https://n8n.example.com ./scripts/set_telegram_webhook.sh
#
# WEBHOOK_URL must be HTTPS and publicly reachable — Telegram Bot API rejects
# plain HTTP. If your n8n is on HTTP only, put Caddy/nginx in front with a
# real cert, use a Cloudflare Tunnel, or switch to polling via an n8n
# Telegram Trigger node.

set -euo pipefail

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN is required}"
: "${WEBHOOK_URL:?WEBHOOK_URL is required (e.g. https://n8n.example.com)}"

BASE="${WEBHOOK_URL%/}"
TARGET="${BASE}/webhook/telegram-bot"

echo "Registering webhook: ${TARGET}"

curl -fsS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${TARGET}\", \"allowed_updates\": [\"message\", \"edited_message\"], \"drop_pending_updates\": true}"

echo
echo "Verify:"
curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
echo
