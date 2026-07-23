# Brainstorm Report — Kiến trúc POC On-Premise Only (Modular Monolith vs Microservices + Async Architecture)

**Ngày:** 2026-07-23 · **Loại:** brainstorm · **Trạng thái:** ✅ User xác nhận toàn bộ quyết định 2026-07-23 14:50 (mục 2)
**Nguồn:** `docs/system-architecture.md` v1.0, `docs/project-overview-pdr.md`, `docs/project-roadmap.md`, `docs/POC_architecture.md` (grep), `docs/description.md`

---

## 1. Problem Statement

POC đổi hướng: **bỏ hoàn toàn Cloud Platform, chỉ triển khai On-Premise**, tập trung thu thập dữ liệu + giám sát + điều khiển thiết bị Industrial IoT. Cần:
- Đánh giá lại microservices vs modular monolith cho quy mô POC.
- Quyết định kiến trúc xử lý bất đồng bộ (EDA? queue+worker? broker nào?).
- Chốt kiến trúc tối ưu: tốc độ dev, mở rộng lên production, dễ bảo trì, hiệu năng, realtime.

## 2. Quyết định đã chốt (user xác nhận 2026-07-23)

| # | Quyết định |
|---|---|
| A1 | **POC-only** — bỏ cloud chỉ trong phạm vi POC; production hybrid (system-architecture v1.0) giữ nguyên → POC chừa seam nối cloud. `docs/system-architecture.md` KHÔNG sửa |
| A2 | **1 site** (ĐV3-class), hàng trăm tags, ≤2.000 msg/s đỉnh, ≤50 user local, single tenant |
| A3 | **Stack Go** + EMQX (hướng D2); POC cắt Kafka/Keycloak/Temporal/ClickHouse |
| A4 | **5 dev, 1 tháng** — timeline gắt → cắt scope mạnh (mục 8b), module ownership để 5 dev song song |
| A5 | **Camera TRONG scope POC** (live view + AI event); **Dashboard = web UI (React)**, Grafana chỉ cho ops |

D1 (edge hardware), D7 (Docker Compose on-prem) không đổi. Phần Cloud/D4/D5/D6 tạm không áp dụng cho POC — vẫn là thiết kế production.

## 3. Ràng buộc giữ nguyên từ docs

- **D7:** Docker Compose on-prem, không K8s/K3s tại site.
- **D1:** hardware ĐV3 cố định (2× R660xs app, R760xs data, DL380 GPU, ECU-1051, ADAM-3600...).
- **Interface Agreement:** ranh giới nghiệm thu tại MQTT broker; topic `v1/{tenant}/{park}/{subsys}/{node}/...`; bản tin bắt buộc (NTP ts, gateway ID, sequence, backfill flag, quality flag); QoS1 + app-level ack cho command.
- **Production on-prem đã dùng PG + TimescaleDB + Redis trên R760xs** (`system-architecture.md:83`) — ClickHouse chỉ ở cloud → POC on-prem dùng TimescaleDB là **align production**, không phải giải pháp tạm.
- KPI PDR: telemetry ≤5s, event ≤2s, command ≤5s, buffer 30 ngày, NĐ 40/2015 fail-safe tại PLC.

## 4. Phương án kiến trúc ứng dụng

### PA-1 — Modular Monolith Go, "single binary – multiple roles" ✅ KHUYẾN NGHỊ

1 codebase, 1 Docker image; binary chạy được nhiều mode (`app api`, `app ingest`, `app worker` — hoặc all-in-one `app serve`). Module boundaries bằng Go packages + interfaces; giao tiếp in-process (function call + channels).

```
Compose (~6 containers, POC cũ là 11):
EMQX · PostgreSQL+TimescaleDB · Redis · app-api · app-ingest+worker · Grafana(ops)
```

| Ưu | Nhược |
|---|---|
| Tốc độ dev cao nhất: 1 repo, 1 build, 1 debug session, refactor xuyên module không cần version contract | Cần kỷ luật giữ module boundary (mitigate: layout chuẩn + import lint + review) |
| Hiệu năng tốt nhất: không network hop nội bộ; Go goroutines/channels hợp pipeline ingest | Scale chỉ vertical — nhưng 2k msg/s 1 site: 1 server thừa sức (đã đo đạc phổ biến: Go ingest + Timescale batch insert >50k rows/s/node) |
| Chạy tách role (api vs ingest) → crash isolation mà vẫn 1 codebase | Nhầm lẫn "monolith = code bừa" nếu team không thống nhất kiến trúc module |
| Seam production rõ: module nào quá tải → tách thành service, giữ nguyên interface | |

### PA-2 — Mini-services (3 services: ingest / api / worker + bus riêng)

| Ưu | Nhược |
|---|---|
| Gần shape production cloud; isolation mạnh | Với 2–3 dev: thuế phân tán (contract versioning, distributed tracing, deploy matrix) ăn thẳng vào timeline |
| Scale độc lập từng service | Vô nghĩa ở 1 site — bottleneck thực là DB, không phải app |
| | Cần thêm broker nội bộ (NATS/Kafka) ngay từ đầu → thêm moving part |

### PA-3 — Giữ nguyên D2 full stack thu nhỏ (Kafka + ClickHouse + Keycloak + Temporal on-prem)

| Ưu | Nhược |
|---|---|
| Không phải học lại stack khi lên production | Ops nặng nhất: Kafka cluster + ClickHouse + Keeper + Keycloak trên 1 site = chậm POC 3–6 tuần chỉ để setup/vận hành |
| | Sai cả với production design: on-prem production KHÔNG chạy Kafka/ClickHouse (chúng ở cloud) — POC on-prem-only mô phỏng cloud stack là sai chỗ |

**Verdict:** PA-1. PA-3 sai đề bài (mô phỏng cloud stack tại site trong khi production site không chạy stack đó). PA-2 là thuế trả trước cho scale chưa tồn tại — vi phạm YAGNI; đường nâng cấp từ PA-1 → PA-2 rẻ nếu module boundary giữ đúng.

## 5. Đồng bộ vs Bất đồng bộ

| Thành phần | Mode | Lý do |
|---|---|---|
| REST API query (history, device list, alarm list) | **Sync** | Request/response tự nhiên; p95 <200ms |
| Auth/login | **Sync** | |
| Telemetry ingest (MQTT → DB) | **Async** (stream) | Batch insert 1–5s window; consumer tách khỏi API |
| Rule evaluation / alarm detect | **Async** (in-process, hot path) | Đánh giá ngay trên stream ingest, KPI event ≤2s → không được qua queue chậm |
| Notification (Telegram/email) | **Async** (durable job) | Retry được, không block alarm path |
| Command downlink + ack tracking | **Async có correlation** | API nhận request sync → publish MQTT QoS1 + idempotency key → chờ `cmd/ack` ≤5s → update state; client nhận kết quả qua WebSocket/poll |
| Report generation (PDF tháng) | **Async** (durable job) | Chạy nền, kết quả lưu Object/file storage |
| Dashboard realtime push | **Async** (WebSocket/SSE fan-out) | Subscribe last-value từ ingest stream + Redis cache initial load |
| Backfill (gateway truyền bù) | **Async** | Cờ backfill sẵn trong Interface Agreement; không tính realtime KPI |

**EDA?** Có — nhưng đúng liều: **MQTT/EMQX đã là event backbone** của hệ thống (bắt buộc theo Interface Agreement). POC dùng "event notification" pattern: EMQX events → ingest module → in-process dispatch (channels) tới rule/alarm/websocket modules. **KHÔNG** event sourcing, không saga, không broker-per-service — đó là formalism cho hệ phân tán nhiều team, POC không có bài toán đó.

**Queue + Worker?** Có — cho durable background jobs (notification, report, retention/housekeeping): **PostgreSQL-backed job queue** (River — Go native, hoặc `SELECT ... FOR UPDATE SKIP LOCKED` tự viết ~200 LOC). Transactional với business data (job enqueue cùng transaction với alarm insert → không mất notification), zero hạ tầng thêm, throughput vài trăm jobs/s — POC cần vài chục.

## 6. Message broker cho Industrial IoT On-Prem — so sánh

| Broker | Vai trò phù hợp | Verdict POC |
|---|---|---|
| **EMQX (MQTT)** | Device ↔ platform. Bắt buộc (Interface Agreement, ranh giới nghiệm thu). Shared subscription `$share/g/...` load-balance consumers; persistent session giữ QoS1 khi consumer down; bridge sẵn để nối cloud sau | ✅ **Broker DUY NHẤT của POC** |
| **PostgreSQL queue (River/SKIP LOCKED)** | Durable background jobs | ✅ Dùng — không thêm hạ tầng |
| **NATS JetStream** | Nếu POC multi-site hoặc cần replay/stream nội bộ: 1 binary ~15MB, ops gần zero, Go-native | ⏸ Defer — plan B nếu A2 sai (multi-site) |
| **Redis Streams** | Queue nhẹ khi đã có Redis | ❌ Durability yếu hơn PG, thêm code quản consumer group/PEL mà không thêm giá trị so với PG queue |
| **RabbitMQ** | Task queue truyền thống | ❌ Thêm công nghệ ngoài D2, không có ưu thế nào ở đây |
| **Kafka** | Fleet-scale cloud (đúng vị trí trong production hybrid) | ❌ Overkill tuyệt đối cho 1 site: cluster ops + partition/consumer-group complexity để xử lý 2k msg/s mà 1 process Go làm được |

**Mất message khi ingest down?** Chuỗi phòng thủ sẵn có: gateway ECU-1051 buffer 30 ngày + backfill flag → EMQX persistent session QoS1 → batch insert transactional. Kafka replay window 3–7 ngày của production giải bài toán *fleet consumer lag*, không phải bài toán của 1 site.

## 7. Storage: TimescaleDB vs ClickHouse (POC)

| Tiêu chí | PG + TimescaleDB | ClickHouse |
|---|---|---|
| Align production **on-prem** design | ✅ chính là thiết kế site (`system-architecture.md:83`) | ❌ CH chỉ ở cloud |
| Số DB engine phải vận hành | 1 (PG làm cả metadata + timeseries) | 2 (PG + CH + backup path riêng) |
| Join metadata ↔ telemetry, transaction alarm lifecycle | Native SQL, 1 connection | Cross-DB, eventual |
| Retention 30d raw / 1y aggregate | retention policy + continuous aggregates | TTL + AggregatingMergeTree (mạnh hơn ở fleet scale) |
| Throughput 1 site (≤2k msg/s) | Thừa (batch insert) | Thừa |
| **Verdict** | ✅ **POC + production on-prem** | Production cloud (không đổi D2) |

Seam: module `telemetry/store` là interface `TelemetryStore` — khi nối cloud, thêm sink Kafka producer hoặc EMQX bridge (bridge là cách production đã thiết kế: edge EMQX → cloud EMQX, không đụng app code).

## 8. Kiến trúc đề xuất (PA-1 chi tiết)

```
  PLC/RTU/Sensors ──Modbus──► ECU-1051 / ADAM-3600 (buffer 30d, scale 1 lần, ký số)
                                   │ MQTT QoS1, topic v1/{tenant}/{park}/{subsys}/{node}/...
                                   ▼
                            ┌───── EMQX ─────┐  ◄── ranh giới Interface Agreement (giữ nguyên)
                            │ ACL per cert CN │  ◄── seam cloud: bật bridge khi cần, app không đổi
                            └──┬──────────▲───┘
              $share ingest   │          │ publish cmd / subscribe ack
                              ▼          │
  ┌────────────────────── app (1 binary Go, 2 container) ─────────────────────┐
  │  role: ingest+worker                     role: api                        │
  │  ┌─────────┐  channels  ┌──────────┐    ┌─────────┐   ┌───────────────┐   │
  │  │ ingest  ├──────────► │ rules/   │    │ REST API│   │ WebSocket hub │   │
  │  │ decode/ │            │ alarm    │    │ (Gin)   │   │ realtime push │   │
  │  │ validate│            └────┬─────┘    └────┬────┘   └──────▲────────┘   │
  │  └────┬────┘                 │               │               │            │
  │       │ batch 1-5s           │ enqueue job   │               │            │
  │  ┌────▼─────────────────┐ ┌──▼───────────┐ ┌─▼───────────────┴──┐         │
  │  │ TelemetryStore       │ │ JobQueue(PG) │ │ auth(JWT+RBAC 3role)│        │
  │  │ (interface)          │ │ notify/report│ │ command (whitelist  │        │
  │  └────┬─────────────────┘ └──┬───────────┘ │  +idempotency+audit)│        │
  └───────┼────────────────────── ┼─────────── └─────────────────────┘────────┘
          ▼                       ▼
   PostgreSQL + TimescaleDB (metadata, alarm, audit, jobs, hypertables)
   Redis (last-value cache, ws session)          Grafana (ops dashboards)
```

**Go module layout (internal boundaries = seam tách service sau):**
```
cmd/app/                    # main, role flags: api|ingest|worker|all
internal/ingest/            # MQTT consume, decode, validate (IA spec), batch
internal/telemetry/         # TelemetryStore interface + timescale impl
internal/rules/             # threshold eval, alarm lifecycle
internal/control/           # command whitelist, dispatch, ack, audit
internal/device/            # device registry, heartbeat
internal/auth/              # JWT, RBAC; interface → swap OIDC/Keycloak sau
internal/jobs/              # PG queue: notify (Telegram/email), report PDF
internal/api/               # Gin handlers, WebSocket hub
internal/camera/            # camera registry, stream URL (MediaMTX), AI event mapping
internal/events/            # in-process event bus (channels); interface → swap Kafka sau
web/                        # React dashboard (Vite), WebSocket client, video player
```

**Camera lane (A5 — trong scope POC):**
- **Recording:** NVR sẵn có đảm nhiệm — POC KHÔNG build VMS.
- **Live view web UI:** MediaMTX (align production design, đã có trong site blueprint) relay RTSP → WebRTC/HLS; API trả stream URL per camera; giới hạn concurrent stream.
- **AI event:** Jetson AI box publish event MQTT (`v1/{tenant}/{park}/security/{node}/event`) → đi qua pipeline ingest/alarm như event thường — không nhánh riêng.
- Compose thêm 1 container MediaMTX → tổng ~7 containers.

## 8b. Scope cut + phân công 5 dev / 4 tuần (A4)

**Cắt khỏi POC 1 tháng (production vẫn giữ):** 2FA TOTP · PDF report (stub API) · Keycloak/OIDC (JWT local) · multi-tenant isolation test · retention automation nâng cao (chỉ set TTL policy) · HA keepalived 2 server (chạy 1 server) · NVR/VMS features.

**Giữ bắt buộc (an toàn công nghiệp, không cắt):** command whitelist + idempotency + app ack + audit trail · quality/backfill flag theo Interface Agreement · alarm durable notification.

| Dev | Own modules | Tuần 1 | Tuần 2 | Tuần 3 | Tuần 4 |
|---|---|---|---|---|---|
| 1 | `ingest`, `telemetry`, `events` | Skeleton + compose + EMQX→Timescale E2E | Batch/validate IA spec | Backfill flag, perf 2k msg/s | Hardening |
| 2 | `rules`, `jobs`, `device` | Schema PG + device registry | Rule engine + alarm lifecycle | Notification (Telegram) | Retention TTL, tuning |
| 3 | `api`, `auth`, `control` | Gin skeleton + JWT/RBAC | REST API telemetry/alarm | Command downlink + ack + audit | API polish, docs |
| 4 | `web/` (React) | UI skeleton + auth flow | Dashboard chart/table + WS realtime | Alarm UI + control UI | Camera view + demo polish |
| 5 | `camera`, compose/ops, Grafana | Compose + MediaMTX + EMQX config | Camera registry + stream URL API | AI event ingest E2E | Demo script, ops runbook, load test |

Tuần 1 exit: telemetry simulator → dashboard thô E2E. Tuần 4 exit: demo full flow (sensor→alarm→notify, live camera, command→ack).

**Seams lên production (trả lời "dễ mở rộng"):**
1. **Cloud connect = bật EMQX bridge** (thiết kế production sẵn có) — zero code change ở data plane.
2. `internal/events` + `TelemetryStore` là interfaces → thay in-process bằng Kafka producer khi lên cloud.
3. Topic/tenant giữ đủ `{tenant}/{park}` dù single-tenant → identifiers production-ready, isolation test thêm sau.
4. Auth interface → Keycloak OIDC ở production, POC dùng JWT local.
5. Module boundary = ranh giới tách microservice khi (và chỉ khi) scale/team đòi hỏi.

## 9. Rủi ro & Mitigation

| Rủi ro | Mitigation |
|---|---|
| Module boundary erosion → "big ball of mud" | Layout chuẩn ngay commit 1; import rule (api không import timescale impl trực tiếp...); review |
| Ingest crash kéo API (nếu chạy all-in-one) | Chạy 2 container 2 role từ 1 image; compose restart policy; EMQX persistent session giữ QoS1 |
| PG vừa OLTP vừa timeseries vừa queue → tranh chấp I/O | Batch insert; hypertable riêng tablespace nếu cần; đo từ tuần đầu (pg_stat); ngưỡng thoát: nếu 1 site vượt Timescale → xem lại (khó xảy ra ở 2k msg/s) |
| Migrate Timescale→ClickHouse khi lên cloud | Không migrate — cloud nhận data qua bridge từ đầu nguồn (gateway backfill 30d); POC data là POC data |
| Team quen microservices, ngại monolith | Đây là modular monolith có kỷ luật + đường tách rõ; PA-2 vẫn mở nếu team lớn lên |
| 2FA TOTP cho control (PDR yêu cầu) không kịp POC | Whitelist + audit + app ack là bắt buộc ngay; TOTP đã cắt khỏi POC (mục 8b), bắt buộc production |
| **Timeline 1 tháng / 5 dev** — trễ tích hợp cuối | Tuần 1 phải có E2E thô (simulator→dashboard) làm khung tích hợp; 5 dev own module riêng (bảng 8b), tích hợp liên tục không chờ cuối; contract nội bộ = Go interfaces chốt tuần 1 |
| 5 dev cùng 1 repo → conflict | Module ownership 1-dev-1-module; API contract (OpenAPI) + event types chốt sớm; trunk-based, PR nhỏ |
| Camera WebRTC/HLS latency + browser compat | MediaMTX WebRTC primary, HLS fallback; giới hạn concurrent stream; demo trên mạng LAN |

## 10. Success Metrics (POC)

- Telemetry E2E (sensor→dashboard) ≤5s; event/alarm ≤2s; command RTT ≤5s (đúng PDR).
- Ingest sustained 2.000 msg/s trên 1 server data (R760xs class) không backlog.
- 50 user local đồng thời xem dashboard realtime.
- `docker compose up` từ zero → hệ thống chạy ≤1 giờ; dev mới onboard ≤1 tuần.
- Alarm → Telegram notification có retry, không mất khi restart (job queue durable).
- Audit trail đầy đủ cho mọi command downlink.

## 11. Next Steps

1. ✅ User đã xác nhận A1–A5 (2026-07-23).
2. `/ck:plan` với báo cáo này làm input: phase theo bảng 8b (compose+skeleton → ingest → rules/alarm → API/WS/control → camera → hardening/demo).
3. Đo message rate ĐV3 thực tế sớm để thay ước tính A2 bằng số liệu (open item #3 của system-architecture).
4. Sau POC thành công: quay lại roadmap production (Phase A landing zone) — báo cáo này không thay đổi system-architecture v1.0.

## Unresolved Questions

1. Danh sách camera + codec thực tế cho demo (số lượng stream đồng thời web UI cần chịu)?
2. Simulator bản tin: dùng data mẫu ĐV3 thật hay synthetic? (ảnh hưởng độ thuyết phục demo)
3. Server demo POC: 1 máy đơn (spec Xeon E-2336/32GB trong POC doc cũ) hay mượn hardware ĐV3?
