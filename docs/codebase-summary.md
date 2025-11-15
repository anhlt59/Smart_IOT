# Codebase Summary — Industrial IoT Platform

**Loại repo:** Docs-only (design phase) · **Trạng thái:** Thiết kế xong, chưa code

---

## Cấu trúc thư mục

```
Smart_IOT/
├── README.md                                  # Giới thiệu dự án, danh mục tài liệu, roadmap
├── CLAUDE.md                                  # Hướng dẫn AI assistant
├── docs/
│   ├── description.md                         # Mô tả 2 nền tảng (94 dòng)
│   ├── system-architecture.md                 # Kiến trúc v1.0: 7 quyết định D1-D7 (251 dòng)
│   ├── project-overview-pdr.md                # PDR: mục tiêu, stakeholders, yêu cầu
│   ├── codebase-summary.md                    # File này (index repo)
│   ├── project-roadmap.md                     # Roadmap A/B/C + timeline ĐV3 + gates
│   ├── POC_architecture.md                    # POC nước thải (tham chiếu, nặng)
│   ├── TechStack_Pipeline.docx.md             # Tech stack + 5 giai đoạn 9 tháng (tham chiếu, nặng)
│   ├── Industrial_Park_Technical_Report.pdf   # Hồ sơ thi công ĐV3 (tham chiếu, PDF)
│   ├── IoT_Software_Team_Collaboration_Guidelines.pdf # Quy chế 2 đội (tham chiếu, PDF)
│   ├── industrial-park-technical-report.md    # Bản Markdown của Technical Report PDF (794 dòng)
│   ├── iot-software-team-collaboration-guidelines.md # Bản Markdown của Quy chế PDF (489 dòng)
│   ├── images/                                # 10 figure extract từ 2 PDF (PNG)
│   └── diagrams/
│       ├── overall-hybrid-architecture.drawio     # Tổng thể 2 nền tảng (XML)
│       ├── overall-hybrid-architecture.png        # Export PNG 2x
│       ├── cloud-platform-architecture.drawio     # Chi tiết cloud (XML)
│       ├── cloud-platform-architecture.png        # Export PNG 2x
│       ├── on-premise-platform-architecture.drawio # Chi tiết on-prem (XML)
│       └── on-premise-platform-architecture.png   # Export PNG 2x
├── docs/journals/
│   └── 260722-brainstorm-production-infra-architecture-decisions.md # Journal quyết định
└── plans/
    └── reports/
        └── brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md
            # Phân tích 12 chủ đề (gaps, alternatives, trade-offs)
```

---

## Danh sách tài liệu

| File | Mục đích | Độ dài | Trạng thái | Lưu ý |
|---|---|---|---|---|
| `README.md` | Giới thiệu dự án, danh mục, tech stack, roadmap, hướng dẫn diagram | <200 dòng | Mới | Link relative tới docs/ |
| `CLAUDE.md` | Hướng dẫn AI: bản đồ file, 7 quyết định D1-D7, QUY TẮC (không read base64, architecture sticky) | <120 dòng | Mới | Sticky architecture, edge cố định, Docker Compose on-prem |
| `docs/description.md` | Tổng quan 2 nền tảng hybrid (on-prem tự trị + cloud multi-tenant) | 94 dòng | Nguồn | Tham chiếu architecture |
| `docs/system-architecture.md` | **Kiến trúc production:** 7 quyết định D1-D7 (edge cố định, tech stack, scale, connectivity, DR, tenancy, Docker Compose) + 15 mục chi tiết (network, data, security, monitoring, roadmap A/B/C) | 251 dòng | Đã duyệt 2026-07-22 | **STICKY:** Chỉ user mới đảo ngược quyết định |
| `docs/project-overview-pdr.md` | **PDR:** mục tiêu nền tảng, stakeholders, phạm vi ĐV3, 4 phân hệ, yêu cầu chức năng (cloud + on-prem), phi chức năng (SLO 99.9%, latency ≤5s), ràng buộc (VNPT Cloud, hardware cố định, Docker Compose) | <250 dòng | Mới | Spec chính thức |
| `docs/codebase-summary.md` | **Index repo:** cấu trúc thư mục, danh sách từng tài liệu, trạng thái, quan hệ giữa tài liệu | <150 dòng | Mới | File này |
| `docs/project-roadmap.md` | **Roadmap:** hợp nhất Phase A/B/C từ system-architecture §14 (exit criteria), timeline thi công ĐV3 (~4 tháng), 5 giai đoạn phần mềm (tháng 1-9), gates G0-G6 từ quy chế 2 đội, trạng thái hiện tại (design done, chưa code) | <150 dòng | Mới | Chi tiết timeline |
| `docs/POC_architecture.md` | **Tham chiếu:** POC xử lý nước thải (edge Docker Compose 10 services, cloud K8s, SLA, cost model) | ~600KB | Nguồn | ⚠️ Base64 nhúng → không read trực tiếp |
| `docs/TechStack_Pipeline.docx.md` | **Tham chiếu:** Tech stack đích vs POC, 5 giai đoạn triển khai phần mềm 9 tháng, rủi ro, learnings | ~237K tokens | Nguồn | ⚠️ Base64 nhúng → không read trực tiếp |
| `docs/Industrial_Park_Technical_Report.pdf` | **Tham chiếu:** Hồ sơ thi công Đồng Văn III: kiến trúc 5 lớp (OT/IT/DMZ), hardware (ECU, ADAM, server, FortiGate), network (VLAN), power/cooling | 30 trang | Nguồn | PDF tham chiếu D1 hardware |
| `docs/IoT_Software_Team_Collaboration_Guidelines.pdf` | **Tham chiếu:** Quy chế phối hợp 2 đội (ranh giới MQTT broker, tag list, P2P test, gates G0-G6, DEV/STG/PROD, KPI telemetry ≤5s) | 22 trang | Nguồn | PDF quy trình gates |
| `docs/industrial-park-technical-report.md` | Bản Markdown đầy đủ của Technical Report PDF: 30 page marker, 32 bảng, 7 hình + 1 mermaid | 794 dòng | Chuyển đổi 2026-07-23 | Đọc bản này thay PDF |
| `docs/iot-software-team-collaboration-guidelines.md` | Bản Markdown đầy đủ của Quy chế PDF: 22 page marker, 17 bảng, 3 hình + 2 mermaid | 489 dòng | Chuyển đổi 2026-07-23 | Đọc bản này thay PDF |
| `docs/images/` | 10 figure PNG extract từ 2 PDF (7 technical-report + 3 collab-guidelines) | 10 file | Chuyển đổi 2026-07-23 | Tham chiếu bởi 2 bản md |
| `docs/diagrams/overall-hybrid-architecture.*` | Sơ đồ tổng thể: cloud + on-prem + MPLS/backup | 2 file (drawio + PNG 2x) | Mới | Mở draw.io tại app.diagrams.net |
| `docs/diagrams/cloud-platform-architecture.*` | Sơ đồ chi tiết cloud: VPC, VKS pools, managed services, Kafka, ClickHouse, Keycloak, LGTM | 2 file (drawio + PNG 2x) | Mới | Export PNG: `drawio -x -f png -s 2 -o out.png in.drawio` |
| `docs/diagrams/on-premise-platform-architecture.*` | Sơ đồ chi tiết on-prem: VLAN (OT/IT/DMZ), Docker Compose, IOC, EMQX bridge, NVR, AI | 2 file (drawio + PNG 2x) | Mới | Hardware ĐV3 cố định (D1) |
| `docs/journals/260722-brainstorm-production-infra-architecture-decisions.md` | Journal: quyết định 7 quyết định (log thảo luận, lý do chọn) | Mở rộng | Nguồn | Audit trail kiến trúc |
| `plans/reports/brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md` | Báo cáo phân tích: 12 chủ đề (cloud provider, serverless, managed vs self-host, cell vs shared, K8s on-prem, DR warm vs active-active, etc.) + trade-offs, gaps, alternatives | Mở rộng | Đã duyệt | Trace quyết định → D1-D7 |

---

## Quan hệ giữa tài liệu (Sơ đồ thứ tự đọc)

```
1. POC Architecture (reference)
   ↓ Learning + findings
2. Brainstorm Report (12 topics, trade-offs, gaps)
   ↓ Consolidated 7 decisions
3. System Architecture v1.0 (D1-D7 + 15 sections, STICKY)
   ↓ Detailed spec
4. Project Overview PDR (functional + non-functional requirements)
   ↓ Planning
5. Project Roadmap (Phase A/B/C + timeline + gates)
   ↓ Architecture visuals
6. Diagrams (draw.io + PNG)
```

**Đọc bắt đầu từ:**
- **Quick:** `README.md` (5 phút) → `system-architecture.md` §1-2 (10 phút)
- **Deep:** `system-architecture.md` (15 phút) → `project-overview-pdr.md` (10 phút) → `project-roadmap.md` (10 phút)
- **Reference:** Brainstorm report (trade-offs), POC (giải pháp tương tự), PDF (hardware/quy trình)

---

## Trạng thái & Phiên bản

| Component | Version | Ngày | Trạng thái |
|---|---|---|---|
| System Architecture | 1.0 | 2026-07-22 | Đã duyệt (7 quyết định D1-D7 sticky) |
| PDR | 1.0 | 2026-07-22 | Mới tạo |
| Roadmap | 1.0 | 2026-07-22 | Mới tạo |
| Codebase Summary | 1.0 | 2026-07-22 | Mới tạo |
| Diagrams | 1.0 | 2026-07-22 | Mới tạo |
| POC Architecture | Ref | 2026-07 | Tham chiếu (learning) |
| TechStack Pipeline | Ref | 2026-07 | Tham chiếu (5 giai đoạn) |

---

## Ghi chú

- **Repo hiện tại:** Docs-only, chưa có application code
- **Next:** Phase A (0–3 tháng) landing zone → code implementation
- **Docs update:** Nếu có code change → sync docs tương ứng (docs-manager agent)
- **Diagram edit:** Mở file `.drawio` tại https://app.diagrams.net/ → export PNG 2x
