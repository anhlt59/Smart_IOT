# PM Report — POC Phase 1 Foundation Compose Skeleton: COMPLETED

**Plan:** `plans/260723-1450-poc-onprem-iiot-modular-monolith/` · **Date:** 2026-07-23 · **Executor:** /ck:cook

## Status

| Phase | Status | Progress |
|---|---|---|
| 1 Foundation Compose Skeleton | ✅ Completed 2026-07-23 | 5/5 success criteria verified E2E |
| 2–8 | Pending | Unblocked: P2 (Dev 1), P6 (Dev 5) partially — contracts frozen |

Plan status: pending → **in-progress** (1/8 phases done).

## Delivered

- `apps/backend/` — Go 1.26 module: `cmd/app` (--role=api|ingest|worker|all, graceful shutdown), `internal/config`, `internal/events` (bus: ordered per-subscription delivery + Redis bridge, 11 unit tests -race pass), `migrations/0001_users` (seed admin, bcrypt), `api/openapi.yaml` (contract frozen: auth/devices/telemetry/alarms/commands/cameras + WS payload map), Dockerfile
- `infra/edge/` — compose 7 containers pinned (timescaledb 2.17.2-pg16, emqx 5.8.4, redis 7.4.2, mediamtx 1.11.3, grafana 11.4.0) + migrate one-shot; emqx auth bootstrap + ACL least-privilege; postgres initdb (timescaledb ext + grafana_ro read-only role); grafana datasource provisioning; `.env.example` template flow
- Root `Makefile` (up/down/test/lint/migrate/run-all) + `.github/workflows/ci.yml` (build/vet/test -race/golangci-lint + compose config validation)

## Verification (live E2E, clean slate `down -v` → `make up`)

- 7/7 containers healthy ~25s; migrate Exited(0)
- api + worker: postgres/redis/mqtt connected, ready; /healthz 200 (checks all 3 deps)
- psql: admin seed + `crypt('ChangeMe123!', pass_hash)` = true; grafana_ro SELECT ok / INSERT denied
- SIGTERM graceful shutdown clean; unit tests 11/11 -race, deterministic (tester agent 2× run)
- Secrets: only `.example` templates tracked (`git check-ignore` verified)

## Code review (code-reviewer agent): DONE_WITH_CONCERNS → all actionable items fixed

Fixed: H1 (loopback bind PG/Redis/MediaMTX-API), H2+M5 (bus ordered serial delivery + documented semantics + ordering test), M1/M2/L1 (PG password single-source, explicit env, local-dev defaults), M3+L6 (OpenAPI ↔ event types reconciled, WS schemas explicit), M4 (plan-phase refs stripped from code), M6 (grafana_ro), L4/L5/L7/L8 (slog shutdown line, .dockerignore, make guards, CI compose validate).
Deferred (observational): L2 (Redis unsub asymmetry — documented), L3 (MQTT client-id per-replica — Phase 2 note).

## Incidents fixed during E2E

1. EMQX bind-mounted emqx.conf thiếu `node{}` block → exit 127 crash-loop
2. `durable_sessions` + `builtin_local` đòi `discovery_strategy = singleton`
3. Host port 5432 bị chiếm (container khác) → PG map 127.0.0.1:5433
4. postgres healthcheck flap trong initdb restart → TCP check + `start_period: 30s`
5. initdb .sh thiếu exec bit → "bad interpreter" (chmod +x, git giữ bit)

## Unresolved questions

1. GH Actions run cần push mới confirm CI green trên runner (local-equivalent đã pass).
2. EMQX 5.8 durable_sessions có cover `$share` subscription đầy đủ? → verify đầu Phase 2 trước khi tin buffered delivery qua shared sub (reviewer L3).
3. 3 quyết định ⏳ pending user từ validation (Q2 simulator-only, Q3 River, Q4 UI stack) — Q3/Q4 cần chốt trước Phase 3/7.
