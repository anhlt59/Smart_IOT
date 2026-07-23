---
phase: 2
title: "Ingest Pipeline"
status: pending
priority: P1
effort: "4d"
dependencies: [1]
---

# Phase 2: Ingest Pipeline

## Overview
Đường dữ liệu chính: EMQX → decode/validate theo Interface Agreement → batch insert TimescaleDB → Redis last-value + pub/sub. Kèm simulator bản tin (công cụ dev + demo + load test).

## Requirements
- Functional: consume `$share/ingest/v1/+/+/+/+/telemetry|event|heartbeat` QoS1; validate bản tin bắt buộc (NTP timestamp, gateway ID, sequence, backfill flag, quality flag); lưu hypertable; last-value vào Redis; publish normalized event lên bus.
- Non-functional: 2.000 msg/s sustained 1 node; batch window 1–5s; message invalid không làm crash pipeline.

## Architecture
- `internal/ingest`: paho MQTT client, shared subscription (scale consumer sau này chỉ cần thêm process — seam production).
- `internal/telemetry`: interface `TelemetryStore` (seam swap Kafka/ClickHouse khi lên cloud) + impl Timescale; schema narrow: `telemetry(time, device_id, metric, value float8, quality int2, backfill bool)`.
- Invalid message → bảng `ingest_dead_letter` (payload, reason, ts) — không drop im lặng.
- Backfill flag = true → insert bình thường nhưng KHÔNG publish realtime event (không tính KPI realtime — per IA).

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/internal/ingest/consumer.go`, `apps/backend/internal/ingest/decoder.go` (IA spec), `apps/backend/internal/ingest/batcher.go`
- Create: `apps/backend/internal/telemetry/store.go` (interface), `apps/backend/internal/telemetry/timescale_store.go`
- Create: `apps/backend/migrations/0002_telemetry.up.sql` (hypertable + index (device_id, time DESC) + dead_letter)
- Create: `apps/backend/cmd/simulator/main.go` (rate configurable, N devices, backfill mode, invalid-message mode)
- Modify: `apps/backend/cmd/app/main.go` (wire ingest vào role worker)

## Implementation Steps
1. Migration hypertable + `create_hypertable`, chunk interval 1 day; dead_letter table.
2. Decoder: JSON schema validate 5 trường bắt buộc + range check quality; unit test với fixtures (valid/thiếu trường/sai kiểu/backfill).
3. Batcher: gom theo window 2s hoặc 5.000 rows, `COPY`/multi-row INSERT; flush khi shutdown.
4. Redis: `HSET lastvalue:{device_id} {metric} {json}` + `PUBLISH rt:telemetry {normalized}`.
5. Heartbeat → update `devices.last_seen` (bảng devices tạo ở Phase 3 — tuần 1 dùng stub log, wire lại khi 0003 merge).
6. Simulator: đọc tag list YAML (mẫu theo 4 phân hệ ĐV3), publish đúng topic + IA fields; flag `--rate`, `--devices`, `--backfill`.
7. Perf test cục bộ: simulator 2k msg/s 10 phút — đo lag (EMQX dashboard + log batcher).

## Success Criteria
- [ ] Simulator 2.000 msg/s trong 10 phút: 0 message loss (đếm sequence), batcher lag <2s
- [ ] Message thiếu trường bắt buộc → dead_letter, pipeline sống
- [ ] Last-value đọc được từ Redis; event nhận được qua bus từ process khác (api role)
- [ ] Backfill message vào DB nhưng không đẩy realtime
- [ ] Unit tests decoder + batcher pass trong CI

## Risk Assessment
- PG chịu cả OLTP + timeseries → theo dõi `pg_stat_statements` từ tuần 1; ngưỡng thoát: batcher lag >5s ở 2k msg/s → tách tablespace/tune trước khi nghĩ tới đổi store.
- Sequence dedup phức tạp → POC chỉ đếm gap để báo metric, không dedup (production mới làm đầy đủ).
