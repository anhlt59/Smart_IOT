# Industrial IoT Platform — Smart KCN

**Nền tảng quản lý vận hành tập trung cho khu công nghiệp thông minh (Industrial IoT Platform)**, hỗ trợ multi-site, multi-tenant. Kiến trúc Hybrid: On-Premise Platform tại từng KCN (tự trị khi mất Internet) + Cloud Platform trên VNPT Cloud.

**Trạng thái dự án:** Thiết kế kiến trúc ✓ · POC on-premise đang triển khai (plan `plans/260723-1450-poc-onprem-iiot-modular-monolith/`).

---

## POC Quickstart

Yêu cầu: Docker Desktop (Compose v2) + Go 1.26+ (chỉ khi dev backend).

```bash
make up      # copy .env.example → .env lần đầu, build + start 7 containers + auto-migrate
make ps      # trạng thái + health từng container
make test    # unit tests backend
make down    # dừng stack (giữ volumes)
```

| Thành phần | Địa chỉ | Ghi chú |
|---|---|---|
| App API (`--role=api`) | http://localhost:8080/healthz | REST + WS theo `apps/backend/api/openapi.yaml` |
| EMQX dashboard | http://localhost:18083 | user `admin`, pass trong `.env` — debug MQTT ([docs EMQX 5.8](https://docs.emqx.com/en/emqx/v5.8/)) |
| Grafana (ops) | http://localhost:3000 | datasource PG provisioned sẵn |
| MediaMTX | rtsp://localhost:8554 · HLS :8888 · WebRTC :8889 | camera relay |
| PostgreSQL/Timescale | 127.0.0.1:5433 (host, dev-only) | trong compose network: `postgres:5432` |

Cấu trúc code: `apps/backend/` (Go modular monolith, 1 binary `--role=api|ingest|worker|all`) · `infra/edge/` (compose + config services) · contract API: `apps/backend/api/openapi.yaml`.
Secrets: chỉ commit `.env.example` / `users-bootstrap.csv.example`; bản thật do `make up` sinh ra, nằm trong `.gitignore`.

---

## Danh mục tài liệu

| Tài liệu | Mô tả | Trạng thái |
|---|---|---|
| [`docs/description.md`](./docs/description.md) | Mô tả chung dự án 2 nền tảng | Đã duyệt |
| [`docs/system-architecture.md`](./docs/system-architecture.md) | Kiến trúc production 7 quyết định (D1-D7) + 15 mục thiết kế chi tiết | Đã duyệt 2026-07-22 |
| [`docs/project-overview-pdr.md`](./docs/project-overview-pdr.md) | PDR: mục tiêu, stakeholders, phạm vi, yêu cầu, ràng buộc | Mới |
| [`docs/codebase-summary.md`](./docs/codebase-summary.md) | Index repo: cấu trúc, từng tài liệu, trạng thái, quan hệ | Mới |
| [`docs/project-roadmap.md`](./docs/project-roadmap.md) | Roadmap Phase A/B/C + timeline thi công + gates G0-G6 | Mới |
| [`docs/POC_architecture.md`](./docs/POC_architecture.md) | POC xử lý nước thải: edge Docker, cloud K8s, chi phí (nặng: base64) | Tham chiếu |
| [`docs/TechStack_Pipeline.docx.md`](./docs/TechStack_Pipeline.docx.md) | Tech stack đích + 5 giai đoạn phần mềm 9 tháng (nặng: base64) | Tham chiếu |
| [`docs/Industrial_Park_Technical_Report.pdf`](./docs/Industrial_Park_Technical_Report.pdf) | Hồ sơ thi công Đồng Văn III: kiến trúc 5 lớp, hardware, network | Tham chiếu |
| [`docs/IoT_Software_Team_Collaboration_Guidelines.pdf`](./docs/IoT_Software_Team_Collaboration_Guidelines.pdf) | Quy chế 2 đội IoT/Phần mềm: ranh giới, gates G0-G6, KPI | Tham chiếu |
| [`docs/industrial-park-technical-report.md`](./docs/industrial-park-technical-report.md) | Bản Markdown của Technical Report PDF (đầy đủ 30 trang, 32 bảng, 7 hình) | Chuyển đổi |
| [`docs/iot-software-team-collaboration-guidelines.md`](./docs/iot-software-team-collaboration-guidelines.md) | Bản Markdown của Quy chế PDF (đầy đủ 22 trang, 17 bảng, 3 hình) | Chuyển đổi |

**Sơ đồ tài liệu:**
```
POC Architecture (reference) 
    ↓
Brainstorm Report (7 quyết định + trade-offs, 12 chủ đề)
    ↓
System Architecture v1.0 (7 quyết định D1-D7 sticky, 15 mục)
    ↓
Diagrams (3 files: overall-hybrid, cloud-platform, on-premise-platform)
```

---

## Kiến trúc Hybrid — Tóm tắt 7 quyết định

| # | Quyết định | Lựa chọn |
|---|---|---|
| D1 | Edge baseline | Cố định ĐV3 (hardware BOM không đổi) |
| D2 | Tech stack | Go · EMQX · Kafka · ClickHouse · PostgreSQL · Redis · Keycloak · Temporal |
| D3 | Scale target | 10–30 KCN; cell-ready 100+; mốc 1000 chỉ nguyên tắc |
| D4 | Connectivity | VNPT MPLS/L3VPN primary + Internet IPsec backup |
| D5 | DR | Warm standby region 2; RPO 5–15ph; RTO 1–2h |
| D6 | Tenancy | Shared cluster + PG RLS + EMQX ACL (không per-tenant deploy) |
| D7 | On-Prem runtime | Docker Compose (KHÔNG K8s/K3s tại site; K8s chỉ cloud) |

---

## Tech Stack

**Compute & Messaging:** Go/Gin, EMQX, Kafka
**Data:** ClickHouse, PostgreSQL, Redis
**Identity & Workflow:** Keycloak, Temporal
**Media:** MediaMTX (video relay)
**CI/CD:** GitLab, Argo CD, Terraform, Ansible
**Observability:** Prometheus, Grafana, Loki, Mimir, Alertmanager
**Security:** Vault PKI, Keycloak 2FA TOTP, ZTNA

---

## Roadmap 3 Phase

| Phase | Thời gian | Mục tiêu | Exit |
|---|---|---|---|
| **A — Landing zone** | 0–3 tháng | VPC/VKS/managed DB; Vault PKI; EMQX cloud; LGTM; DMZ ĐV3 | Telemetry ≤5s; 0 secret plaintext |
| **B — Hardening** | 3–6 tháng | Warm standby region 2; backup; Temporal onboarding; NOC dashboard | Site #2 ≤1 ngày; DR RTO ≤2h |
| **C — Scale-out** | 6–18 tháng | 10+ KCN live; Device Registry; cost tuning | SLO 99.9% đo được |

---

## Diagrams (Sơ đồ kiến trúc)

Lưu tại `docs/diagrams/` — 3 file Mermaid v11 (`flowchart LR`):
- `overall-hybrid-architecture.mmd` — tổng thể 2 nền tảng
- `cloud-platform-architecture.mmd` — chi tiết cloud
- `on-premise-platform-architecture.mmd` — chi tiết on-prem

**Hướng dẫn chỉnh sửa & export:**
```bash
# Preview: GitHub/GitLab render trực tiếp, hoặc https://mermaid.live

# Export PNG/SVG (từ CLI, cần @mermaid-js/mermaid-cli):
mmdc -i input.mmd -o output.png -s 2
```

---

## Cảnh báo

⚠️ **2 file tài liệu chứa base64 nhúng (ảnh) — tránh read trực tiếp:**
- `docs/POC_architecture.md` (~600KB)
- `docs/TechStack_Pipeline.docx.md` (~237K tokens)

**Thay thế:** Dùng grep hoặc strip text (nếu AI assistant cần).

---

## Bắt đầu

1. **Hiểu kiến trúc:** Đọc [`system-architecture.md`](./docs/system-architecture.md) — 7 quyết định + 15 mục (15 phút)
2. **Chi tiết PDR:** Xem [`project-overview-pdr.md`](./docs/project-overview-pdr.md) — yêu cầu chi tiết
3. **Roadmap & timeline:** Xem [`project-roadmap.md`](./docs/project-roadmap.md)
4. **Sơ đồ kiến trúc:** Mở diagrams từ [`docs/diagrams/`](./docs/diagrams/)

---

## Liên hệ

- **Email:** account2@neoscorp.vn
- **Repo:** Docs-only design phase (code base TBD)
