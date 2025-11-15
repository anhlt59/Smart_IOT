# Recommendations — Đề xuất cải thiện ưu tiên

**Ngày:** 2026-07-22 · **Nguyên tắc:** KHÔNG đề xuất nào đảo ngược quyết định sticky D1–D7. Đề xuất chạm quyết định user đã xác nhận được đánh dấu `[USER-DECISION]` — chỉ trình phương án, user chọn. Tham chiếu: AR-xx (`architecture-review.md`), C-xx (`consistency-review.md`), G-xx/M-xx (`gap-analysis.md`).

---

## Mục lục

1. [Critical](#1-critical--làm-ngay-chặn-phase-a)
2. [High](#2-high--trong-phase-a)
3. [Medium](#3-medium--trước-phase-b)
4. [Low](#4-low--khi-tiện)
5. [Bảng tổng hợp](#5-bảng-tổng-hợp)

---

## 1. CRITICAL — làm ngay, chặn Phase A

### R-01 · Thiết kế cơ chế khôi phục telemetry sau DR (AR-01, G-01)

- **Vấn đề:** §11 tuyên bố "telemetry RPO≈0 nhờ edge buffer 30d truyền bù" nhưng store-and-forward chỉ cover dữ liệu **chưa gửi**; dữ liệu đã ACK rồi mất do DR (ClickHouse backup daily, Kafka không replicate) không có cơ chế nào truyền lại.
- **Ảnh hưởng:** RPO telemetry thực = ≤24h chứ không phải ≈0. DR drill Phase B sẽ fail tiêu chí hoặc pass với dữ liệu thủng 1 ngày; SLA/hợp đồng tenant dựa trên con số sai.
- **Giải pháp đề xuất:** bổ sung thiết kế "replay-on-request": sau DR, cloud xác định khoảng thủng `[T1, T2]` per site → gửi lệnh replay qua downlink → sync service tại DMZ đọc TSDB site (≥12 tháng) hoặc gateway buffer, phát lại với cờ truyền bù + sequence gốc → ingest dedup (sequence + timestamp) ghi đè an toàn. Không đổi D5 — bổ sung để D5 đạt đúng tuyên bố. Cập nhật §11 với RPO thực tế từng lớp trong lúc chưa có cơ chế.

### R-02 · Chuẩn hóa lại hệ thống Gates (C-01)

- **Vấn đề:** `project-roadmap.md` định nghĩa lại G0–G6 thành milestone chương trình, xung đột với G0–G6 của Quy chế 2 đội (quality gates per phân hệ, có chữ ký); `system-architecture.md` §13 lại dùng nghĩa Quy chế.
- **Ảnh hưởng:** nhầm lẫn tại nghiệm thu — "pass G2" mang 2 nghĩa; Quy chế là tài liệu có hiệu lực giữa 2 đội, roadmap không được phép ghi đè đơn phương.
- **Giải pháp đề xuất:** giữ G0–G6 đúng nghĩa Quy chế; đổi tên milestone roadmap thành M-A1/M-B1/M-C1 (hoặc Gate-A/B/C); rà lại mọi tham chiếu "G2" trong system-architecture/PDR/roadmap về đúng nghĩa.

### R-03 · Chốt thành phần EMQX → Kafka (AR-02, M-11)

- **Vấn đề:** pipeline chuẩn ghi `EMQX → Kafka → Go ingest` nhưng không nêu thành phần chuyển bản tin từ EMQX vào Kafka. `[external — cần verify]` Kafka data-integration là tính năng EMQX Enterprise; bản OSS không có.
- **Ảnh hưởng:** Phase A tháng 2–3 (ingest service) không thể bắt đầu đúng; chọn sai → phát sinh license ngoài dự toán hoặc đảo thứ tự pipeline.
- **Giải pháp đề xuất:** quyết định 1 trong 2 trước Phase A: (a) EMQX Enterprise (lấy báo giá, thêm cost model); (b) Go ingest consume MQTT shared-subscription → produce Kafka (pipeline thành `EMQX → Go ingest → Kafka → consumers`, sửa §7 + cloud diagram). Khuyến nghị (b): đúng tinh thần OSS + kiểm soát backpressure/validate tại một chỗ; đánh đổi tự vận hành consumer group logic.

### R-04 · Sửa số liệu sai trong PDR (C-04)

- **Vấn đề:** PDR (spec chính thức, "Đã duyệt") ghi sai: 4 tủ IoT (đúng: 9), cảm biến CO₂ (không tồn tại — đúng: pH/COD/TSS/NH4/T° + PM2.5/PM10), 50 user on-prem (giới hạn nền tảng: 10 đồng thời), 30 stream camera (đúng: 32 camera), "nhiệt độ tựa sưởi" (garbled).
- **Ảnh hưởng:** đội dev build theo spec sai (thiết kế dashboard môi trường quanh CO₂ không có thật; sizing session cho 50 user không có cơ sở); mất tin cậy tài liệu.
- **Giải pháp đề xuất:** sửa PDR đối chiếu Technical Report Phụ lục A + §3.2 + §7.4; bump version PDR 1.1; thêm ghi chú nguồn cho từng con số hardware.

---

## 2. HIGH — trong Phase A

### R-05 · Trình user quyết định scope bị drop im lặng (C-02, G-08) `[USER-DECISION]`

- **Vấn đề:** Mobile App, GIS 3D/Digital Twin, voice control, dynamic QR có trong tài liệu nguồn (TechStack_Pipeline, Technical Report, description.md, diagrams) nhưng vắng khỏi PDR/roadmap không ghi chú descope. GIS 3D là cam kết trong hồ sơ thi công ĐV3 (IOC on-prem).
- **Ảnh hưởng:** kỳ vọng stakeholder lệch khỏi kế hoạch xây; phát hiện lúc UAT = trễ nhất và đắt nhất.
- **Giải pháp đề xuất:** lập bảng quyết định 4 hạng mục × 3 lựa chọn (in-scope PDR / out-of-scope có ghi chú / thuộc IOC on-prem không thuộc Cloud Platform) trình user ký. Sau đó cập nhật PDR + roadmap + đánh dấu superseded trong TechStack_Pipeline. **Không tự cắt** — đây là phạm vi user/chủ đầu tư quyết.

### R-06 · Đưa Interface Agreement + JSON Schema registry vào repo (G-02)

- **Vấn đề:** IA v1.0 và schema registry được mọi thiết kế tham chiếu nhưng chưa tồn tại trong repo; simulator (artifact chính thức DEV) không viết được khi chưa có schema.
- **Ảnh hưởng:** 2 đội không thể song song hóa đúng Quy chế (G1 nghĩa gốc yêu cầu IA ký); ingest service không có contract để validate.
- **Giải pháp đề xuất:** tạo repo/thư mục `interface-agreement/`: JSON Schema per loại bản tin (telemetry/event/heartbeat/cmd/ack) + bảng topic + quy ước chất lượng dữ liệu + tag list template; version + chữ ký 2 trưởng nhóm theo Quy chế §4.

### R-07 · Đặt deadline + owner cho các xác minh VNPT (AR-03, M-01/02/03/10/12)

- **Vấn đề:** 5 câu hỏi VNPT (multi-AZ, PostGIS/replica, MPLS coverage, quota region 2, Terraform provider) quyết định hình dạng HA/DR/IaC nhưng đang treo không deadline.
- **Ảnh hưởng:** Phase A tháng 1 (setup VPC/VKS/managed) có thể phải làm lại nếu câu trả lời khác giả định.
- **Giải pháp đề xuất:** gửi VNPT bảng câu hỏi chính thức (RFI) trước Phase A kickoff; mỗi câu gắn "nếu KHÔNG → phương án B" đã có sẵn trong brainstorm (vd PG managed không PostGIS → CloudNativePG; không multi-AZ → ghi rõ vào SLA khách).

### R-08 · Threat model + security incident response + crypto standards (AR-05, AR-06, G-05, G-06)

- **Vấn đề:** kiểm soát an ninh tốt nhưng không có threat model chứng minh độ phủ; chưa có quy trình security incident (khác sự cố vận hành P1–P4); tài liệu tham chiếu còn "md5 encryption"/"tls 1.2" chưa bị phủ quyết chính thức.
- **Ảnh hưởng:** lỗ hổng không hệ thống hóa được (vd compromise cert gateway → chuỗi hành động thu hồi chưa định nghĩa); dev có thể tham khảo chuẩn mã hóa lỗi thời.
- **Giải pháp đề xuất:** (1) threat model theo IEC 62443 zone/conduit đã có sẵn (thêm SL-target per zone) + STRIDE cho 4 luồng critical; (2) security IR playbook: compromise cert, ransomware site, lộ CI credential; (3) 1 trang crypto standards (TLS 1.3 ưu tiên/1.2 floor, AES-GCM at-rest, Argon2/bcrypt password, cấm MD5/SHA1 cho mục đích an ninh) đặt trong docs/ và ghi chú superseded vào TechStack_Pipeline.

### R-09 · IP/VLAN addressing plan cho fleet 30 site (AR-07, G-04)

- **Vấn đề:** zoning mới ở mức khái niệm; chưa có scheme địa chỉ tránh trùng khi 30 site cùng nối MPLS về cloud.
- **Ảnh hưởng:** trùng subnet giữa site = làm lại network lúc đã có site chạy production; blueprint site không thể "instantiate" tự động nếu thiếu quy tắc cấp phát.
- **Giải pháp đề xuất:** cấp phát block per site dạng công thức (vd `10.{site_id}.{vlan}.0/24`), bảng VLAN ID chuẩn (OT/server/DMZ/camera/mgmt/IT), firewall rule matrix chuẩn kèm blueprint; ĐV3 hiện hữu giữ nguyên, đánh số như site 1 as-built.

### R-10 · Sequence diagrams cho 4 luồng critical (G-03)

- **Vấn đề:** điều khiển ngược, backfill, onboarding, DR failover — nhiều hop, nhiều failure mode, chưa có sơ đồ trình tự.
- **Ảnh hưởng:** mỗi dev tự suy diễn xử lý lỗi tại từng hop → hành vi không nhất quán, khó review.
- **Giải pháp đề xuất:** 4 sequence diagram (Mermaid trong docs/ hoặc draw.io cùng thư mục diagrams), kèm bảng failure mode per hop (timeout, retry, dedup, alert).

### R-11 · Thiết kế compliance flow quan trắc TT 10/2021 (G-07, M-09) `[USER-DECISION một phần]`

- **Vấn đề:** docs nhắc datalogger đạt TT 10/2021 nhưng không thiết kế luồng truyền số liệu về cơ quan quản lý; chưa rõ trách nhiệm thuộc datalogger/đội IoT hay platform.
- **Ảnh hưởng:** rủi ro pháp lý cho chủ đầu tư nếu kênh báo cáo không được vận hành/giám sát; phát hiện muộn khi thanh tra.
- **Giải pháp đề xuất:** xác nhận phạm vi với chủ đầu tư (M-09); nếu ngoài platform → ghi rõ "out of scope, datalogger tự truyền" trong PDR; nếu platform tham gia → thêm FR + giám sát uptime kênh báo cáo vào NOC dashboard.

---

## 3. MEDIUM — trước Phase B

### R-12 · ADR hóa D1–D7 + sửa drift đếm quyết định (C-03, G-09)

- **Vấn đề:** header ghi 3, journal ghi 6, bảng có 7 quyết định; không trace được quyết định nào user xác nhận trực tiếp.
- **Ảnh hưởng:** cơ chế sticky decision (quy tắc repo) mất hiệu lực khi không rõ nguồn xác nhận; audit sau này khó phân xử.
- **Giải pháp đề xuất:** 7 file `docs/adr/adr-00X-*.md` (context, decision, alternatives đã bác — trích từ brainstorm, nguồn xác nhận + ngày, status); sửa header system-architecture; các bản sao (README, CLAUDE.md, codebase-summary) chỉ giữ bảng tóm tắt + link.

### R-13 · Cập nhật lựa chọn observability agent/on-call (AR-10, M-13)

- **Vấn đề:** `[external — cần verify]` Grafana Agent EOL 2025-11; Grafana OnCall OSS maintenance mode.
- **Ảnh hưởng:** triển khai Phase A trên component hết vòng đời → migrate sớm ngoài kế hoạch.
- **Giải pháp đề xuất:** verify trạng thái upstream; nếu đúng → thay "Grafana Agent" bằng "Grafana Alloy" trong §9 (config tương thích), chọn on-call thay thế (vd tích hợp Alertmanager → Telegram + lịch trực đơn giản, hoặc công cụ khác) trước khi dựng LGTM.

### R-14 · Định nghĩa hành vi degraded + runbook cho data host on-prem (AR-04)

- **Vấn đề:** R760xs (PG/TimescaleDB/Redis local) hỏng → hành vi IOC local + rule engine + độ mất dữ liệu chưa định nghĩa. Hardware cố định theo D1 — chỉ xử lý bằng software.
- **Ảnh hưởng:** site mù vận hành local không kiểm soát được thời gian khôi phục; đội site không có thao tác chuẩn.
- **Giải pháp đề xuất:** (giữ nguyên BOM) định nghĩa degraded mode (gateway vẫn buffer + đẩy cloud trực tiếp qua bridge? dashboard cloud thay thế tạm?); backup local DB nightly đã có → thêm mục tiêu thời gian restore lên app host dự phòng (R660xs standby còn tài nguyên); runbook thao tác + drill trong kỳ bảo trì.

### R-15 · Kế hoạch đo capacity ĐV3 + load test (AR khu 9, G-10, G-11, M-05)

- **Vấn đề:** mọi số sizing là `[assumption]`; chưa có kế hoạch đo và load test xác nhận 2.000–6.000 msg/s + alarm ≤2s dưới tải.
- **Ảnh hưởng:** Phase C nhân bản site trên sizing chưa kiểm chứng; phát hiện thiếu capacity khi đã có nhiều tenant.
- **Giải pháp đề xuất:** sau go-live ĐV3 đo ≥2 tuần (msg/s, bytes/ngày, event AI/ngày, lag); dùng simulator bắn load ×30 site trên STG; cập nhật §7 + gắn vào exit criteria Phase B.

### R-16 · Hợp nhất test strategy + khôi phục chaos test (G-11, AR khu 7)

- **Vấn đề:** isolation test, simulator, restore test, DR drill nằm rải rác; chaos test có trong brainstorm nhưng rơi khỏi system-architecture.
- **Giải pháp đề xuất:** 1 tài liệu test-strategy: ma trận loại test × môi trường × tần suất × owner; đưa chaos test (kill broker pod, drain node, cắt MPLS site) vào lịch quý trên STG như brainstorm R3 đề xuất.

### R-17 · Chốt PG tenancy model (AR-13, C — D6 ghi "RLS/schema")

- **Vấn đề:** RLS và schema-per-tenant khác nhau về migration, connection pooling, isolation test.
- **Ảnh hưởng:** đội dev Phase A (PG schema + RLS ở roadmap tháng 2–3) cần 1 mô hình rõ.
- **Giải pháp đề xuất:** khuyến nghị RLS thuần cho bảng dùng chung + tiêu chí nâng cấp lên schema/DB riêng khi tenant yêu cầu cách ly cứng (khớp open item #6). Ghi thành ADR. Không đổi D6 — làm rõ cách thực hiện D6.

### R-18 · Failback + region-2 capacity vào DR design (AR-08, G-23, M-03)

- **Vấn đề:** DR một chiều — chưa có tiêu chí + quy trình quay về region 1 (đồng bộ ngược dữ liệu phát sinh ở region 2); quota region 2 chưa xác nhận.
- **Giải pháp đề xuất:** thêm mục failback vào §11 (điều kiện, trình tự đảo replication, cutover DNS); RFI VNPT quota region 2 (R-07).

### R-19 · Trích alert catalog + retention/threshold tables ra doc chính thức (G-19, document-summary #5)

- **Vấn đề:** bảng ngưỡng cảnh báo + retention "giữ nguyên bảng POC" — nằm trong file base64 600KB không đọc trực tiếp được.
- **Ảnh hưởng:** nguồn sự thật vận hành nằm trong file mà chính CLAUDE.md cấm đọc; khó review/sửa.
- **Giải pháp đề xuất:** trích thành `docs/operations-thresholds-retention.md` (hoặc tương tự), đánh dấu POC là lịch sử.

### R-20 · Đồng bộ tài liệu vệ tinh + đánh dấu superseded (C-06, C-07, C-08, C-11, C-14)

- **Vấn đề:** description.md còn tiền-quyết-định (API Gateway, Digital Twin); diagrams có OTA/Device Registry lệch phase; TechStack_Pipeline chứa nội dung đã thay thế không đánh dấu.
- **Giải pháp đề xuất:** (1) chốt API Gateway có/không (M-10) rồi sửa 3 nơi; (2) thêm nhãn "(future/Phase C)" cho OTA + Device Registry trên diagram hoặc bỏ; (3) thêm khối "Trạng thái hiệu lực" đầu TechStack_Pipeline/POC: liệt kê mục đã bị D2/D6/D7 thay thế.

---

## 4. LOW — khi tiện

| ID | Đề xuất | Tham chiếu |
|---|---|---|
| R-21 | Sửa typo PDR ("múi", "nhiệt độ tựa sưởi", "+dùng"), roadmap ("Dr drill"), định nghĩa hoặc bỏ "Phase D" | C-13, C-15 |
| R-22 | Sửa CLAUDE.md "4 server Dell" → "3 Dell + 1 HPE DL380"; README "Brainstorm Report (7 quyết định)" → mô tả đúng | C-12, C-16 |
| R-23 | Chốt số kit 4G (4 vs 5) sau khi đối chiếu bảng khối lượng gốc (M-08), đồng bộ mọi nơi | C-05 |
| R-24 | Naming/tagging convention cloud resources (cost allocation per tenant/site) | G-22 |
| R-25 | Thiết kế nhỏ cho EVN API polling (component, zone, credential Vault) | G-21 |
| R-26 | UPS runtime target + graceful shutdown vào site blueprint | G-24 |
| R-27 | Ghi nhận rủi ro chấp nhận: FortiGate đơn chiếc (spare/RMA + config backup), NVR/HDD đơn (backup evidence sự kiện lên Object Storage), DL380 đơn | AR-11, AR-14 |
| R-28 | Chọn frontend stack chính thức (web cloud) — hiện React (roadmap) vs Bootstrap/Mapbox (TechStack) chưa chốt | C-18, G-14 |

---

## 5. Bảng tổng hợp

| ID | Đề xuất | Mức | Chặn mốc | User quyết? |
|---|---|---|---|---|
| R-01 | Cơ chế replay telemetry sau DR | **Critical** | Phase B DR drill | — |
| R-02 | Chuẩn hóa Gates (bỏ định nghĩa lại G0–G6) | **Critical** | Nghiệm thu Phase A | — |
| R-03 | Chốt thành phần EMQX→Kafka | **Critical** | Phase A tháng 2 | — |
| R-04 | Sửa số liệu PDR | **Critical** | Phase A kickoff | — |
| R-05 | Quyết định scope Mobile/GIS 3D/voice/QR | **High** | PDR freeze | ✅ |
| R-06 | Interface Agreement + Schema registry vào repo | **High** | Phase A tháng 2 | — |
| R-07 | RFI VNPT có deadline (5 câu hỏi) | **High** | Phase A kickoff | — |
| R-08 | Threat model + security IR + crypto standards | **High** | ĐV3 go-live | — |
| R-09 | IP/VLAN plan 30 site | **High** | Site #2 | — |
| R-10 | 4 sequence diagrams | **High** | Phase A | — |
| R-11 | Compliance flow TT 10/2021 | **High** | ĐV3 go-live | ✅ (phạm vi) |
| R-12 | ADR D1–D7 + sửa drift đếm quyết định | **Medium** | Sớm | — |
| R-13 | Grafana Alloy / on-call thay thế | **Medium** | LGTM setup | — |
| R-14 | Degraded mode + runbook data host on-prem | **Medium** | Phase B | — |
| R-15 | Đo capacity + load test | **Medium** | Phase B/C | — |
| R-16 | Test strategy + chaos test | **Medium** | Phase B | — |
| R-17 | Chốt PG tenancy model (ADR) | **Medium** | Phase A tháng 2–3 | — |
| R-18 | Failback + quota region 2 | **Medium** | Phase B | — |
| R-19 | Trích alert catalog khỏi POC | **Medium** | Phase A LGTM | — |
| R-20 | Đồng bộ tài liệu vệ tinh + superseded marks | **Medium** | Phase A | — |
| R-21→R-28 | Nhóm Low (typo, naming, EVN, UPS, frontend...) | **Low** | Khi tiện | R-28 nên hỏi |
