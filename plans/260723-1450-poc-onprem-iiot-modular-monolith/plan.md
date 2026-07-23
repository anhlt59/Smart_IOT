---
title: "POC On-Premise Industrial IoT — Modular Monolith Go"
description: "POC on-prem only: thu thập dữ liệu, giám sát, điều khiển thiết bị IIoT. Modular Monolith Go + EMQX + PG/TimescaleDB + MediaMTX + React. 5 dev / 4 tuần."
status: in-progress
priority: P1
branch: "main"
tags: [poc, on-premise, iiot, golang, modular-monolith]
blockedBy: []
blocks: []
created: "2026-07-23T07:55:10.040Z"
createdBy: "ck:plan"
source: skill
---

# POC On-Premise Industrial IoT — Modular Monolith Go

## Overview

POC on-premise only (bỏ Cloud Platform — quyết định user 2026-07-23, POC-only, production hybrid giữ nguyên). Chức năng: thu thập telemetry qua MQTT, giám sát realtime + lịch sử, alarm + notification, điều khiển downlink whitelist, camera live view + AI event. 1 site, single tenant, ≤2.000 msg/s, ≤50 user local.

**Kiến trúc (chốt tại brainstorm):** Modular Monolith Go — 1 binary chạy role `api` / `ingest` / `worker` / `all`; EMQX là broker duy nhất; PostgreSQL + TimescaleDB (metadata + timeseries + job queue); Redis (last-value cache + pub/sub cross-role); MediaMTX (camera relay); React web UI; Grafana chỉ cho ops. Docker Compose ~7 containers (D7).

**Nguồn:** `plans/reports/brainstorm-260723-1438-poc-onprem-only-architecture-modular-monolith-vs-microservices-report.md` (đọc mục 5–8b trước khi code).

**Cấu trúc repo (user chốt 2026-07-23 15:19, POC docker-compose only):**
```
├── apps/
│   ├── backend/        # Go module: cmd/ (app, simulator, probe), internal/, migrations/, api/openapi.yaml
│   └── web/            # React dashboard (Vite) — bổ sung theo convention apps/, user confirm nếu muốn tên khác
├── infra/
│   └── edge/           # docker-compose.yml, emqx/, postgres/, grafana/, mediamtx/
├── deploy/             # scripts vận hành (backup_pg.sh, demo_seed.sh)
├── docs/  ·  plans/
├── Makefile            # root
└── .github/workflows/  # CI root, working-directory: apps/backend
```

## Phases

| Phase | Name | Status | Effort | Owner (dev) | Depends |
|-------|------|--------|--------|-------------|---------|
| 1 | [Foundation Compose Skeleton](./phase-01-foundation-compose-skeleton.md) | ✅ Completed 2026-07-23 | 3d | Dev 5 (+all) | — |
| 2 | [Ingest Pipeline](./phase-02-ingest-pipeline.md) | Pending | 4d | Dev 1 | 1 |
| 3 | [Rules Alarm Jobs](./phase-03-rules-alarm-jobs.md) | Pending | 4d | Dev 2 | 2 |
| 4 | [API Auth Realtime](./phase-04-api-auth-realtime.md) | Pending | 5d | Dev 3 | 1, 2 |
| 5 | [Control Downlink](./phase-05-control-downlink.md) | Pending | 3d | Dev 3 | 4 |
| 6 | [Camera Integration](./phase-06-camera-integration.md) | Pending | 4d | Dev 5 | 1, 2 |
| 7 | [Web UI Dashboard](./phase-07-web-ui-dashboard.md) | Pending | 8d | Dev 4 | 4 (contract từ tuần 1) |
| 8 | [Hardening Demo](./phase-08-hardening-demo.md) | Pending | 4d | All | 2–7 |

Phases chạy SONG SONG theo ownership (5 dev), không tuần tự — deps chỉ là điểm tích hợp. Tuần 1 exit: simulator → dashboard thô E2E. Tuần 4 exit: demo full flow.

## Key Constraints

- **Sticky:** D1 hardware ĐV3, D7 Docker Compose (KHÔNG K8s tại site). `docs/system-architecture.md` KHÔNG sửa (POC-only).
- **Interface Agreement giữ nguyên:** topic `v1/{tenant}/{park}/{subsys}/{node}/telemetry|event|heartbeat|cmd|cmd/ack`; bản tin bắt buộc: NTP timestamp, gateway ID, sequence, backfill flag, quality flag. Tenant/park cố định POC nhưng giữ trong topic/schema (seam production).
- **KPI:** telemetry E2E ≤5s · event/alarm ≤2s · command ack ≤5s · 2.000 msg/s sustained.
- **Scope cut (KHÔNG làm):** Kafka, ClickHouse, Keycloak/OIDC, Temporal, 2FA TOTP, PDF report (stub), multi-tenant isolation test, HA keepalived, VMS/recording (NVR lo).
- **Bắt buộc không cắt:** command whitelist + idempotency + app-level ack + audit trail; alarm notification durable (PG job queue).

## Dependencies

Không có plan nào khác đang mở (scan 2026-07-23). Cross-plan: none.

## Validation Log

### Session 1 — 2026-07-23
**Trigger:** `/ck:plan validate` sau khi tạo plan (user chọn ở post-plan handoff)
**Questions asked:** 4 (user AFK sau 60s → áp dụng option Recommended, đánh dấu ⏳ pending user confirm)

#### Verification Results
- Claims checked: 10 | Verified: 10 | Failed: 0 | Unverified: 0
- Tier: Reduced (repo greenfield docs-only — không có code symbols/paths; verify claims vs `docs/`)
- Verified vs nguồn: topic standard + IA fields (`system-architecture.md:149-153`), whitelist 9 lộ + PTZ (`:79`), QoS1 + app ack (`:152`), PG+TSDB+Redis on-prem (`:83`), KPI ≤5s/≤2s/≤5s + 50 user local (PDR mục 5), retention 30d/1y (PDR), D7 Compose, brainstorm report path.
- Failures: none

#### Questions & Answers

1. **[Architecture]** Code POC đặt ở đâu?
   - Options: Root repo này (Recommended) | Repo mới | Thư mục con
   - **Answer:** ✅ User recommend structure (15:19): `apps/backend/` + `infra/edge/` (compose, emqx, postgres, grafana, mediamtx) + `deploy/` + `Makefile` root
   - **Custom input (verbatim):** "POC chỉ sử dụng docker-compose tôi recommend sử dụng structure sau: apps/backend · infra/edge/{docker-compose.yml,emqx,postgres,grafana,mediamtx} · deploy · docs · Makefile"
   - **Rationale:** tách app code / infra config / deploy scripts; web UI đặt `apps/web/` theo convention apps (Claude bổ sung — user confirm); CI root `working-directory: apps/backend` — propagated toàn bộ 8 phase files
2. **[Assumptions]** Nguồn thiết bị demo?
   - Options: Simulator only (Recommended) | +1 ECU-1051 lab | Site ĐV3 thật
   - **Answer:** ⏳ Simulator only (default — EMQX username/password đủ; gateway thật để Phase A production)
3. **[Architecture]** Job queue PG: lib hay tự viết?
   - Options: River (Recommended) | Tự viết SKIP LOCKED
   - **Answer:** ⏳ River (default — tiết kiệm 2-3 ngày; đã propagate vào Phase 3)
4. **[Architecture]** UI stack?
   - Options: Tailwind+shadcn+ECharts (Recommended) | AntD+ECharts | MUI+Recharts
   - **Answer:** ⏳ Tailwind + shadcn/ui + ECharts (default — như plan; đổi sang AntD nếu Dev 4 quen hơn, chi phí đổi = 0 nếu quyết trước tuần 1)

#### Confirmed Decisions
- River cho job queue — propagated Phase 3 (Architecture, files, step 5).
- 3 default còn lại khớp giả định sẵn có của plan → không cần propagate.

#### Action Items
- [x] Q1 vị trí code: user chốt `apps/` (15:19) — đã propagate
- [ ] User confirm/override 3 quyết định ⏳ còn lại trước Phase 1 (Q2 simulator, Q3 River, Q4 UI stack theo skill Dev 4)

#### Impact on Phases
- Phase 3: SKIP LOCKED → River (3 edits, marker inline).
- Phase 1–8: mọi path Related Code Files map theo structure user: Go → `apps/backend/`, React → `apps/web/`, compose+config services → `infra/edge/`, scripts → `deploy/scripts/`, `Makefile` root; prose Go package refs (`internal/...`) giữ nguyên vì relative với module root `apps/backend/`.

### Whole-Plan Consistency Sweep
- Grep toàn plan dir: "SKIP LOCKED" chỉ còn trong Validation Log (lịch sử) — phase files sạch.
- Migration numbering 0001–0008 không trùng; Redis channels `rt:telemetry|alarm|command` nhất quán P2/P3/P4/P5; role worker = ingest+rules+jobs nhất quán P1/P2/P3.
- Sweep sau Q1 (structure user 15:19): grep verify mọi file path đã map `apps/backend/` | `apps/web/` | `infra/edge/` | `deploy/scripts/` | `Makefile` root; ngoại lệ có chủ đích: Go package refs (`cmd/app`, `internal/...` — relative module root), MQTT topic `cmd/ack`, `.github/workflows/` + `README.md` ở root.
- Unresolved contradictions: 0.
