# CLAUDE.md — Industrial IoT Platform

Hướng dẫn cho AI assistant làm việc trong repo docs-only này.

## Bản chất repo

**Giai đoạn:** Thiết kế kiến trúc ✓ · Chưa triển khai code.
**Nội dung:** Tài liệu (markdown, PDF, draw.io) + sơ đồ kiến trúc + kế hoạch dự án.

---

## Bản đồ file quan trọng

### Nguồn sự thật kiến trúc (STICKY — không tự đảo ngược)
- **`docs/system-architecture.md`** v1.0 (2026-07-22) — 7 quyết định D1-D7 + 15 mục + roadmap Phase A/B/C
  - **D1 Edge:** Cố định ĐV3 (hardware BOM không đổi, chỉ can thiệp software)
  - **D2 Stack:** Go/Gin, EMQX, Kafka, ClickHouse, PostgreSQL, Redis, Keycloak, Temporal
  - **D3 Scale:** 10–30 KCN; cell-ready 100+
  - **D4 Connectivity:** VNPT MPLS/L3VPN primary + Internet IPsec backup
  - **D5 DR:** Warm standby region 2; RPO 5–15ph; RTO 1–2h
  - **D6 Tenancy:** Shared cluster + PG RLS + EMQX ACL (không per-tenant deploy)
  - **D7 Runtime:** Docker Compose on-prem (KHÔNG K8s/K3s tại site; K8s chỉ cloud)
  - **Nguyên tắc:** Edge tự trị #1 · Một cửa vào cloud · Managed-first · 1 pipeline dữ liệu · Shared multi-tenant · Mọi thứ là code
  - **QUY TẮC:** Chỉ user hoặc task chính thức mới được đảo ngược quyết định. Audit/suggestion không đủ. Nếu audit phát hiện issue mới → ghi chú trạng thái, đề cập tới user.

### Tài liệu tham chiếu (context dùng được)
- `docs/description.md` — Mô tả 2 nền tảng (94 dòng)
- `docs/POC_architecture.md` — POC nước thải: edge 10 services, cloud K8s (nặng, base64)
- `docs/tech-stack-pipeline.md` — Tech stack + 5 giai đoạn phần mềm 9 tháng (nặng, base64)
- `docs/industrial-park-technical-report.md` — Bản Markdown ĐẦY ĐỦ của Technical Report PDF (794 dòng) → **đọc bản này thay PDF**
- `docs/iot-software-team-collaboration-guidelines.md` — Bản Markdown ĐẦY ĐỦ của Quy chế PDF (489 dòng) → **đọc bản này thay PDF**
- `docs/project-overview-pdr.md` — PDR: mục tiêu, stakeholders, phạm vi, yêu cầu
- `docs/codebase-summary.md` — Index repo: cấu trúc, từng tài liệu, quan hệ
- `docs/project-roadmap.md` — Roadmap A/B/C + timeline ĐV3 + 5 giai đoạn phần mềm + gates

### Sơ đồ kiến trúc
- `docs/diagrams/overall-hybrid-architecture.mmd` — Tổng thể 2 nền tảng
- `docs/diagrams/cloud-platform-architecture.mmd` — Chi tiết cloud
- `docs/diagrams/on-premise-platform-architecture.mmd` — Chi tiết on-prem
- **Định dạng:** Mermaid v11 `flowchart LR` + subgraph (validated mermaid@11.16.0)

### Quy hoạch & báo cáo
- `docs/journals/260722-brainstorm-production-infra-architecture-decisions.md` — Journal quyết định
- `plans/reports/brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md` — Phân tích 12 chủ đề (gaps/alternatives/trade-offs)

---

## QUY TẮC làm việc

### ⚠️ Đọc file an toàn
- **KHÔNG Read trực tiếp:**
  - `docs/POC_architecture.md` (600KB base64)
  - `docs/tech-stack-pipeline.md` (237K tokens base64)
  - `docs/archive/*`
- **Thay thế:** Dùng `grep`, hoặc strip text (nếu cần trích dẫn chi tiết).

### Kiến trúc STICKY
- **system-architecture.md** = Nguồn sự thật + 7 quyết định D1-D7 chốt 2026-07-22
- **Chỉ user mới được xin thay đổi quyết định** (per quy tắc review-audit-self-decision.md)
- Nếu audit/suggestion phát hiện issue: ghi chú status, báo cáo user (không tự đảo ngược)

### Hardware & Runtime
- **Edge hardware:** Cố định theo ĐV3 (BOM: 9× ECU-1051, ADAM-3600, 2× Jetson Orin, FortiGate 80F, 4 server Dell, NVR, UPS) → **KHÔNG thay thế**
- **On-prem software:** Docker Compose (D7 xác nhận 2026-07-22) → **KHÔNG đề xuất K8s/K3s tại site**
- **Cloud:** VKS (Kubernetes) dùng được; managed services từ VNPT

### Tài liệu và Kế hoạch
- **Docs:** Viết tiếng Việt, thuật ngữ kỹ thuật = Anh, sacrifice grammar for concision
- **Vị trí:** `docs/` cho tài liệu; `plans/` cho kế hoạch + reports
- **Lưu ý:** Tuân thủ `.claude/rules/*.md` từ repo này (development-rules, primary-workflow, code-standards, etc.)

### Diagram chỉnh sửa & export
- File nguồn: `.mmd` (Mermaid v11, `flowchart LR` + subgraph)
- Preview: GitHub/GitLab render trực tiếp, hoặc https://mermaid.live
- Export PNG/SVG khi cần: `mmdc -i input.mmd -o output.png -s 2` (@mermaid-js/mermaid-cli)
- Quy ước: `==>` luồng dữ liệu chính · nét đứt đỏ = downlink/điều khiển ngược · nét đứt xám = replication/standby
- Lưu `.mmd` trong `docs/diagrams/`

### Commits & Docs sync
- Conventional commit format (no emoji, no plan refs in code)
- Docs update: nếu code change → update docs sau (docs-manager agent)
- Không commit `.env`, API keys, confidential info

---

## Tổng quan kiến trúc (30 giây)

Edge tự trị (PLC fail-safe + gateway buffer 30 ngày) → Cloud warm standby (VNPT Cloud MPLS primary + Internet IPsec backup) → Shared multi-tenant (PG RLS + EMQX ACL + cell_id) → 1 pipeline dữ liệu (EMQX → Kafka → ingest → ClickHouse/PG/Redis) → Managed-first + Docker Compose on-prem → Roadmap A (landing zone 0–3 tháng) → B (hardening 3–6) → C (scale-out 6–18).

---

## Người liên hệ

Email: account2@neoscorp.vn
