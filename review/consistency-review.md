# Consistency Review — Kiểm tra tính nhất quán giữa các tài liệu

**Ngày:** 2026-07-22 · **Phương pháp:** đối chiếu chéo 15 tài liệu (docs chính, PDF strip text, drawio labels, journal, brainstorm report, README).

---

## Mục lục

1. [Tổng quan kết quả](#1-tổng-quan-kết-quả)
2. [Xung đột nghiêm trọng (High)](#2-xung-đột-nghiêm-trọng-high)
3. [Không nhất quán mức Medium](#3-không-nhất-quán-mức-medium)
4. [Không nhất quán mức Low](#4-không-nhất-quán-mức-low)
5. [Các điểm ĐÃ nhất quán tốt](#5-các-điểm-đã-nhất-quán-tốt)

---

## 1. Tổng quan kết quả

| Hạng mục kiểm tra | Kết quả |
|---|---|
| Kiến trúc (nguyên tắc, quyết định) | ✅ Nhất quán cao giữa system-architecture ↔ brainstorm ↔ diagrams; ⚠️ đếm số quyết định lệch (C-03) |
| Thành phần / Service | ⚠️ 3 xung đột (API Gateway, OTA, Device Registry timing) |
| Số liệu hardware | ❌ PDR sai đáng kể so với nguồn (C-04); PDF nguồn tự mâu thuẫn (C-05) |
| Thuật ngữ | ✅ Tốt (EMQX/Kafka/ClickHouse/tenant/park/cell nhất quán) |
| Naming convention | ✅ Tốt (kebab-case docs, topic standard, cert CN thống nhất) |
| Diagram ↔ text | ✅ Khớp ~90%; 3 điểm lệch có chủ đích cần ghi chú (C-09, C-10, C-11) |
| Deployment model | ✅ Docker Compose on-prem / VKS cloud nhất quán tuyệt đối trên mọi tài liệu (D7 được tôn trọng) |
| Quy trình / Gates | ❌ Roadmap định nghĩa lại G0–G6 khác Quy chế (C-01) |

---

## 2. Xung đột nghiêm trọng (High)

### C-01 · Gates G0–G6 bị định nghĩa lại khác Quy chế 2 đội — **High**

| Gate | Quy chế 2 đội (nguồn gốc, §5) | project-roadmap.md |
|---|---|---|
| G0 | Khảo sát & yêu cầu | Design review (IA v1.0, tag list) |
| G1 | Thiết kế & Interface (IA v1.0 ký) | **Phase A complete** |
| G2 | Dựng nền tảng & lắp đặt | **Phase B complete (site #2)** |
| G3 | Tích hợp P2P (100% tag pass) | P2P test readiness |
| G4 | Hiển thị & cảnh báo | UAT readiness |
| G5 | SIT/UAT | Go-live approval (≥10 KCN) |
| G6 | Vận hành & bảo trì | Scale-out (cell #2, >30 KCN) |

- Quy chế: G0–G6 là **quality gates lặp lại per phân hệ/per site** trong vòng đời tích hợp 2 đội. Roadmap: G0–G6 thành **milestone 1 lần của chương trình**. Cùng nhãn, 2 nghĩa → nguy cơ hiểu nhầm khi nghiệm thu ("pass G2" nghĩa là gì?).
- `system-architecture.md` §13 dùng "bàn giao G2" theo nghĩa Quy chế (onboarding site) → mâu thuẫn với nghĩa roadmap ngay trong bộ docs chính.
- **Đề xuất:** giữ G0–G6 đúng nghĩa Quy chế (tài liệu gốc có chữ ký 2 đội); đặt tên khác cho milestone chương trình (M1/M2/M3 hoặc Gate-A/B/C). → `recommendations.md` R-02.

### C-02 · Bảng "5 giai đoạn phần mềm (từ TechStack_Pipeline)" không khớp tài liệu nguồn — **High**

| Giai đoạn | TechStack_Pipeline (nguồn) | project-roadmap.md (ghi "hợp nhất từ TechStack_Pipeline") |
|---|---|---|
| 1 | Số hóa hạ tầng & thu thập dữ liệu (T1–3) | Setup dev env (W1–2) |
| 2 | **Camera & AI An ninh/PCCC** (T4–5) | Ingest (W3–6) |
| 3 | **GIS hóa & Digital Twin 3D** (T6–7) | API (W7–10) |
| 4 | **Điều khiển tập trung & Mobile App** (T8) | UI (W11–16) |
| 5 | Đào tạo, chuyển giao & bảo trì (T9) | Ops (W17–26) |

- Nội dung 2 bảng khác nhau hoàn toàn nhưng roadmap tuyên bố là "hợp nhất" từ nguồn. Các hạng mục **Camera AI, GIS/Digital Twin 3D, Mobile App, Đào tạo** biến mất khỏi roadmap mà không có ghi chú descope.
- Theo quy tắc `review-audit-self-decision.md`: đây có thể là cắt phạm vi chưa được user xác nhận → **không tự kết luận**, trình user: giữ scope nguồn / xác nhận descope / tách roadmap phần mềm riêng. `[USER-DECISION]` → R-05.

### C-03 · Số lượng "quyết định đã chốt" lệch 3 nơi — **High** (vì đụng cơ chế sticky)

| Tài liệu | Ghi nhận |
|---|---|
| `system-architecture.md` dòng 3 | "Đã duyệt (**3 quyết định** kiến trúc chốt 2026-07-22)" |
| Brainstorm report header | "**3 quyết định** — USER ĐÃ XÁC NHẬN TOÀN BỘ" (connectivity, DR, tenancy) |
| Journal 260722 | "**6 quyết định** chốt" (D1–D6, không có D7) |
| `system-architecture.md` bảng §1, README, CLAUDE.md | **7 quyết định** D1–D7 |

- Hệ quả: không trace được quyết định nào **user xác nhận trực tiếp** (D4, D5, D6 chắc chắn; D7 có ghi "xác nhận 2026-07-22") vs quyết định nào tổng hợp từ scope brainstorm (D1, D2, D3 vốn là "scope đã chốt với user" ở đầu brainstorm). Cơ chế sticky decision cần trail rõ.
- **Đề xuất:** cập nhật header system-architecture thành "7 quyết định (D1–D3 scope confirm, D4–D7 user confirm 2026-07-22)" hoặc lập ADR từng quyết định ghi rõ nguồn xác nhận. → R-12.

### C-04 · PDR sai số liệu so với mọi nguồn khác — **High** (PDR là spec chính thức)

| Mục trong PDR | PDR ghi | Nguồn đúng |
|---|---|---|
| §3 Hardware | "**4 tủ IoT ECU-1051**" | 9 tủ (system-architecture §3, CLAUDE.md, on-prem diagram, Technical Report Phụ lục A + §5.1); con số 4 có lẽ nhầm từ "4 tủ kèm 4G" |
| §3 Phân hệ môi trường | "**CO₂**, độ ẩm, nhiệt độ" | Không nguồn nào có CO₂. Thực tế: pH/COD/TSS/NH4/nhiệt độ (nước thải) + PM2.5/PM10/nhiệt độ/độ ẩm (không khí Smart Pole) — Technical Report §3.2 |
| §5 Concurrency | "**50 on-prem local** users" | Giới hạn nền tảng IOC on-prem: **10 user đồng thời** (Technical Report §7.4, gói duy trì) |
| §3 An ninh | "Camera ONVIF (**30 stream**)" | 27 bullet + 2 PTZ tầm xa + 3 PTZ Smart Pole = 32 camera (Technical Report) |
| §3 Năng lượng | "nhiệt độ tựa sưởi" (vô nghĩa), "kVAR" | Technical Report: U, I, P, cosφ, kWh (không nêu kVAR) |

- **Đề xuất:** sửa PDR đối chiếu Technical Report trước khi Phase A bắt đầu (spec sai → đội dev build sai). → R-04.

---

## 3. Không nhất quán mức Medium

### C-05 · PDF Technical Report tự mâu thuẫn về số gateway/4G — **Medium** + **Missing Information**

- §6.1.1 ghi "Số lượng: **08 cái**" ECU-1051 và "2 tủ PCCC/báo cháy"; nhưng §5.3.3 ghi "Lắp **03 tủ IoT**" PCCC, và Phụ lục A liệt kê **9 tủ** có ECU-1051 (XLNT 1, trạm bơm 1, PCCC 3, chiếu sáng 3, cấp nước 1). §5.1 ghi "9 tủ IoT hiện trường".
- Module 4G: §6.1.1 "4 bộ kèm module 4G" vs Phụ lục A (trạm bơm 1 + chiếu sáng 3 + cấp nước 1 = **5 bộ**) vs "05 SIM data" (§4.2, §8.4). `system-architecture.md` ghi "4 tủ kèm 4G".
- Các docs dẫn xuất chọn số 9 (khớp Phụ lục A) — hợp lý; nhưng số 4G kit chưa thể kết luận. **Missing Information:** cần đối chiếu bảng khối lượng thiết bị gốc (tài liệu căn cứ §1.3 của PDF) để chốt 8 vs 9 gateway và 4 vs 5 kit 4G, rồi thống nhất mọi nơi.

### C-06 · API Gateway: có ở 2 nơi, vắng ở nguồn sự thật — **Medium**

- `description.md` (danh sách managed services) và **cloud diagram** ("API Gateway — routing · rate limit · JWT verify") có API Gateway.
- `system-architecture.md` §6 Ingress chỉ có LB L4 (MQTT) + LB L7 + WAAP (Web/API) — không nhắc API Gateway.
- Cần chốt: có dùng API Gateway không (VNPT managed hay tự dựng), hay LB L7 + service tự verify JWT là đủ → cập nhật cả 3 tài liệu về 1 phương án.

### C-07 · OTA: sơ đồ thể hiện như luồng hiện hữu, kiến trúc lại defer — **Medium**

- Overall diagram: downlink "config · **OTA ring rollout** · remote command"; on-prem diagram: "Device Config Agent — nhận config/**OTA** từ cloud".
- `system-architecture.md`: cập nhật edge qua **Ansible-pull** (không phải MQTT OTA); brainstorm §12-R4: Device Registry "làm **trước khi nghĩ tới OTA**" (OTA defer).
- 2 vấn đề: (a) kênh cập nhật trên sơ đồ (MQTT downlink) khác thiết kế (Ansible-pull qua HTTPS/Git); (b) OTA gateway firmware chưa được thiết kế nhưng sơ đồ vẽ như đã có. Cần chú thích "(future)" trên sơ đồ hoặc bỏ nhãn OTA.

### C-08 · Device Registry / Fleet Management: sơ đồ cloud vẽ như core service ngay từ đầu — **Medium**

- Cloud diagram đặt "Device Registry · Fleet Management" trong Core Services; roadmap đưa Device Registry v1.0 vào **tháng 12–18 (Phase C)**. Sơ đồ nên ghi chú phase hoặc roadmap nên kéo sớm hơn (Temporal onboarding Phase B đã cần registry tối thiểu để cấp cert/ACL).

### C-09 · Điều khiển ngược: tài liệu tham chiếu vượt whitelist — **Medium** (reference-only)

- TechStack_Pipeline giai đoạn 1/4: "điều khiển dữ liệu điện **từng khách hàng**", "điều khiển nước thải/sinh hoạt", "điều khiển **bơm**", voice2action.
- Whitelist chính thức (Technical Report §2.2, system-architecture §8, Quy chế §4.4): **chỉ 9 lộ chiếu sáng + PTZ camera**; mở rộng qua Change Request.
- Whitelist là authoritative. Cần đánh dấu rõ trong TechStack_Pipeline (hoặc README) rằng phạm vi điều khiển của nó không còn hiệu lực — tránh đội dev đọc tài liệu tham chiếu và implement vượt whitelist (rủi ro an toàn OT).

### C-10 · Roadmap G1 exit vs DR runbook timing — **Medium**

- Roadmap Gate G1 (Phase A) yêu cầu "DR drill runbook v0.1" nhưng warm standby region 2 + DR drill nằm ở Phase B. Runbook v0.1 Phase A viết dựa trên gì? Chấp nhận được nếu là runbook nháp lý thuyết — nên ghi rõ.

### C-11 · description.md còn phản ánh trạng thái tiền-quyết-định — **Medium**

- Nhắc "API Gateway" (C-06), "Digital Twin" như chức năng cloud, không nhắc EMQX/D1–D7. Là tài liệu "Đã duyệt" nhưng nội dung generic hơn system-architecture → cần cập nhật hoặc đánh dấu "tổng quan, chi tiết theo system-architecture.md".

---

## 4. Không nhất quán mức Low

| ID | Nội dung | Chi tiết |
|---|---|---|
| C-12 | CLAUDE.md ghi "4 server Dell" | Thực tế 3 Dell (2× R660xs + 1× R760xs) + 1 HPE DL380 — **Low** |
| C-13 | Roadmap nhắc "Phase D (scale to 100+)" 1 lần, không định nghĩa ở đâu | Phases chỉ có A/B/C — **Low** |
| C-14 | TechStack_Pipeline nội bộ mâu thuẫn: bảng ghi Mobile "React Native", lý do lại nói "Flutter"; media server bảng ghi "MediaMTX", giai đoạn 2 ghi "ZLMediaKit" | Reference doc — đã bị D2 supersede một phần; đánh dấu superseded — **Low** |
| C-15 | Lỗi chính tả/garbled trong docs chính thức: PDR "múi khu công nghiệp", "nhiệt độ tựa sưởi", "đang +dùng POC"; roadmap "Dr drill" | Giảm tin cậy spec — **Low** |
| C-16 | README sơ đồ tài liệu ghi "Brainstorm Report (7 quyết định...)" | Brainstorm chốt 3, hợp nhất thành 7 ở system-architecture — nhãn không chính xác — **Low** |
| C-17 | PDR ràng buộc #7 gộp "gates G0-G6" vào roadmap A/B/C | Kế thừa nhầm lẫn C-01 — **Low** (sửa cùng C-01) |
| C-18 | Frontend stack: roadmap giai đoạn 4 ghi "React"; TechStack ghi Bootstrap + Mapbox; D2 không có frontend | Chưa có quyết định frontend chính thức — xem gap G-14 — **Low** (ở đây), **Medium** (ở gap) |

---

## 5. Các điểm ĐÃ nhất quán tốt

Ghi nhận để tránh sửa nhầm những chỗ đang đúng:

| Chủ đề | Các tài liệu khớp nhau |
|---|---|
| D7 Docker Compose on-prem, KHÔNG K8s/K3s tại site | system-architecture, PDR, README, CLAUDE.md, cả 3 diagram (on-prem diagram ghi rõ 2 lần + legend) — nhất quán tuyệt đối |
| Topic standard `v1/{tenant}/{park}/{subsys}/{node}/...` + cert CN `{tenant}:{park}:{gw}` | system-architecture §8, PDR §7, brainstorm §7 |
| KPI: telemetry ≤5s, event/alarm ≤2s, command ack ≤5s, gateway ≥99.5% | Quy chế §10, system-architecture, PDR NFR, diagrams |
| QoS strategy (QoS1 + dedup, app-level ack, không QoS2) | system-architecture §8, PDR §7, brainstorm §7 |
| Bản tin bắt buộc (NTP, gateway ID, sequence, cờ truyền bù, cờ chất lượng; scale 1 lần tại gateway) | Quy chế §4.2, Technical Report, system-architecture, PDR |
| Retention: raw 30d / aggregate 1y / logs 90d / metrics 13mo / audit 2y / footage local 30d | system-architecture §7 §9, PDR, Technical Report §7.4 (≥12 tháng vận hành — được cover bởi aggregate 1y + TSDB edge ≥12mo) |
| DMZ Z3.5 + zone Purdue + camera VLAN không Internet + mgmt VLAN qua bastion | system-architecture §5, on-prem diagram, brainstorm §4 |
| Warm standby region 2, RPO 5–15ph, RTO 1–2h, immutable backup, DR drill quý | system-architecture §11, README, diagrams, brainstorm §10 |
| Whitelist điều khiển ngược 9 lộ + PTZ, 2FA TOTP, audit | Technical Report, Quy chế, system-architecture, PDR, cả 3 diagram (legend mũi tên đỏ) |
| Tủ 4G VPN về FortiGate site, không nối thẳng cloud | system-architecture §4, on-prem diagram, brainstorm §3 |
| VKS ~6 worker / EMQX×3 / Kafka RF3 / CH 2 replica + 3 Keeper / PG managed HA | system-architecture §6–7, cloud diagram, roadmap tháng 1–2 |

**Kết luận:** phần lõi kiến trúc (quyết định, nguyên tắc, thông số giao thức, KPI, deployment model) nhất quán tốt — chứng tỏ quy trình brainstorm → architecture → diagram làm việc hiệu quả. Không nhất quán tập trung ở: (1) tài liệu quy trình (gates, 5 giai đoạn), (2) PDR số liệu, (3) tài liệu tham chiếu chưa đánh dấu phần bị thay thế.
