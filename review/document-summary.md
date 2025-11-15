# Document Summary — Architecture Review

**Ngày review:** 2026-07-22 · **Phạm vi:** toàn bộ `docs/` + tài liệu liên quan (`README.md`, journal, brainstorm report)
**Phương pháp đọc:** file nhẹ đọc trực tiếp; PDF strip text bằng pypdf; file base64 nặng đọc qua grep vùng text (đúng quy tắc CLAUDE.md).

---

## Mục lục

1. [Danh sách tài liệu đã đọc](#1-danh-sách-tài-liệu-đã-đọc)
2. [Mục đích từng tài liệu](#2-mục-đích-từng-tài-liệu)
3. [Trùng lặp / chồng chéo](#3-trùng-lặp--chồng-chéo)

---

## 1. Danh sách tài liệu đã đọc

| # | Tài liệu | Loại | Cách đọc | Trạng thái ghi trong doc |
|---|---|---|---|---|
| 1 | `docs/system-architecture.md` | Nguồn sự thật kiến trúc (v1.0, sticky D1–D7) | Đọc đầy đủ (251 dòng) | Đã duyệt 2026-07-22 |
| 2 | `docs/description.md` | Mô tả tổng quan 2 nền tảng | Đọc đầy đủ (94 dòng) | Đã duyệt |
| 3 | `docs/project-overview-pdr.md` | PDR — spec chính thức | Đọc đầy đủ | Đã duyệt (v1.0) |
| 4 | `docs/project-roadmap.md` | Roadmap Phase A/B/C + gates | Đọc đầy đủ | Mới (v1.0) |
| 5 | `docs/codebase-summary.md` | Index repo | Đọc đầy đủ | Mới (v1.0) |
| 6 | `docs/POC_architecture.md` | Tham chiếu POC nước thải (~600KB base64) | Grep cấu trúc heading | Tham chiếu |
| 7 | `docs/TechStack_Pipeline.docx.md` | Tham chiếu tech stack + 5 giai đoạn 9 tháng (~237K tokens) | Grep + đọc vùng text (dòng 54–260) | Tham chiếu |
| 8 | `docs/Industrial_Park_Technical_Report.pdf` | Hồ sơ thi công ĐV3 (30 trang, Rev 1.1) | Strip text đầy đủ 30 trang | Tham chiếu (nguồn D1 hardware) |
| 9 | `docs/IoT_Software_Team_Collaboration_Guidelines.pdf` | Quy chế phối hợp 2 đội (22 trang, v1.1) | Strip text đầy đủ 22 trang | Tham chiếu (nguồn gates, KPI) |
| 10 | `docs/diagrams/overall-hybrid-architecture.drawio` | Sơ đồ tổng thể | Trích toàn bộ text label từ XML | Mới |
| 11 | `docs/diagrams/cloud-platform-architecture.drawio` | Sơ đồ cloud chi tiết | Trích toàn bộ text label từ XML | Mới |
| 12 | `docs/diagrams/on-premise-platform-architecture.drawio` | Sơ đồ on-prem chi tiết | Trích toàn bộ text label từ XML | Mới |
| 13 | `docs/journals/260722-brainstorm-production-infra-architecture-decisions.md` | Journal quyết định | Đọc đầy đủ | Nguồn (audit trail) |
| 14 | `plans/reports/brainstorm-260722-1457-...-report.md` | Phân tích 12 chủ đề, trade-offs | Đọc đầy đủ (397 dòng) | Đã duyệt |
| 15 | `README.md` (root) | Giới thiệu dự án | Đọc đầy đủ | Mới |

**Ghi chú:** file PNG diagrams không đọc (đã có nội dung đầy đủ từ `.drawio` XML).

---

## 2. Mục đích từng tài liệu

### Nhóm quyết định (authoritative)

- **`system-architecture.md` v1.0** — Nguồn sự thật duy nhất: 7 quyết định D1–D7 (sticky) + 15 mục chi tiết (edge, connectivity, network, cloud, data plane, IoT comm, observability, security, backup/DR, CI/CD, multi-tenancy, roadmap, open items). Chất lượng cao, cô đọng, có đánh dấu `[assumption]` cho số liệu chưa đo.
- **`project-overview-pdr.md`** — PDR: mục tiêu, stakeholders, phạm vi ĐV3, FR/NFR, ràng buộc, success criteria. Là spec chính thức cho đội dev. ⚠️ Chứa nhiều lỗi số liệu (xem `consistency-review.md`).
- **`project-roadmap.md`** — Roadmap 3 phase + timeline chi tiết theo tháng + gates + timeline thi công ĐV3. ⚠️ Định nghĩa lại gates G0–G6 khác Quy chế 2 đội; bảng "5 giai đoạn phần mềm" không khớp nguồn TechStack_Pipeline.

### Nhóm điều hướng

- **`README.md`** — Landing page: danh mục tài liệu, tóm tắt D1–D7, tech stack, roadmap, hướng dẫn diagram.
- **`codebase-summary.md`** — Index repo: cấu trúc, trạng thái, quan hệ tài liệu, thứ tự đọc. Chính xác, hữu ích cho onboarding.
- **`description.md`** — Elevator pitch 2 nền tảng, danh sách managed services VNPT, sơ đồ ASCII đơn giản. Mức generic, tiền thân của system-architecture.

### Nhóm tham chiếu (không authoritative — learning input)

- **`POC_architecture.md`** — POC xử lý nước thải: stack Docker Compose 10 services (Mosquitto/TimescaleDB/Watchtower), cloud K8s manifests, retention/alerting/SLO tables, DRP, cost model. Nhiều điểm đã bị brainstorm report bác (Watchtower, per-tenant deploy, PG Deployment đơn) — vai trò hiện tại: nguồn bảng retention/alerting thresholds được kế thừa.
- **`TechStack_Pipeline.docx.md`** — Tech stack đề xuất (bảng layer) + 5 giai đoạn triển khai 9 tháng + rủi ro từng giai đoạn. Chứa nội dung đã bị thay thế một phần bởi D2 (TDengine→ClickHouse) và nội dung **chưa được xử lý chính thức** (Mobile App, GIS 3D/Digital Twin, voice control, dynamic QR — xem `gap-analysis.md`).
- **`Industrial_Park_Technical_Report.pdf`** — Hồ sơ thi công ĐV3: kiến trúc 5 lớp, bảng chỉ số thu thập theo phân hệ, network (quang/4G/VLAN), BOM chi tiết (Phụ lục A), tiến độ ~4 tháng, giới hạn nền tảng (10 user đồng thời, 5.000 I/O, 300 camera, 40 camera AI). Nguồn gốc của D1. ⚠️ Nội bộ PDF không nhất quán về số lượng gateway (8 vs 9) và 4G kit (4 vs 5).
- **`IoT_Software_Team_Collaboration_Guidelines.pdf`** — Quy chế 2 đội: contract-first, ranh giới nghiệm thu tại MQTT broker, Interface Agreement, gates **G0–G6 nguyên bản** (G0 khảo sát → G6 vận hành), luồng 12 bước/điểm đo, DoD 8 tiêu chí, RACI, KPI (P2P ≥95%, telemetry ≤5s, event ≤2s, gateway ≥99.5%/tháng), SLA sự cố P1–P4, quy trình CR + freeze 48h.

### Nhóm trace quyết định

- **Journal 260722** — Log quyết định: "6 quyết định chốt", brutal truth về POC, lessons learned, next steps.
- **Brainstorm report** — Phân tích 12 chủ đề (gaps/alternatives/trade-offs), header ghi "3 quyết định user xác nhận". Chất lượng phân tích rất tốt; là ADR de-facto của dự án.

### Sơ đồ

- **3 file draw.io + PNG** — overall / cloud / on-prem. Nội dung label khớp `system-architecture.md` ở mức rất cao (node pools, EMQX×3, Kafka RF3, CH×2+3 Keeper, DMZ Z3.5, keepalived VIP, warm standby, legend điều khiển ngược 2FA). Điểm lệch: sơ đồ có `API Gateway`, `Device Registry · Fleet Management`, `OTA` mà system-architecture chưa cover/đã defer (chi tiết ở `consistency-review.md`).

---

## 3. Trùng lặp / chồng chéo

| # | Nội dung trùng | Xuất hiện tại | Rủi ro | Ưu tiên |
|---|---|---|---|---|
| 1 | Bảng 7 quyết định D1–D7 | `system-architecture.md` §1, `README.md`, `CLAUDE.md`, `codebase-summary.md` | 4 bản sao → drift khi sửa (đã xảy ra: đếm "3/6/7 quyết định" lệch nhau giữa header system-architecture, journal, README) | **Medium** |
| 2 | Roadmap Phase A/B/C + exit criteria | `system-architecture.md` §14 và `project-roadmap.md` | 2 bản; roadmap chi tiết hơn nhưng nếu sửa 1 nơi sẽ lệch. Nên: system-architecture giữ tóm tắt + link roadmap | **Medium** |
| 3 | Tech stack listing | `README.md`, `system-architecture.md` D2, `codebase-summary.md`, `description.md` (generic) | Drift thấp nhưng README thêm chi tiết (MediaMTX, Ansible) không có trong D2 | **Low** |
| 4 | Mô tả 2 nền tảng hybrid | `description.md` ↔ `system-architecture.md` §1 | `description.md` là bản generic tiền-quyết-định (còn nhắc "API Gateway", "Digital Twin" chưa được resolve) — cần đánh dấu superseded-by hoặc cập nhật | **Medium** |
| 5 | Retention/alerting/SLO tables | POC (gốc) được "giữ nguyên" bằng tham chiếu trong `system-architecture.md` §7, §9 | Bảng gốc nằm trong file base64 khó đọc — nên trích bảng chính thức ra doc riêng thay vì tham chiếu vào file nặng | **Medium** |
| 6 | Timeline thi công ĐV3 | `project-roadmap.md` ↔ Technical Report §8.1 | Roadmap diễn giải theo tuần 0–16; PDF ghi 8–12 tuần giao hàng + 8–10 tuần thi công. Không mâu thuẫn nhưng là 2 cách trình bày cùng dữ kiện | **Low** |
| 7 | Gates G0–G6 | `project-roadmap.md` ↔ Collaboration Guidelines §5 | **Không phải trùng lặp mà là xung đột định nghĩa** — chi tiết tại `consistency-review.md` C-01 | **High** |

**Nhận xét chung:** bộ tài liệu có cấu trúc phân tầng tốt (reference → brainstorm → architecture → PDR → roadmap → diagrams), quan hệ đọc rõ ràng trong `codebase-summary.md`. Vấn đề chính không phải thiếu tổ chức mà là **drift giữa các bản sao** và **tài liệu tham chiếu chưa được đánh dấu phần nào còn hiệu lực / phần nào đã bị thay thế**.
