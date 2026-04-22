#!/usr/bin/env python3
"""
Deploy or update the baseline n8n workflows for the clinic admin assistant MVP.

Required environment variables:
  N8N_BASE_URL
  N8N_EMAIL
  N8N_PASSWORD
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://109.122.196.8:5678").rstrip("/")
N8N_EMAIL = os.environ.get("N8N_EMAIL", "")
N8N_PASSWORD = os.environ.get("N8N_PASSWORD", "")


PUBLIC_EVENT_CODE = r"""
const https = require('https');
const { URL } = require('url');

function requestJson(url, options = {}) {
  const parsedUrl = new URL(url);
  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        protocol: parsedUrl.protocol,
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 443,
        path: `${parsedUrl.pathname}${parsedUrl.search}`,
        method: options.method ?? 'GET',
        headers: options.headers ?? {},
      },
      (response) => {
        let raw = '';
        response.on('data', (chunk) => {
          raw += chunk;
        });
        response.on('end', () => {
          let data = null;
          if (raw) {
            try {
              data = JSON.parse(raw);
            } catch {
              data = raw;
            }
          }
          if (response.statusCode >= 200 && response.statusCode < 300) {
            resolve(data);
            return;
          }
          reject(new Error(typeof data === 'string' ? data : JSON.stringify(data)));
        });
      },
    );

    request.on('error', reject);

    if (options.body !== undefined) {
      request.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
    }

    request.end();
  });
}

const payload = $input.first().json.body ?? $input.first().json ?? {};
const eventName = payload.eventName ?? payload.event_name ?? null;
const actorType = payload.actorType ?? payload.actor_type ?? payload.source ?? 'web';
const actorId =
  payload.actorId ??
  payload.actor_id ??
  payload.sessionId ??
  payload.session_id ??
  payload.externalUserId ??
  payload.external_user_id ??
  null;

const allowedEvents = new Set([
  'landing_view',
  'telegram_open_click',
  'chat_started',
  'lead_started',
  'lead_created',
]);

if (!allowedEvents.has(eventName)) {
  return [{ json: { ok: false, error: 'invalid_event', eventName } }];
}

await requestJson(`${$env.SUPABASE_URL}/rest/v1/event_logs`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    apikey: $env.SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${$env.SUPABASE_SERVICE_ROLE_KEY}`,
    Prefer: 'return=representation',
  },
  body: {
    event_name: eventName,
    actor_type: actorType,
    actor_id: actorId,
    properties: payload,
  },
});

return [{ json: { ok: true, eventName } }];
""".strip()


WEB_CHAT_CODE = r"""
const https = require('https');
const { URL, URLSearchParams } = require('url');

function requestJson(url, options = {}) {
  const parsedUrl = new URL(url);
  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        protocol: parsedUrl.protocol,
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 443,
        path: `${parsedUrl.pathname}${parsedUrl.search}`,
        method: options.method ?? 'GET',
        headers: options.headers ?? {},
      },
      (response) => {
        let raw = '';
        response.on('data', (chunk) => {
          raw += chunk;
        });
        response.on('end', () => {
          let data = null;
          if (raw) {
            try {
              data = JSON.parse(raw);
            } catch {
              data = raw;
            }
          }
          if (response.statusCode >= 200 && response.statusCode < 300) {
            resolve(data);
            return;
          }
          reject(new Error(typeof data === 'string' ? data : JSON.stringify(data)));
        });
      },
    );

    request.on('error', reject);

    if (options.body !== undefined) {
      request.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
    }

    request.end();
  });
}

const payload = $input.first().json.body ?? $input.first().json ?? {};
const message = String(payload.message ?? '').trim();
const sessionId = String(
  payload.sessionId ??
    payload.session_id ??
    payload.externalUserId ??
    payload.external_user_id ??
    `web-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`,
);
const patientName = payload.patientName ?? payload.patient_name ?? null;

if (!message) {
  return [{ json: { answer: 'Пожалуйста, напишите вопрос текстом.', conversationId: null, leadCreated: false } }];
}

const supabaseHeaders = {
  'Content-Type': 'application/json',
  apikey: $env.SUPABASE_SERVICE_ROLE_KEY,
  Authorization: `Bearer ${$env.SUPABASE_SERVICE_ROLE_KEY}`,
};

async function supabase(path, options = {}) {
  return requestJson(`${$env.SUPABASE_URL}${path}`, {
    ...options,
    headers: {
      ...supabaseHeaders,
      ...(options.headers ?? {}),
    },
  });
}

async function insertEvent(eventName, properties = {}) {
  await supabase('/rest/v1/event_logs', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: {
      event_name: eventName,
      actor_type: 'web',
      actor_id: sessionId,
      properties,
    },
  });
}

async function insertMessage(conversationId, role, text, messageType = 'text') {
  await supabase('/rest/v1/messages', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: {
      conversation_id: conversationId,
      role,
      message_text: text,
      message_type: messageType,
    },
  });
}

const conversationParams = new URLSearchParams({
  source: 'eq.web',
  external_user_id: `eq.${sessionId}`,
  select: 'id,source,external_user_id,patient_name,telegram_username,created_at',
  limit: '1',
});

let conversation = await supabase(`/rest/v1/conversations?${conversationParams.toString()}`, {
  method: 'GET',
});

conversation = Array.isArray(conversation) ? conversation[0] : conversation;
let conversationCreated = false;

if (!conversation) {
  const created = await supabase('/rest/v1/conversations', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: {
      source: 'web',
      external_user_id: sessionId,
      patient_name: patientName,
      telegram_username: null,
    },
  });
  conversation = Array.isArray(created) ? created[0] : created;
  conversationCreated = true;
}

if (conversationCreated) {
  await insertEvent('chat_started', {
    source: 'web',
    sessionId,
    patientName,
  });
}

await insertMessage(conversation.id, 'user', message);

let matches = [];
let context = '';

try {
  const embeddingData = await requestJson('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${$env.OPENAI_API_KEY}`,
    },
    body: {
      model: 'text-embedding-3-small',
      input: message,
    },
  });

  const embedding = embeddingData?.data?.[0]?.embedding;
  if (Array.isArray(embedding)) {
    const rpcMatches = await supabase('/rest/v1/rpc/match_knowledge_chunks', {
      method: 'POST',
      body: {
        query_embedding: embedding,
        match_count: 5,
        category_filter: null,
      },
    });

    matches = Array.isArray(rpcMatches) ? rpcMatches : [];
    context = matches
      .map((item, index) => `[${index + 1}] ${item.title ?? 'Документ'}\n${item.chunk_text ?? ''}`)
      .join('\n\n');
  }
} catch (error) {
  context = '';
}

const systemPrompt = [
  'Ты AI-помощник администратора клиники.',
  'Ты отвечаешь только на административные вопросы: цены, режим работы, подготовка к визиту, правила записи и сбор контактов.',
  'Ты не ставишь диагнозы и не даешь медицинские рекомендации как врач.',
  'Если в контексте не хватает фактов, честно говори, что это нужно уточнить у администратора.',
  context ? `Контекст из базы знаний:\n${context}` : 'Контекст из базы знаний пока пуст.',
].join('\n\n');

let answer = 'Извините, сейчас не получилось подготовить ответ. Попробуйте еще раз чуть позже.';

try {
  const chatData = await requestJson('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${$env.OPENAI_API_KEY}`,
    },
    body: {
      model: 'gpt-4o-mini',
      temperature: 0.2,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: message },
      ],
    },
  });

  answer = chatData?.choices?.[0]?.message?.content?.trim() || answer;
} catch (error) {
  answer = 'Не удалось обратиться к модели. Попробуйте позже.';
}

const leadIntent = /(запис|заявк|прием|приём|консультац|перезвон|оставить контакт)/i.test(message);
const phoneMatch = message.match(/(?:\+7|8)[\s\-()]*\d[\d\s\-()]{8,}/);
const nameMatch = message.match(/меня зовут\s+([A-Za-zА-Яа-яЁё\-]+)/i);
let leadCreated = false;

if (leadIntent) {
  await insertEvent('lead_started', {
    source: 'web',
    sessionId,
    message,
  });
}

if (leadIntent && phoneMatch) {
  const leadPayload = {
    patient_name: nameMatch?.[1] ?? patientName,
    phone: phoneMatch[0],
    telegram_username: null,
    source: 'web',
    service_interest: message.slice(0, 180),
    desired_date: null,
    notes: message,
    status: 'new',
  };

  await supabase('/rest/v1/leads', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: leadPayload,
  });

  await insertEvent('lead_created', {
    source: 'web',
    sessionId,
    phone: phoneMatch[0],
  });

  leadCreated = true;

  if (!/заявк/i.test(answer)) {
    answer += '\n\nЯ зафиксировал заявку и передал ее администратору клиники.';
  }
}

await insertMessage(conversation.id, 'assistant', answer);

return [
  {
    json: {
      answer,
      conversationId: conversation.id,
      leadCreated,
      matchesFound: matches.length,
    },
  },
];
""".strip()


KNOWLEDGE_INGEST_CODE = r"""
const https = require('https');
const { URL } = require('url');

function requestJson(url, options = {}) {
  const parsedUrl = new URL(url);
  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        protocol: parsedUrl.protocol,
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 443,
        path: `${parsedUrl.pathname}${parsedUrl.search}`,
        method: options.method ?? 'GET',
        headers: options.headers ?? {},
      },
      (response) => {
        let raw = '';
        response.on('data', (chunk) => {
          raw += chunk;
        });
        response.on('end', () => {
          let data = null;
          if (raw) {
            try {
              data = JSON.parse(raw);
            } catch {
              data = raw;
            }
          }
          if (response.statusCode >= 200 && response.statusCode < 300) {
            resolve(data);
            return;
          }
          reject(new Error(typeof data === 'string' ? data : JSON.stringify(data)));
        });
      },
    );

    request.on('error', reject);

    if (options.body !== undefined) {
      request.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
    }

    request.end();
  });
}

const payload = $input.first().json.body ?? $input.first().json ?? {};
const title = String(payload.title ?? '').trim();
const category = payload.category ? String(payload.category).trim() : null;
const originalText = String(payload.text ?? '').trim();

if (!title || !originalText) {
  return [{ json: { ok: false, error: 'title_and_text_required' } }];
}

function chunkText(text, size = 850, overlap = 140) {
  const chunks = [];
  let cursor = 0;
  let chunkIndex = 0;

  while (cursor < text.length) {
    const end = Math.min(cursor + size, text.length);
    const chunk = text.slice(cursor, end).trim();

    if (chunk) {
      chunks.push({
        chunk_text: chunk,
        metadata: {
          chunk_index: chunkIndex,
          source_title: title,
          category,
        },
      });
    }

    if (end === text.length) {
      break;
    }

    cursor = Math.max(end - overlap, cursor + 1);
    chunkIndex += 1;
  }

  return chunks;
}

const supabaseHeaders = {
  'Content-Type': 'application/json',
  apikey: $env.SUPABASE_SERVICE_ROLE_KEY,
  Authorization: `Bearer ${$env.SUPABASE_SERVICE_ROLE_KEY}`,
};

async function supabase(path, options = {}) {
  return requestJson(`${$env.SUPABASE_URL}${path}`, {
    ...options,
    headers: {
      ...supabaseHeaders,
      ...(options.headers ?? {}),
    },
  });
}

const documentInsert = await supabase('/rest/v1/knowledge_documents', {
  method: 'POST',
  headers: { Prefer: 'return=representation' },
  body: {
    title,
    category,
    original_text: originalText,
  },
});

const documentRecord = Array.isArray(documentInsert) ? documentInsert[0] : documentInsert;
const chunks = chunkText(originalText);

const embeddingData = await requestJson('https://api.openai.com/v1/embeddings', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${$env.OPENAI_API_KEY}`,
  },
  body: {
    model: 'text-embedding-3-small',
    input: chunks.map((item) => item.chunk_text),
  },
});

const embeddings = embeddingData?.data ?? [];

const rows = chunks.map((chunk, index) => ({
  document_id: documentRecord.id,
  chunk_text: chunk.chunk_text,
  embedding: `[${(embeddings[index]?.embedding ?? []).join(',')}]`,
  metadata: chunk.metadata,
}));

if (rows.length) {
  await supabase('/rest/v1/knowledge_chunks', {
    method: 'POST',
    headers: { Prefer: 'return=representation' },
    body: rows,
  });
}

await supabase('/rest/v1/event_logs', {
  method: 'POST',
  headers: { Prefer: 'return=representation' },
  body: {
    event_name: 'knowledge_document_ingested',
    actor_type: 'system',
    actor_id: documentRecord.id,
    properties: {
      title,
      category,
      chunksCreated: rows.length,
    },
  },
});

return [{ json: { ok: true, documentId: documentRecord.id, chunksCreated: rows.length } }];
""".strip()


def n8n_request(cookie: str, method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        f"{N8N_BASE_URL}{path}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie,
        },
        method=method,
    )
    with urllib.request.urlopen(request) as response:
        raw = response.read().decode()
    return json.loads(raw) if raw else {}


def login() -> str:
    if not N8N_EMAIL or not N8N_PASSWORD:
        print("Set N8N_EMAIL and N8N_PASSWORD first.", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps(
        {
            "emailOrLdapLoginId": N8N_EMAIL,
            "password": N8N_PASSWORD,
        }
    ).encode()

    request = urllib.request.Request(
        f"{N8N_BASE_URL}/rest/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        cookies = response.headers.get_all("Set-Cookie") or []

    for cookie in cookies:
        if cookie.startswith("n8n-auth="):
            return cookie.split(";", 1)[0]

    raise RuntimeError("Could not extract n8n-auth cookie")


def build_workflow(name: str, path: str, js_code: str) -> dict:
    return {
        "name": name,
        "settings": {},
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": path,
                    "responseMode": "lastNode",
                },
                "id": "Webhook_1",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [260, 300],
                "webhookId": path,
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "language": "javaScript",
                    "jsCode": js_code,
                },
                "id": "Code_1",
                "name": "Code",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [520, 300],
            },
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "Code", "type": "main", "index": 0}]],
            }
        },
    }


def upsert_workflow(cookie: str, name: str, path: str, js_code: str) -> tuple[str, str]:
    workflows = n8n_request(cookie, "GET", "/rest/workflows").get("data", [])
    existing = next((workflow for workflow in workflows if workflow["name"] == name), None)
    payload = build_workflow(name, path, js_code)

    if existing:
        detail = n8n_request(cookie, "GET", f"/rest/workflows/{existing['id']}")["data"]
        payload["versionId"] = detail["versionId"]
        response = n8n_request(cookie, "PATCH", f"/rest/workflows/{existing['id']}", payload)
        workflow_id = response["data"]["id"]
    else:
        response = n8n_request(cookie, "POST", "/rest/workflows", payload)
        workflow_id = response["data"]["id"]

    detail = n8n_request(cookie, "GET", f"/rest/workflows/{workflow_id}")["data"]
    n8n_request(
        cookie,
        "POST",
        f"/rest/workflows/{workflow_id}/activate",
        {"versionId": detail["versionId"]},
    )
    return name, workflow_id


def main() -> None:
    cookie = login()
    definitions = [
        ("public-event", "public-event", PUBLIC_EVENT_CODE),
        ("web-chat", "web-chat", WEB_CHAT_CODE),
        ("knowledge-ingest", "knowledge-ingest", KNOWLEDGE_INGEST_CODE),
    ]

    for name, path, code in definitions:
        deployed_name, workflow_id = upsert_workflow(cookie, name, path, code)
        print(f"DEPLOYED {deployed_name} {workflow_id}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        print(body or str(error), file=sys.stderr)
        raise
