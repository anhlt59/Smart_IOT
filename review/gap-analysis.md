# Gap Analysis — Những gì còn thiếu

**Ngày:** 2026-07-22 · **Bối cảnh:** repo docs-only, giai đoạn thiết kế, Phase A dự kiến bắt đầu tháng 8. Gap được đánh giá theo tiêu chí "cần trước mốc nào" chứ không phải "thiếu là xấu" — nhiều gap chấp nhận được ở giai đoạn này nếu có kế hoạch.

---

## Mục lục

1. [Bảng tổng hợp gap](#1-bảng-tổng-hợp-gap)
2. [Chi tiết gap theo nhóm](#2-chi-tiết-gap-theo-nhóm)
3. [Missing Information — cần bên ngoài trả lời](#3-missing-information--cần-bên-ngoài-trả-lời)

---

## 1. Bảng tổng hợp gap

| ID | Gap | Nhóm | Mức | Cần trước |
|---|---|---|---|---|
| G-01 | Cơ chế khôi phục telemetry sau DR (replay/re-request từ site) | Design | **Critical** | Phase B (DR drill #1) |
| G-02 | Interface Agreement v1.0 + JSON Schema registry chưa có trong repo | Contract | **High** | Phase A (ingest dev) |
| G-03 | Sequence diagrams cho 4 luồng critical | Diagram | **High** | Phase A |
| G-04 | IP addressing / VLAN numbering plan cho 30 site | Network | **High** | Site #2 (Phase B) |
| G-05 | Threat model + security incident response plan | Security | **High** | Phase A go-live ĐV3 |
| G-06 | Crypto standards chính thức (phủ quyết MD5/TLS cũ ở tài liệu tham chiếu) | Security | **High** | Phase A (trước dòng code đầu) |
| G-07 | Quy trình truyền số liệu quan trắc về cơ quan quản lý (TT 10/2021, NĐ 40/2015) | Compliance | **High** | Phase A go-live ĐV3 |
| G-08 | Quyết định scope: Mobile App, GIS 3D/Digital Twin, voice, dynamic QR | Scope | **High** `[USER-DECISION]` | PDR freeze |
| G-09 | ADR chính thức cho D1–D7 | Governance | **Medium** | Sớm nhất có thể |
| G-10 | Capacity planning & measurement plan (thay số `[assumption]`) | Sizing | **Medium** | Phase B |
| G-11 | Test strategy tổng thể (load, chaos, failover site, isolation spec) | QA | **Medium** | Phase B |
| G-12 | Runbooks vận hành (NOC, on-call, edge failure, cert expiry, DR, failback) | Ops | **Medium** | Phase B (một phần đã lên kế hoạch) |
| G-13 | Data model / schema design (PG, ClickHouse DDL) + API spec (OpenAPI) | Design | **Medium** | Phase A (song song sprint ingest/API) |
| G-14 | Quyết định frontend stack (web dashboard cloud) | Stack | **Medium** | Phase A tháng 2–3 |
| G-15 | SLA document per tenant + error budget policy | Business | **Medium** | Trước hợp đồng tenant #2 |
| G-16 | DPA template + masking policy biển số (PDPD NĐ 13/2023) | Compliance | **Medium** | Trước go-live camera AI |
| G-17 | Cost model đối chiếu báo giá VNPT | Finance | **Medium** | Phase A kickoff |
| G-18 | Deployment diagram per environment (DEV/STG/PROD topology) | Diagram | **Medium** | Phase A |
| G-19 | Alert catalog chính thức (trích từ POC ra doc riêng) | Ops | **Medium** | Phase A (LGTM setup) |
| G-20 | Onboarding tenant/site checklist phi kỹ thuật (hợp đồng, DPA, SLA) | Process | **Low** | Phase B |
| G-21 | EVN API integration design (component, zone, credential) | Design | **Low** | Sprint năng lượng |
| G-22 | Naming/tagging convention cloud resources | Infra | **Low** | Phase A Terraform |
| G-23 | Failback procedure sau DR (region 2 → region 1) | DR | **Medium** | Phase B |
| G-24 | UPS runtime target + shutdown có trật tự on-prem | Ops | **Low** | Site blueprint |

---

## 2. Chi tiết gap theo nhóm

### Design gaps

**G-01 · Khôi phục telemetry sau DR — Critical**
`system-architecture.md` §11 tuyên bố ClickHouse "RPO≈0 thực tế nhờ edge buffer 30d truyền bù". Cơ chế store-and-forward hiện tại (gateway SD buffer + bridge backfill flag) chỉ truyền bù dữ liệu **chưa gửi thành công**. Kịch bản DR mất dữ liệu **đã nhận** (ClickHouse backup daily → mất tới 24h; Kafka không replicate): không có thiết kế nào cho cloud yêu cầu site gửi lại khoảng dữ liệu đã ACK. Nguồn dữ liệu để replay có sẵn (gateway buffer 30d, TSDB site ≥12 tháng) nhưng **thiếu cơ chế kích hoạt + API + dedup khi ghi đè**. Không có nó, RPO telemetry thực = 24h.

**G-03 · Sequence diagrams — High.** 4 luồng phức tạp nhiều bên tham gia chưa có sơ đồ trình tự:
1. Điều khiển ngược: user 2FA → Cloud API → Kafka → EMQX cloud → bridge → EMQX edge → gateway → PLC → ack ngược (≤5s) — kèm timeout/idempotency/failure tại từng hop.
2. Backfill sau mất kết nối: buffer → cờ truyền bù → dedup sequence → ghi lịch sử đúng timestamp gốc.
3. Onboarding site (Temporal workflow): tenant/park → cert → ACL → schema → dashboard → smoke test.
4. DR failover: phát hiện → DNS switch → IaC dựng stack → bridge reconnect → (G-01) replay.

**G-13 · Data model + API spec — Medium.** Chưa có DDL ClickHouse (bảng telemetry/event, partition, TTL), PG schema (tenant, park, device, alarm lifecycle, audit), OpenAPI cho REST v1. Bình thường ở giai đoạn này; cần trước sprint tương ứng trong Phase A (roadmap tháng 2–3 đã cần PG schema + RLS).

**G-21 · EVN API — Low.** Nguồn dữ liệu duy nhất đi qua Internet REST (không qua MQTT/gateway): component nào poll (on-prem hay cloud), zone đặt ở đâu, credential quản lý qua Vault ra sao — chưa thiết kế.

### Contract gaps

**G-02 · Interface Agreement + Schema registry — High.** Toàn bộ kiến trúc dựa trên "Interface Agreement v1.0" và "JSON Schema registry trong Git" nhưng repo chưa có cả hai (Quy chế chỉ định nghĩa yêu cầu cấp nhóm, đặc tả chi tiết "do hai đội soạn riêng"). Simulator (artifact chính thức của DEV) không thể viết nếu chưa có schema. Gate G0/G1 (nghĩa Quy chế) yêu cầu IA ký trước khi 2 đội song song.

### Diagram gaps

Hiện có 3 sơ đồ kiến trúc tĩnh (tốt). Thiếu:
- **Sequence diagram** (G-03 — High).
- **Deployment diagram per env** (G-18 — Medium): DEV/STG/PROD khác nhau thế nào (DEV+STG chung VPC — service nào chung, tách gì), simulator đứng đâu.
- **Network diagram chi tiết** (thuộc G-04 — High): hiện bảng VLAN mức zone; cần bản vẽ IP plan, VLAN ID, firewall matrix để nhân bản qua blueprint.

### Security & Compliance gaps

**G-05 · Threat model + security IR — High.** Chưa có threat model (STRIDE per luồng hoặc IEC 62443 zone/conduit SL-target — kiến trúc đã ánh xạ Purdue, thêm SL là bước tự nhiên). Chưa có security incident response (phân biệt với sự cố vận hành P1–P4): compromise gateway cert → thu hồi thế nào trong bao lâu; ransomware site; lộ credential CI.

**G-06 · Crypto standards — High.** Tài liệu tham chiếu (TechStack_Pipeline) chứa "md5 encryption", "tls 1.2" — đã lỗi thời/sai nhưng chưa có tài liệu chuẩn mã hóa chính thức phủ quyết (thuật toán cho at-rest, in-transit, hashing password, chữ ký bản tin). Rủi ro: dev tham khảo tài liệu cũ.

**G-07 · Compliance flow quan trắc — High + Missing Information.** Docs nhắc ADAM-3600 "đạt TT 10/2021" và cảnh báo theo "NĐ 40/2015" nhưng **không tài liệu nào thiết kế luồng truyền số liệu quan trắc tự động về Sở TN&MT** (yêu cầu trọng tâm của TT 10/2021 đối với trạm quan trắc nước thải tự động). Cần xác nhận: luồng này do datalogger gửi trực tiếp (ngoài phạm vi platform) hay platform phải forward? Ai chịu trách nhiệm uptime kênh báo cáo pháp lý? `[Missing Information — cần xác nhận phạm vi với chủ đầu tư/đội IoT]`

**G-16 · DPA + masking — Medium.** Đã nhận diện trong open item #7 nhưng chưa có template/chính sách. Cần trước khi camera AI + nhận diện biển số go-live.

### Scope gaps `[USER-DECISION]`

**G-08 · High.** Các hạng mục có trong tài liệu nguồn nhưng vắng trong PDR/system-architecture mà không có ghi chú descope:

| Hạng mục | Nguồn | Trạng thái trong docs chính |
|---|---|---|
| Mobile App | TechStack_Pipeline giai đoạn 4; description.md ("web/mobile") ; overall diagram ("Web · Mobile · Open API") | PDR không có FR mobile |
| GIS 3D / Digital Twin | Technical Report §7.1 (IOC on-prem có GIS 3D); TechStack giai đoạn 3; description.md | PDR chỉ có "map" trong dashboard; cloud scope không rõ |
| Voice control tiếng Việt | TechStack (voice2action) | Vắng hoàn toàn |
| Dynamic QR + 2FA | TechStack (mọi giai đoạn); brainstorm §9 nhắc "2FA TOTP + dynamic QR (stack đích)" | system-architecture chỉ còn TOTP |
| Báo cáo compliance PDF/Excel tự động | Technical Report §7.1 (02 mẫu chuẩn); PDR có FR #6 reporting ✓ | Một phần có — mẫu báo cáo chưa spec |

Lưu ý: GIS 3D/Digital Twin là chức năng **đã cam kết trong hồ sơ thi công ĐV3** (nền tảng IOC on-prem) — nếu Cloud Platform không làm, vẫn phải rõ ai làm cho on-prem (liên quan open item #5: 1 codebase hay 2 sản phẩm).

### Governance / Ops gaps

**G-09 · ADR — Medium.** D1–D7 sticky nhưng nằm trong bảng + journal + brainstorm rải rác (đếm số quyết định đã lệch — xem consistency C-03). 7 file ADR ngắn (context/decision/consequences/nguồn xác nhận/status) giải quyết cả trace lẫn drift.

**G-10 · Capacity — Medium.** Số liệu `[assumption]` đã đánh dấu tốt; thiếu **kế hoạch đo**: metric nào tại ĐV3 (msg/s, bytes/day, event AI/day), đo bao lâu (≥2 tuần?), ngưỡng nào kích hoạt re-size, ai cập nhật §7.

**G-11 · Test strategy — Medium.** Đã có isolation test CI + simulator + restore test + DR drill (rải rác). Thiếu tài liệu hợp nhất: load test (2.000–6.000 msg/s + alarm ≤2s dưới tải), chaos test (brainstorm có, system-architecture rơi mất), failover drill site (MPLS→IPsec), tiêu chí P2P tự động hóa với simulator.

**G-12 · Runbooks — Medium.** Roadmap Phase B có DR runbook + NOC dashboard; thiếu danh mục runbook đầy đủ: edge data-host failure (AR-04), cert-expiry emergency, bridge lag/backfill backlog xử lý, failback (G-23), FortiGate RMA.

**G-15 · SLA + error budget — Medium.** SLO nội bộ có; SLA đối ngoại (open item #6 "SLA cam kết với chủ đầu tư") chưa chốt → chưa thể viết error budget policy + cam kết đền bù. Ràng buộc lên mức đầu tư HA/DR đã ghi nhận trong brainstorm.

---

## 3. Missing Information — cần bên ngoài trả lời

Tổng hợp các điểm không thể kết luận từ nội dung `docs/` (trùng với Open Items §15 + phát hiện mới của review):

| # | Câu hỏi | Chặn gì | Nguồn cần |
|---|---|---|---|
| M-01 | VNPT multi-AZ trong 1 region? SLA managed PG/Kafka/Redis? PG có PostGIS + cross-region replica? | Thiết kế HA/DR chi tiết Phase A | VNPT (open item #1) |
| M-02 | MPLS/L3VPN coverage + giá theo tỉnh KCN mục tiêu | Chọn site Phase C, cost model | VNPT (open item #2) |
| M-03 | Quota/capacity region 2 (HCM) đủ nhận full stack khi DR? | Tính khả thi RTO 1–2h | VNPT (mới — từ review AR-08) |
| M-04 | ECU-1051/EdgeLink hỗ trợ EST/SCEP nạp cert tự động? | PKI rotation design | Advantech / đội IoT (open item #4) |
| M-05 | Message rate thực tế ĐV3 sau go-live | Capacity §7 | Đo thực tế (open item #3) |
| M-06 | IOC on-prem + Cloud: 1 codebase 2 target hay 2 sản phẩm? | CI/CD, blueprint, scope GIS 3D | User/Product (open item #5) |
| M-07 | SLA cam kết hợp đồng vs 99.9% design; tenant nào cần cách ly DB cứng? | Error budget, tenancy mode | Business (open item #6) |
| M-08 | Số gateway ECU-1051 chính xác (8 vs 9) + số kit 4G (4 vs 5) | Sửa nhất quán docs | Bảng khối lượng thiết bị gốc ĐV3 (mới — C-05) |
| M-09 | Luồng báo cáo quan trắc về Sở TN&MT: ai chịu trách nhiệm, platform có tham gia? | Scope compliance G-07 | Chủ đầu tư + đội IoT (mới) |
| M-10 | VNPT có API Gateway managed không (nếu quyết định dùng — C-06)? | Ingress design | VNPT (mới) |
| M-11 | EMQX cloud: Enterprise license (Kafka data-integration) hay OSS + Go ingest tự viết? | Pipeline Phase A (AR-02) | Quyết định kỹ thuật + báo giá EMQX (mới) |
| M-12 | Terraform provider VNPT Cloud coverage đủ cho "mọi resource là code"? | IaC Phase A | VNPT / thử nghiệm PoC nhỏ (mới) |
| M-13 | Trạng thái Grafana Agent (EOL) / Grafana OnCall (maintenance) — chọn thay thế? | Observability design | Verify web trước Phase A (mới) |
