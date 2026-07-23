# Journal 2026-07-23 — POC pivot: On-Premise Only + Modular Monolith

## Bối cảnh
User đổi hướng POC (xác nhận trực tiếp 14:50): bỏ hoàn toàn Cloud Platform, chỉ on-premise, tập trung thu thập dữ liệu + giám sát + điều khiển IIoT. **POC-only** — production hybrid (system-architecture v1.0, D1-D7) giữ nguyên, KHÔNG sửa.

## Quyết định chốt (user confirm)
1. **Phạm vi:** POC-only; 1 site; single tenant; Go stack; 5 dev / 1 tháng; camera TRONG scope; dashboard = web UI React.
2. **Kiến trúc app:** Modular Monolith Go — 1 binary, roles `api|ingest|worker|all`. Loại microservices (thuế phân tán vô nghĩa 1 site) và full-D2-on-prem (sai đề: Kafka/ClickHouse vốn chỉ ở cloud; site production dùng PG+TSDB+Redis per `system-architecture.md:83`).
3. **Async:** EMQX = broker DUY NHẤT (Interface Agreement giữ nguyên). Hot path (ingest→rules→WS) in-process channels (KPI event ≤2s). Durable jobs = River trên PG (validation session 1). Cross-role = Redis pub/sub. Kafka/NATS/RabbitMQ/Redis Streams: defer.
4. **Storage:** PG + TimescaleDB (align production on-prem design, không phải tạm). ClickHouse vẫn là production cloud.
5. **Seams lên production:** EMQX bridge (bật là nối cloud), `TelemetryStore`/`EventBus`/`Authenticator` interfaces, topic giữ `{tenant}/{park}`.

## Sản phẩm phiên
- Brainstorm: `plans/reports/brainstorm-260723-1438-poc-onprem-only-architecture-modular-monolith-vs-microservices-report.md` (3 phương án + trade-off + sync/async split + so sánh 6 broker)
- Plan 8 phases: `plans/260723-1450-poc-onprem-iiot-modular-monolith/` (active plan; tasks #1-8 hydrated với dependency chain; validate session 1 xong, verification 10/10, consistency sweep 0 contradiction)

## Ghi chú / pending
- Cấu trúc repo: user chốt (15:19) **`apps/backend/` + `infra/edge/` (compose, emqx, postgres, grafana, mediamtx) + `deploy/` + `Makefile` root** — propagated 8 phase files; web UI đặt `apps/web/` (Claude bổ sung theo convention, chờ user confirm tên).
- 3 quyết định validate còn dùng default do user AFK (⏳ trong Validation Log): simulator only · River · Tailwind+shadcn+ECharts → user confirm trước Phase 1.
- Lesson: `ck` CLI bị shell alias che (trỏ GNU Make) — gọi bằng absolute path `/Users/anhlt/.nvm/versions/node/v24.18.0/bin/ck`.
