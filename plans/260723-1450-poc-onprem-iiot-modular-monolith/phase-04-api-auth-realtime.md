---
phase: 4
title: "API Auth Realtime"
status: pending
priority: P1
effort: "5d"
dependencies: [1, 2]
---

# Phase 4: API Auth Realtime

## Overview
REST API (Gin) + JWT/RBAC + WebSocket hub đẩy realtime cho web UI. Contract theo `apps/backend/api/openapi.yaml` chốt ở Phase 1.

## Requirements
- Functional: auth login; CRUD/query devices, telemetry latest/history, alarms list/ack/close; WS push telemetry last-value + alarm events; audit log cho mọi mutating request.
- Non-functional: API p95 <200ms (history query qua continuous aggregate); WS 50 client đồng thời; RBAC enforced mọi endpoint.

## Architecture
- `internal/auth`: JWT HS256 (secret env), bcrypt, middleware RBAC 3 role — interface `Authenticator` (seam swap Keycloak/OIDC production, KHÔNG hardcode JWT vào handlers).
- WS hub (`internal/api/ws`): subscribe Redis pub/sub `rt:telemetry`, `rt:alarm`, `rt:command` → fan-out theo subscription filter của client (park/subsys/device). Auth khi handshake (token query param hoặc header).
- History query: `time_bucket` trên aggregate khi range >24h, raw khi ≤24h.
- Audit: middleware ghi `audit_log(user, action, resource, payload, ts)` cho POST/PUT/DELETE.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/internal/api/router.go`, `apps/backend/internal/api/handlers_{auth,devices,telemetry,alarms}.go`, `apps/backend/internal/api/ws/hub.go`
- Create: `apps/backend/internal/auth/jwt.go`, `apps/backend/internal/auth/middleware.go`
- Create: `apps/backend/migrations/0006_audit_log.up.sql`
- Modify: `apps/backend/api/openapi.yaml` (hoàn thiện từ skeleton), `apps/backend/cmd/app/main.go` (wire role api)

## Implementation Steps
1. Router + middleware chain: recover, request log, auth, RBAC, audit.
2. Endpoints: `POST /auth/login` · `GET /devices` (+status từ last_seen) · `GET /devices/{id}/telemetry/latest` (Redis) · `GET /devices/{id}/telemetry/history?from&to&bucket` (Timescale) · `GET/POST /alarms`, `POST /alarms/{id}/ack|close` (operator+).
3. RBAC matrix: viewer=GET only; operator=+ack/close+command; admin=+CRUD devices/rules/users.
4. WS hub: register/unregister, ping/pong, filter theo subscribe message `{"parks":[],"devices":[]}`; backpressure: drop-oldest per client buffer 100.
5. Integration test: docker compose + simulator → gọi API + WS client assert nhận message.
6. Load: k6 hoặc vegeta — 50 VU đọc history + latest, p95 <200ms.

## Success Criteria
- [ ] OpenAPI cập nhật khớp implementation (CI lint openapi diff nếu kịp)
- [ ] Viewer không ack được alarm (403); mọi mutating request có audit row
- [ ] WS client nhận telemetry ≤5s từ lúc simulator publish (E2E qua ingest→Redis→WS)
- [ ] History 30 ngày bucket 1h trả <200ms p95 với 10M rows seed
- [ ] 50 WS clients đồng thời không drop connection trong 10 phút

## Risk Assessment
- WS fan-out chậm do 1 goroutine → per-client send goroutine + buffered channel ngay từ đầu.
- JWT secret rotate không có ở POC → ghi rõ trong runbook (production dùng Keycloak).
