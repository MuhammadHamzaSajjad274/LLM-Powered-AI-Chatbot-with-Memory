# API and Webhooks

FlowBoard provides a REST API and outbound webhooks for integrating with custom tools. API access requires Pro plan or above; webhooks require Business plan.

## Authentication

Generate a personal API token under **Account Settings → API Tokens**. Include it in the `Authorization: Bearer <token>` header. Tokens inherit your user permissions—you cannot access boards you aren't a member of. Rate limits: 100 requests/minute on Pro, 1000/minute on Business.

## Core Endpoints

- `GET /v1/boards` — List accessible boards
- `GET /v1/boards/{id}/tasks` — List tasks with pagination (max 100 per page)
- `POST /v1/boards/{id}/tasks` — Create task (JSON body: title, column_id, assignee_id, etc.)
- `PATCH /v1/tasks/{id}` — Update task fields
- `GET /v1/tasks/{id}/comments` — List comments

Full OpenAPI spec: `https://api.flowboard.io/v1/openapi.json`

## Webhooks

Configure outbound webhooks under **Settings → Webhooks**. Supported events: `task.created`, `task.updated`, `task.moved`, `task.deleted`, `comment.added`. Payloads are JSON with event type, timestamp, and task snapshot. FlowBoard signs payloads with HMAC-SHA256 in the `X-FlowBoard-Signature` header—verify using your webhook secret.

## Retry Policy

Failed webhook deliveries (non-2xx response) retry with exponential backoff: 1 min, 5 min, 30 min, 2 hours, 24 hours. After five failures, the webhook is disabled and admins receive email notification.

## Pagination and Filtering

List endpoints support `cursor` pagination and filters: `assignee_id`, `column_id`, `label`, `updated_since` (ISO 8601). Example: `GET /v1/boards/abc123/tasks?updated_since=2026-01-01T00:00:00Z&limit=50`.

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid or expired token |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 422 | Validation error (see `details` array) |

## Best Practices

Use idempotency keys (`Idempotency-Key` header) on POST requests to safely retry creates. Poll `updated_since` instead of full board exports for sync jobs. Store tokens in secrets managers, never client-side code.
