---
phase: 1
title: "Foundation Compose Skeleton"
status: completed
completed: "2026-07-23"
priority: P1
effort: "3d"
dependencies: []
---

# Phase 1: Foundation Compose Skeleton

## Overview
Khung dự án chạy được ngày 3: Go module + role flags, Docker Compose 7 containers, migrations, config, CI. Chốt contracts (OpenAPI skeleton + event types) để 5 dev song song từ tuần 1.

## Requirements
- Functional: `docker compose up` → EMQX + PG/Timescale + Redis + MediaMTX + Grafana + app (api, worker) chạy, healthcheck pass.
- Non-functional: 1 lệnh setup từ zero ≤1 giờ; version pin toàn bộ images (không `latest` — bài học Watchtower).

## Architecture
- **Binary duy nhất** `cmd/app`: flag `--role=api|ingest|worker|all` (worker = ingest + rules + jobs chung process để rule eval in-process, KPI event ≤2s).
- Cross-role communication: Redis pub/sub (`internal/events` bus: in-process channels trong 1 role + Redis bridge giữa roles).
- Config: env vars + file `.env.example` (KHÔNG commit `.env`).

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/go.mod`, `apps/backend/cmd/app/main.go` (role dispatch), `apps/backend/internal/config/config.go`
- Create: `infra/edge/docker-compose.yml`, `infra/edge/emqx/emqx.conf` (auth username/password POC, ACL prefix `v1/{tenant}/{park}/#`), `infra/edge/mediamtx/mediamtx.yml`, `infra/edge/postgres/` (init conf: timescaledb preload, tuning), `infra/edge/grafana/` (provisioning)
- Create: `apps/backend/migrations/0001_users.up.sql` (users: id, username, pass_hash bcrypt, role admin|operator|viewer), seed admin
- Create: `Makefile` (build/test/lint/migrate/compose-up), `.github/workflows/ci.yml` (root — GitHub yêu cầu; `working-directory: apps/backend`), `apps/backend/api/openapi.yaml` (skeleton — chốt contract cho Dev 3+4)
- Create: `apps/backend/internal/events/bus.go` (interface EventBus + types: TelemetryPoint, AlarmEvent, CommandState)

## Implementation Steps
1. Layout theo structure user chốt: `apps/backend/` (`go mod init` tại đây — chứa `cmd/`, `internal/`, `migrations/`, `api/`) · `apps/web/` (React, Phase 7) · `infra/edge/` (docker-compose.yml + emqx/ + postgres/ + grafana/ + mediamtx/) · `deploy/` (scripts vận hành) · `Makefile` root · root còn lại giữ docs, plans, `.github/`, README.
2. `cmd/app` với role flags; graceful shutdown (context + signal).
3. Compose: `timescale/timescaledb:2.x-pg16`, `emqx/emqx:5.x`, `redis:7.x`, `bluenviron/mediamtx:1.x`, `grafana/grafana:11.x`, `app-api` (`--role=api`), `app-worker` (`--role=worker`); healthchecks + restart policy + volumes.
4. golang-migrate + migration đầu; seed admin user.
5. EMQX: tạo user cho gateway/simulator + app consumer; ACL theo topic prefix; persistent session enable.
6. `internal/events`: định nghĩa types + interface (Publish/Subscribe), impl in-process channels + Redis pub/sub bridge.
7. OpenAPI skeleton: auth, devices, telemetry, alarms, commands, cameras — đủ path/schema chính để Dev 4 mock.
8. CI: golangci-lint + go test + go build.

## Success Criteria
- [x] `make up` từ máy sạch → 7 containers healthy ≤10 phút (verified: clean `down -v` → healthy ~25s)
- [x] `app --role=all` kết nối EMQX + PG + Redis, log ready (verified: api + worker logs; /healthz 200 check cả 3 deps)
- [x] Migration + seed chạy tự động; login admin qua psql verify được (verified: `pass_hash = crypt('ChangeMe123!', pass_hash)` → true)
- [x] CI green; OpenAPI skeleton merge — Dev 3/4 bắt đầu từ contract này (CI local-equivalent: build+vet+gofmt+test -race pass; GH run cần push)
- [x] 0 secret plaintext trong Git (`.env.example` + `users-bootstrap.csv.example` only; bản thật gitignored, verify `git check-ignore`)

## Completion Notes (2026-07-23, contract deltas cho Dev 2-5)
- **Bus semantics (code-review fix):** per-subscription serial delivery ĐÚNG THỨ TỰ publish, queue 1024, đầy → Publish block (backpressure). Publish lỗi Redis SAU KHI đã deliver local — KHÔNG retry (godoc `internal/events/bus.go`).
- **WS payload ≠ REST shape:** WS đẩy `TelemetryPoint | AlarmEvent | CommandStateEvent` (khớp `internal/events`); REST trả `Alarm | Command` (persisted). Map trong `x-websocket` cuối openapi.yaml.
- **EMQX 5.8.4 gotchas:** mount emqx.conf phải có `node{}` block; `durable_sessions` đòi `cluster.discovery_strategy = singleton`; users CSV chỉ import lần đầu (fresh volume).
- **Ports:** PG host 127.0.0.1:5433 (5432 hay bị chiếm), Redis/MediaMTX-API loopback-only; MQTT 1883 + media + UI mở LAN.
- **Grafana:** datasource dùng role read-only `grafana_ro` (tạo bởi postgres/initdb, cần exec bit trên file .sh).
- **Simulator (`cmd/simulator`) chưa tạo** — thuộc Phase 2 per plan; EMQX user `gateway1` + ACL đã sẵn.

## Risk Assessment
- Contract chốt muộn → 5 dev block nhau. Mitigation: OpenAPI + event types là deliverable ngày 2-3, review chung cả team.
- EMQX config lạ với team → dùng dashboard EMQX (port 18083) debug; docs link trong README.
