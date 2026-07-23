---
phase: 8
title: "Hardening Demo"
status: pending
priority: P1
effort: "4d"
dependencies: [2, 3, 4, 5, 6, 7]
---

# Phase 8: Hardening Demo

## Overview
Tuần 4: load test KPI, failure drills, ops dashboard, backup, demo script. Đích: demo full flow thuyết phục + hệ thống sống sót qua restart/failure cơ bản.

## Requirements
- Functional: demo script end-to-end (sensor→alarm→notify, command→ack, camera live, history query); backup/restore PG.
- Non-functional: KPI đo được bằng số: telemetry ≤5s, event ≤2s, command ≤5s, 2.000 msg/s sustained 30 phút, 50 WS clients.

## Architecture
- Đo E2E: simulator gắn timestamp publish → so với timestamp WS client nhận (synthetic probe đơn giản, in kết quả p50/p95/p99).
- Ops: Grafana + postgres_exporter + redis_exporter + EMQX built-in metrics (Prometheus endpoint) — 1 dashboard ops duy nhất, không LGTM stack.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/cmd/probe/main.go` (synthetic E2E latency probe), `deploy/scripts/backup_pg.sh` (pg_dump nightly + restore verify), `deploy/scripts/demo_seed.sh`
- Create: `infra/edge/grafana/dashboards/ops.json`, `docs runbook`: `plans/260723-1450-poc-onprem-iiot-modular-monolith/reports/ops-runbook.md`
- Create: `README.md` (root — quickstart ≤10 bước, trỏ vào `apps/`)
- Modify: `infra/edge/docker-compose.yml` (exporters + resource limits)

## Implementation Steps
1. Load test: simulator 2k msg/s × 30 phút + 50 WS clients (k6) + history query song song → thu p95/p99, batcher lag, PG stats.
2. Failure drills: (a) kill app-worker → restart → không mất notification, EMQX session giữ QoS1; (b) kill PG → app reconnect + backoff, không crash loop; (c) simulator backfill mode sau khi "mất mạng" → data đủ, không đẩy realtime; (d) kill EMQX → app reconnect, simulator (gateway thật sẽ buffer) resume.
3. Retention verify: chèn data >30d → policy xóa; aggregate còn.
4. Backup script + restore drill 1 lần vào staging DB, checksum row count.
5. Grafana ops dashboard: ingest rate, batcher lag, EMQX connections/queue, PG connections/slow queries, Redis mem, alarm/notify counters, probe latency.
6. Fix bugs từ drills; freeze feature từ đầu tuần 4.
7. Demo script viết + tổng duyệt: kịch bản 15 phút (telemetry → vượt ngưỡng → alarm + Telegram → operator ack → bật lộ chiếu sáng → ack → camera live + AI event → history/report view).

## Success Criteria
- [ ] KPI pass có số liệu: telemetry p95 ≤5s, event p95 ≤2s, command p95 ≤5s @ 2k msg/s
- [ ] 4 failure drills pass, ghi kết quả vào runbook
- [ ] Restore drill pass (row count khớp)
- [ ] Demo 15 phút chạy trơn 2 lần liên tiếp trên máy demo sạch
- [ ] README quickstart: người ngoài team dựng được hệ thống ≤1 giờ

## Risk Assessment
- Tuần 4 bị ăn bởi feature trễ → freeze cứng: feature chưa xong = cắt khỏi demo, không kéo dài.
- KPI fail ở load test → ưu tiên fix ingest/WS trước (core value); camera/history có thể degrade (giảm concurrent stream, tăng bucket).
