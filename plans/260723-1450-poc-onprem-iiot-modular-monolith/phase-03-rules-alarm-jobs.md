---
phase: 3
title: "Rules Alarm Jobs"
status: pending
priority: P1
effort: "4d"
dependencies: [2]
---

# Phase 3: Rules Alarm Jobs

## Overview
Device registry + rule engine ngưỡng + alarm lifecycle + PG job queue cho notification durable (Telegram/email) + retention policy.

## Requirements
- Functional: CRUD device + alarm rule; đánh giá ngưỡng trên stream ingest (in-process, cùng worker role); alarm open→ack→close; notification retry được, không mất khi restart.
- Non-functional: event/alarm E2E ≤2s (sensor → alarm record + WS push); notification enqueue cùng transaction với alarm insert.

## Architecture
- Rule eval subscribe bus in-process (KHÔNG qua Redis — cùng process với ingest trong role worker, giữ KPI ≤2s).
- Alarm dedup: 1 alarm OPEN duy nhất per (rule, device); vượt ngưỡng tiếp khi đang open → update last_seen_value, không tạo mới.
- Job queue: **River** (riverqueue.com — Go-native, PG-backed) <!-- Updated: Validation Session 1 - chốt River thay vì tự viết SKIP LOCKED; tiết kiệm 2-3 ngày (retry/backoff/scheduler sẵn), transactional enqueue native -->. Migration schema do River CLI sinh.
- Duration condition (ví dụ "CPU >80% trong 5 phút"): POC chỉ hỗ trợ threshold tức thời + optional `min_duration_s` bằng state in-memory per rule.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/internal/device/registry.go`, `apps/backend/internal/rules/engine.go`, `apps/backend/internal/rules/alarm_lifecycle.go`
- Create: `apps/backend/internal/jobs/river_client.go`, `apps/backend/internal/jobs/notify_telegram.go`, `apps/backend/internal/jobs/notify_email.go`
- Create: `apps/backend/migrations/0003_devices_rules_alarms.up.sql` (devices, alarm_rules, alarms), `apps/backend/migrations/0004_jobs.up.sql` (River schema qua `river migrate-get`)
- Create: `apps/backend/migrations/0005_retention.up.sql` (retention policy raw 30d + continuous aggregate 1h/1d giữ 1 năm)
- Modify: `apps/backend/cmd/app/main.go` (wire rules + jobs vào role worker), `apps/backend/internal/ingest/consumer.go` (wire heartbeat → devices.last_seen)

## Implementation Steps
1. Migration devices (id, gateway_id, subsys, node, name, type, unit, meta jsonb, last_seen), alarm_rules (device_id, metric, operator, threshold, severity, min_duration_s), alarms (rule_id, device_id, state, opened_at, acked_by/at, closed_at, peak_value).
2. Device registry store + seed từ tag list YAML (cùng file simulator dùng — 1 nguồn sự thật).
3. Rule engine: load rules vào memory, reload khi có thay đổi (poll 30s hoặc pg NOTIFY); eval mỗi TelemetryPoint; state machine alarm.
4. Alarm insert + enqueue notification job CÙNG transaction; publish AlarmEvent lên bus (Redis) cho WS.
5. Job worker: River worker (InsertTx cho transactional enqueue), max attempts 5, backoff mặc định River.
6. Telegram bot (token qua env) + SMTP email; template message tiếng Việt (site, device, metric, giá trị, ngưỡng, severity).
7. Retention + continuous aggregates; verify TTL bằng cách chèn data cũ.
8. Report PDF: chỉ stub endpoint trả 501 (scope cut — production làm).

## Success Criteria
- [ ] Simulator bơm giá trị vượt ngưỡng → alarm OPEN + Telegram message ≤2s (đo log timestamp)
- [ ] Kill worker giữa chừng → restart → notification vẫn gửi (job durable)
- [ ] Ack/close alarm qua SQL/API thay đổi state đúng; không duplicate alarm khi giá trị dao động quanh ngưỡng
- [ ] Continuous aggregate 1h trả kết quả đúng với raw
- [ ] Unit tests rule engine (biên: đúng ngưỡng, NaN, quality=lỗi → không eval) pass

## Risk Assessment
- Rule engine phình → giữ ĐÚNG threshold + min_duration; mọi yêu cầu phức tạp hơn (biểu thức, multi-metric) → ghi vào backlog production, KHÔNG làm POC.
- Telegram rate limit → gom message theo batch 30s nếu >20 alarm/phút.
