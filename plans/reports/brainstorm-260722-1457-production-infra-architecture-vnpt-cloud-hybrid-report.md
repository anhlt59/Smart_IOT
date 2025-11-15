# Brainstorm Report — Production Infrastructure Architecture (VNPT Cloud + Edge/On-Premise)

**Date:** 2026-07-22 · **Type:** brainstorm (Principal Infra/Cloud/IIoT/Network Architect)
**Scope đã chốt với user:**
- Edge/On-Premise: **cố định hoàn toàn** theo mẫu KCN Đồng Văn III (Technical Report Rev 1.1) — brainstorm tập trung Cloud + Hybrid Connectivity.
- Tech stack đích: **EMQX, Kafka, ClickHouse, Keycloak, Temporal** (theo TechStack_Pipeline).
- Scale: thiết kế cho **10–30 KCN**, không khóa đường lên 100+; mốc 1000 chỉ ở mức nguyên tắc.
- Đầu ra: report này (plans/reports/), convert sang `docs/system-architecture.md` sau khi chốt.

**Trạng thái 3 quyết định kiến trúc — ✅ USER ĐÃ XÁC NHẬN TOÀN BỘ (2026-07-22):**
1. Connectivity: VNPT MPLS/L3VPN primary + Internet IPsec backup.
2. DR: Warm standby tối giản ở region 2 (RPO 5–15 phút, RTO 1–2h).
3. Tenancy: Shared cluster + namespace/RLS, thiết kế sẵn cell-ID cho scale 100+.

**Nguồn:** `docs/description.md`, `docs/POC_architecture.md`, `docs/TechStack_Pipeline.docx.md`, `docs/Industrial_Park_Technical_Report.pdf`, `docs/IoT_Software_Team_Collaboration_Guidelines.pdf`. Thông tin ngoài tài liệu được đánh dấu `[assumption]` hoặc `[verified-web]`.

---

## 0. Bối cảnh tổng hợp

- Mô hình hybrid: On-Prem platform tại từng KCN (tự trị khi mất Internet, store & forward 30 ngày tại gateway) + Cloud platform trên VNPT Cloud quản lý tập trung đa KCN, multi-tenant (tenant = chủ đầu tư, sở hữu ≥1 KCN).
- Site mẫu (ĐV3): 5 lớp, gateway Advantech ECU-1051 (Modbus⇄MQTT, SD buffer 30d), FortiGate 80F, VLAN IT/OT, 4G VPN cho tủ phân tán, server room 4 máy chủ (2×R660xs app, 1×R760xs data, 1×DL380 GPU 48GB AI), NVR local, OT read-only, chỉ 2 đối tượng điều khiển ngược (9 lộ chiếu sáng + PTZ).
- Ranh giới trách nhiệm 2 đội tại MQTT Broker; KPI telemetry ≤5s end-to-end, gateway availability ≥99.5%; môi trường DEV/STG/PROD bắt buộc.
- VNPT Cloud `[verified-web]`: có VKS (managed K8s), DBaaS (PostgreSQL/MySQL/MongoDB/Redis), Message Streaming (Kafka), Object Storage, Backup; VNPT IDC 8 DC, 6 Tier III (HN: Nam Thăng Long, Hòa Lạc; Đà Nẵng; HCM) → DR đa region khả thi. **ClickHouse, EMQX, Keycloak, Temporal KHÔNG có managed → tự vận hành trên VKS.**

---

## 1. Edge / On-Premise Architecture

**Current Design:** Theo ĐV3 (cố định): kiến trúc 5 lớp; 9 tủ IoT hiện trường + ECU-1051 buffer 30 ngày; ADAM-3600 quan trắc (TT 10/2021, ISO 27001); Edge AI Box Jetson Orin (khói/lửa); server room chạy nền tảng IOC on-prem (dashboard, VMS, rule engine, TSDB ≥12 tháng); POC bổ sung stack Docker Compose 10 services (Mosquitto, PG, TimescaleDB, Redis, Go app, AI, cloud-sync, Nginx, Telegraf, Watchtower).

**Gaps / Risks:**
- G1. Server room = 1 phòng duy nhất, không HA ở tầng software: docs không định nghĩa app services chạy HA trên 2×R660xs hay active/passive; mất 1 server → chưa rõ hành vi.
- G2. **Watchtower auto-update (POC) trong môi trường OT = rủi ro cao**: tự pull image mới bất kỳ lúc nào, mâu thuẫn trực tiếp quy trình release có kiểm soát của Collaboration Guidelines (release theo checklist, freeze trước nghiệm thu).
- G3. Credentials plaintext trong `.env` (POC: `DB_PASSWORD=Str0ng_P@ssw0rd_ChangeMe!`).
- G4. Config drift giữa 10–30 site: chưa có cơ chế quản lý cấu hình site tập trung, as-built chỉ là file export thủ công.
- G5. POC edge stack (Mosquitto/TimescaleDB) khác stack đích (EMQX/ClickHouse) → 2 hệ tri thức vận hành song song.
- G6. Không có out-of-band management (iDRAC/iLO có sẵn trên Dell/HPE nhưng docs không quy hoạch truy cập).
- G7. NTP: bản tin bắt buộc đồng bộ NTP (Interface Agreement) nhưng chưa quy hoạch NTP server local khi mất Internet.

**Recommendations** (chỉ software/ops — hardware giữ nguyên):
- R1. Chuẩn hóa **Site Blueprint** dạng code: 1 repo Git `site-blueprint` chứa compose/K3s manifests + config template; mỗi site 1 nhánh/thư mục as-built có version. Deploy site mới = instantiate blueprint (đáp ứng mục tiêu nhân bản 10–30 KCN).
- R2. Chạy app layer trên K3s 3 node (2×R660xs + R760xs, taint node data) HOẶC giữ Docker Compose + keepalived VIP giữa 2 R660xs cho stateless services. Đề xuất **K3s** vì TechStack_Pipeline đã định hướng "K3s cho quy mô vừa" và thống nhất được cơ chế GitOps với cloud. KISS: nếu đội vận hành site yếu K8s → giữ Compose + VIP, chấp nhận failover thủ công (edge tự trị nên chấp nhận được).
- R3. **Bỏ Watchtower.** Thay bằng GitOps pull agent (Argo CD agent/Fleet trên K3s, hoặc Ansible-pull theo lịch nếu Compose), version pin, rollout theo ring: site lab → 1 site canary → toàn fleet.
- R4. Edge broker: dùng **EMQX (open-source) tại edge** thay Mosquitto để đồng nhất stack + có sẵn bridge lên cloud, ACL, mTLS. TSDB edge: giữ TimescaleDB nếu IOC on-prem ĐV3 đã build trên nó (đã ký hợp đồng); site mới theo blueprint dùng 1 chuẩn duy nhất.
- R5. NTP: chrony local trên server room (stratum từ GPS/4G khi mất WAN); iDRAC/iLO vào VLAN mgmt riêng, chỉ truy cập qua tunnel quản trị.

**Alternative:** Không có (hardware cố định). **Trade-offs:** K3s tăng learning curve đội site nhưng thống nhất toolchain; Compose+VIP đơn giản nhưng thao tác failover/rollout thủ công nhân với 30 site = gánh nặng vận hành tăng tuyến tính.

**Priority: HIGH** (R3 bỏ Watchtower + R1 blueprint là tiền đề scale).

---

## 2. Cloud Architecture (VNPT Cloud)

**Current Design:** description.md: VKS + API Gateway + LB + WAAP + Managed PG/Redis/Kafka + Object Storage + Backup; microservices Go, multi-tenant, HA, horizontal scaling. POC: manifests tự host PG/ClickHouse/Redis/MQTT trong cluster, namespace per tenant, HPA cho processing service, ước tính 12 cores/38GB RAM/650GB — cho 1 KCN.

**Gaps / Risks:**
- G1. POC **tự host DB trong VKS bằng Deployment (không StatefulSet cho PG), Redis replicas=1** — mâu thuẫn định hướng managed, không production-grade.
- G2. Chưa có thiết kế VPC/subnet/AZ; chưa rõ VNPT Cloud region có multi-AZ trong 1 region hay không `[cần verify với VNPT]`.
- G3. Chưa có node pool strategy; DB time-series cần NVMe (chính docs yêu cầu) nhưng chưa quy hoạch pool riêng.
- G4. DEV/STG/PROD bắt buộc (Collab Guidelines) nhưng chưa có thiết kế tách môi trường ở tầng hạ tầng.
- G5. WAAP đặt trước cả MQTT? — WAAP là L7 HTTP, không áp dụng cho MQTT/TCP; docs chưa phân biệt.

**Recommendations:**
- R1. **Landing zone:** 1 VPC/environment (prod, staging, dev — dev/stg có thể chung 1 VPC tách subnet để tiết kiệm). Prod VPC subnets: `edge-ingest` (LB MQTT/VPN), `app` (VKS worker app), `data` (VKS worker DB + managed DB endpoints), `mgmt` (bastion, CI runner, monitoring). Security group deny-by-default.
- R2. **VKS prod:** 3 node pools tối thiểu — `app-pool` (Go microservices, API, Keycloak, Temporal, Grafana...), `data-pool` (NVMe/SSD cao IOPS: ClickHouse, EMQX, Loki/Mimir), `ingest-pool` (EMQX + Kafka consumers, tách để burst không ảnh hưởng app). GPU pool: **chưa cần** — AI inference đã ở edge (Jetson + DL380 on-prem); thêm sau nếu có nhu cầu train tập trung.
- R3. **Managed-first:** PostgreSQL (HA), Redis, Kafka dùng dịch vụ managed VNPT; ClickHouse + EMQX + Keycloak + Temporal self-host trên VKS (không có managed). Nguyên tắc: cái gì stateful và có managed → dùng managed; còn lại Operator trên VKS (CloudNativePG chỉ khi managed PG không đạt yêu cầu; ClickHouse dùng Altinity operator; EMQX operator).
- R4. Ingress: VNPT LB (L4) cho MQTT :8883 (mTLS) và VPN; VNPT LB + WAAP (L7) chỉ cho Web/API/HTTPS public. API nội bộ site→cloud đi qua tunnel riêng không qua WAAP.
- R5. Registry: VNPT Container Registry cho prod images; GitLab registry cho dev.

**Alternative:** toàn bộ self-host trên VServer (IaaS thuần) — kiểm soát tối đa, nhưng đội DevOps phải vận hành PG/Kafka HA thủ công; chỉ chọn nếu managed SLA/phiên bản không đạt. **Trade-offs:** managed giảm ops nhưng lock phiên bản/extension (PG cần verify hỗ trợ PostGIS — POC dùng PostGIS!).

**Priority: HIGH.**

---

## 3. Hybrid Connectivity (On-Premise ↔ Cloud)

**Current Design:** description.md: "VPN / TLS / MQTT" (generic). POC: cloud-sync service + script bash sync 60s/lần qua HTTPS API; tủ IoT phân tán 4G VPN về FortiGate site. Collab Guidelines: gateway trỏ STG/PROD qua kênh VPN do đội Phần mềm cấp.

**Gaps / Risks:**
- G1. Chưa chốt underlay (Internet? kênh riêng?); chưa có băng thông ước tính (telemetry nhỏ, nhưng event AI kèm ảnh + on-demand video stream đáng kể).
- G2. Sync bằng bash script + cron là POC-grade: không backpressure, không idempotency, khó quan sát.
- G3. Không có thiết kế failover endpoint (DNS, IP tĩnh, health check) khi cloud region fail.
- G4. Mô hình kết nối cho tủ 4G: hiện VPN về site; nếu về thẳng cloud sẽ phá ranh giới nghiệm thu tại broker site.

**Recommendations** (✅ user đã xác nhận phương án R1 ngày 2026-07-22):
- R1. **Underlay 2 lớp:** VNPT MPLS/L3VPN (site ↔ VNPT Cloud private peering) làm primary — tận dụng VNPT vừa là ISP vừa là cloud, SLA telco, QoS cho lưu lượng điều khiển; Internet FTTH + IPsec (FortiGate → cloud VPN GW) làm backup, SD-WAN rule trên FortiGate tự failover. Site nhỏ/pilot có thể bắt đầu Internet-only rồi nâng cấp.
- R2. **Data plane chuẩn hóa = MQTT bridge:** EMQX edge bridge → EMQX cloud qua tunnel, mTLS per-site cert, topic namespace `{tenant}/{park}/...`. Thay bash sync bằng bridge + backfill flag (Interface Agreement đã quy định cờ truyền bù + sequence number). File lớn (ảnh sự kiện, clip): upload trực tiếp Object Storage qua pre-signed URL, chỉ metadata đi MQTT.
- G3 fix: 2 FQDN (`mqtt.{env}.domain`, `api.{env}.domain`) TTL thấp, health-checked, trỏ region DR khi failover.
- R3. Tủ 4G giữ nguyên mô hình về site (đúng ranh giới nghiệm thu); KHÔNG cho gateway 4G nối thẳng cloud.
- R4. Băng thông tham chiếu/site `[assumption]`: telemetry+heartbeat <1 Mbps; event kèm ảnh ~5 Mbps burst; xem video on-demand 2–8 Mbps/stream → MPLS 20–50 Mbps/site đủ, Internet backup ≥100 Mbps (FTTH phổ thông).

**Alternative:** SD-WAN full-mesh đa đường (FTTH + 4G/5G + MPLS) — linh hoạt nhất, phức tạp vận hành; Internet-only IPsec — rẻ nhất, chấp nhận mất giám sát tập trung khi ISP sự cố (edge vẫn tự trị). **Trade-offs:** MPLS thêm chi phí ~vài triệu VNĐ/site/tháng nhưng loại rủi ro jitter cho video + điều khiển ngược; Internet-only đẩy rủi ro sang vận hành.

**Priority: HIGH.**

---

## 4. Network Segmentation (IT/OT/DMZ)

**Current Design:** Site ĐV3: VLAN tách OT (tủ IoT/PLC) / camera / server / văn phòng; FortiGate 80F biên; least-privilege giữa vùng; OT read-only; MQTT TLS; 4G về firewall qua VPN.

**Gaps / Risks:**
- G1. Chưa formalize theo Purdue/IEC 62443 (zones & conduits); chưa có **DMZ site** — service cloud-sync/bridge hiện đứng chung server room, nghĩa là vùng chứa dữ liệu OT nói chuyện trực tiếp Internet.
- G2. Cloud-side segmentation chưa thiết kế (POC chỉ có namespace).
- G3. Chưa có chính sách egress: server room/camera VLAN có được ra Internet tự do không? (Watchtower POC cần egress tự do — thêm lý do bỏ).
- G4. NetworkPolicy giữa namespace tenant trên VKS chưa định nghĩa (checklist POC có nhắc nhưng không có spec).

**Recommendations:**
- R1. Site zoning chuẩn hóa (ánh xạ Purdue): Z0–2 = VLAN OT (PLC, tủ IoT, datalogger); Z3 = VLAN vận hành site (server room: IOC, broker edge, TSDB); **Z3.5 = DMZ site (VLAN mới trên FortiGate — chỉ chứa MQTT bridge + reverse proxy + sync)**; Z4 = VLAN IT văn phòng; camera VLAN riêng không route Internet. Conduits: OT→Z3 chỉ MQTT/Modbus-đọc; Z3→cloud CHỈ qua DMZ; deny-by-default; egress whitelist theo FQDN (registry, cloud endpoints, NTP).
- R2. Cloud zoning: subnet như mục 2-R1 + VKS NetworkPolicy: default-deny per namespace, tenant namespace không nói chuyện chéo, data services chỉ nhận từ app/ingest namespaces.
- R3. Admin plane tách riêng: bastion trong `mgmt`, truy cập site (iDRAC, FortiGate mgmt) chỉ từ mgmt qua tunnel.

**Alternative:** micro-segmentation đầy đủ (per-workload) bằng Cilium — hoãn, YAGNI ở quy mô này. **Trade-offs:** DMZ site thêm 1 VLAN + rule phức tạp hơn chút trên FortiGate 80F (hoàn toàn trong năng lực thiết bị), đổi lại cô lập được OT khỏi Internet đúng chuẩn IIoT.

**Priority: HIGH** (DMZ site + egress whitelist là thay đổi cấu hình, không thay đổi phần cứng — hợp lệ với ràng buộc "cố định").

---

## 5. High Availability (Cloud Platform)

**Current Design:** POC: SLO uptime 99.9%/SLA 99.5%; PG streaming replication failover <30s; ClickHouse ReplicatedMergeTree failover <1 phút; HPA cho microservices; replicas=3 cho processing.

**Gaps / Risks:**
- G1. Manifests POC không khớp mục tiêu: PG là Deployment đơn, Redis 1 replica, Mosquitto đơn node.
- G2. EMQX/Kafka HA chưa thiết kế; mất broker cloud = mất ingest toàn bộ KCN (dù edge buffer cứu dữ liệu, mất realtime).
- G3. Multi-AZ chưa xác nhận trên VNPT Cloud; anti-affinity/PDB chưa có.
- G4. SLO 99.9% chưa gắn error budget với thành phần cụ thể.

**Recommendations:**
- R1. Tier hóa HA: **Tier-0 (ingest path — EMQX, Kafka, LB):** EMQX cluster ≥3 node trải AZ (nếu có AZ) + LB L4; Kafka managed 3 broker RF=3. **Tier-1 (data):** PG managed HA (sync standby), ClickHouse 2 replica + 3 ClickHouse Keeper, Redis managed replica. **Tier-2 (app):** replicas ≥2 + PDB + topology spread. Mất Tier-2 vài phút chấp nhận được; Tier-0 phải sống vì realtime alarm.
- R2. Nếu VNPT region không có multi-AZ: chấp nhận single-AZ + warm standby region 2 gánh vai trò DR (mục 10), ghi rõ trong SLA khách hàng.
- R3. Định kỳ chaos test nhẹ (kill pod broker, drain node) trên STG mỗi quý.

**Alternative:** stretch cluster 2 region — không khuyến nghị (latency liên region, phức tạp Keeper/quorum). **Trade-offs:** EMQX 3 node + CH 2 replica tăng ~40–60% chi phí data plane so POC đơn node — bắt buộc cho production đa KCN.

**Priority: HIGH.**

---

## 6. Compute, Storage, Database, Cache, Message Broker

**Current Design:** POC cho 1 KCN: PG 100GB (metadata/config/audit, PostGIS, RLS), ClickHouse 500GB (time-series TTL 30 ngày raw + 1 năm aggregate), Redis 20GB, MQTT 10GB; ~12 cores/38GB. TechStack đích thêm: Kafka, MinIO/HDFS, Spark/Flink, Trino, Atlas/Airflow. Retention policy + alerting thresholds + SLO đã có bảng chi tiết (POC).

**Gaps / Risks:**
- G1. Mâu thuẫn TSDB (TimescaleDB/ClickHouse/TDengine) — đã chốt ClickHouse theo stack đích.
- G2. **BigData stack (HDFS/Spark/Flink/Trino/Atlas/Airflow) là over-engineering ở 10–30 KCN** — chưa có use case vượt khả năng ClickHouse + Kafka; MinIO thừa khi có VNPT Object Storage.
- G3. Sizing chỉ có cho 1 KCN; chưa có capacity model cho 10–30.
- G4. Kafka topic/partition strategy, schema versioning chưa thiết kế.

**Recommendations:**
- R1. **Canonical pipeline duy nhất:** `EMQX (cloud) → Kafka (managed) → Go ingest/normalize/validate → ClickHouse (telemetry, events) + PG (metadata, alarm lifecycle, audit) + Redis (last-value cache, session)`. Alarm path tách consumer riêng để độ trễ ≤2s không bị ảnh hưởng bulk ingest.
- R2. **Defer:** Spark/Flink/Trino/HDFS/Atlas/Airflow — chỉ đưa vào khi có yêu cầu phân tích thực tế vượt ClickHouse (materialized views đủ cho báo cáo/aggregate hiện tại). MinIO bỏ, dùng VNPT Object Storage. (YAGNI, đúng tinh thần "scale-up path" chính POC đã viết.)
- R3. Capacity model `[assumption — cần đo thực tế ĐV3]`: mỗi KCN ~500–1.500 tag hoạt động, chu kỳ 1s–5phút → 50–200 msg/s/site đỉnh; 30 KCN ≈ 2.000–6.000 msg/s — nhẹ với EMQX 3 node + Kafka 3 broker. ClickHouse: ~5–15 GB/ngày raw toàn fleet (nén ~10x) → 30 ngày raw ≈ 150–450GB + aggregate 1 năm ≈ 200–500GB → data-pool 2 node NVMe 2TB khởi điểm. Kafka retention 3–7 ngày (replay window cho consumer lỗi).
- R4. Kafka topics theo domain không theo tenant: `telemetry.raw`, `events.alarm`, `commands.audit`... partition key = `{tenant}/{park}` (giữ ordering per site, tránh topic explosion khi 100+ KCN); schema JSON + JSON Schema registry trong Git (Interface Agreement đã là contract-first — số hóa nó).
- R5. Compute khởi điểm prod (10 KCN đầu) `[assumption]`: VKS ~6 worker (4×8vCPU/16GB app+ingest, 2×8vCPU/32GB NVMe data) + managed PG (2×4vCPU/16GB HA) + managed Kafka 3 broker + managed Redis 4GB — ước tính thô 40–70 triệu VNĐ/tháng chưa gồm MPLS + Object Storage; đối chiếu con số POC 15–20tr/1 KCN → shared platform rẻ hơn nhiều per-site.

**Alternative:** TimescaleDB thay ClickHouse (đồng nhất PG toolchain, dùng managed PG được) — hợp lý nếu đội mỏng, nhưng kém hơn về nén + tốc độ aggregate ở fleet lớn, và trái stack đích user đã chốt. **Trade-offs:** ClickHouse self-host = thêm ops (operator, backup, upgrade) đổi lấy hiệu năng time-series + đúng định hướng audit stream (Kafka→ClickHouse).

**Priority: HIGH** (R1/R2); Medium (R3–R5 tinh chỉnh theo số liệu thật).

---

## 7. IoT Communication (MQTT, OPC-UA, Modbus, BACnet…)

**Current Design:** Field: Modbus RTU/TCP (chuẩn hóa tại ECU-1051 — hỗ trợ sẵn OPC UA client/server, DNP3, BACnet/IP), 4–20mA/DI qua datalogger; EVN REST API; video RTSP/ONVIF tách luồng telemetry, NVR local 30 ngày; uplink MQTT TLS; bản tin bắt buộc: NTP timestamp, gateway ID, sequence number, cờ truyền bù, cờ chất lượng; QoS2 cho khẩn cấp (POC); kênh tách telemetry/event/heartbeat/command; heartbeat 3 chu kỳ → cảnh báo mất kết nối; payload ký SHA-256+RSA (POC đặt tại PLC).

**Gaps / Risks:**
- G1. Topic namespace chưa chuẩn hóa cross-site/tenant (Interface Agreement để 2 đội tự ban hành per-project → nguy cơ mỗi KCN một kiểu).
- G2. Ký số payload **tại PLC** (POC) không thực tế (PLC S7-1200 không phù hợp RSA + quản lý private key); mâu thuẫn với chính mô tả gateway-centric của ĐV3.
- G3. QoS strategy chưa nhất quán (QoS2 everywhere giết throughput).
- G4. Command (điều khiển ngược) qua cloud chưa có spec idempotency/timeout/2-man rule — TechStack yêu cầu 2FA/PIN cho reverse control.
- G5. Video lên cloud chưa có chính sách băng thông (nguyên tắc đã có: footage ở local, "sau 5h gửi về trung tâm" — mơ hồ).

**Recommendations:**
- R1. **Topic standard toàn nền tảng** (đưa vào Interface Agreement template): `v1/{tenant}/{park}/{subsys}/{node}/telemetry|event|heartbeat` uplink; `v1/{tenant}/{park}/{subsys}/{node}/cmd` + `.../cmd/ack` downlink. EMQX ACL: cert CN = `{tenant}:{park}:{gateway}` → chỉ pub/sub đúng prefix.
- R2. Chốt: **chữ ký/mTLS tại gateway** (ECU-1051 giữ private key, TLS mutual với broker); PLC chỉ làm ngưỡng cục bộ + fail-safe như quy định pháp lý. Range check + schema validation làm 2 lớp: gateway + ingest service.
- R3. QoS: telemetry QoS1, event/alarm QoS1 + dedup theo sequence, command QoS1 + ack ứng dụng (không dựa QoS2 MQTT; idempotency key + timeout 5s theo KPI phản hồi ≤5s của Collab doc).
- R4. Command qua cloud: chain `Cloud API (2FA + RBAC + audit) → Kafka commands → cloud EMQX → bridge → edge EMQX → gateway`; danh mục điều khiển whitelist đúng như site (chiếu sáng, PTZ); mở rộng qua Change Request.
- R5. Video: mặc định chỉ metadata + snapshot sự kiện lên cloud (Object Storage); live view từ xa qua relay WebRTC (MediaMTX trong DMZ site) theo yêu cầu, giới hạn concurrent streams/site.
- R6. OPC UA: bật ở gateway cho PLC nào hỗ trợ (data model tốt hơn) — tùy site, không bắt buộc retrofit.

**Alternative:** MQTT Sparkplug B (birth/death certificates, state management chuẩn công nghiệp) — cân nhắc cho site mới từ KCN thứ 2+ nếu đội chấp nhận payload binary (mất tính human-readable của JSON hiện tại; ECU-1051 hỗ trợ Azure/AWS profile, cần verify Sparkplug). **Trade-offs:** JSON dễ debug + đã có Interface Agreement; Sparkplug chuẩn hơn nhưng đổi contract giữa chừng vi phạm quy trình CR nặng.

**Priority: HIGH** (R1/R2/R4 — an toàn điều khiển ngược); Medium (R5/R6).

---

## 8. Monitoring, Logging, Observability

**Current Design:** Prometheus + Grafana (TechStack + POC); edge có Telegraf + Grafana Agent; system logs 90 ngày (Loki/ELK); bảng ngưỡng cảnh báo hạ tầng chi tiết (CPU/RAM/disk/MQTT queue/API latency/sync lag); SLO đo bằng Prometheus histogram; VNPT Cloud Monitoring nhắc đến như kỹ năng.

**Gaps / Risks:**
- G1. Không có thiết kế **fleet observability tập trung** — 30 site × metrics/logs cần long-term store + multi-tenancy, Prometheus đơn không đủ.
- G2. Thiếu tracing (microservices Go + pipeline Kafka → khó truy độ trễ ≤5s end-to-end nếu không có trace).
- G3. Alert routing/on-call tooling chưa chọn (bảng SLA P1–P4 + on-call đã có ở mức quy trình).
- G4. Giám sát "sức khỏe kết nối site" (bridge lag, buffer depth gateway, sync backlog) chưa là first-class metric.

**Recommendations:**
- R1. Cloud: **LGTM stack trên VKS** — Grafana + Mimir (metrics long-term, multi-tenant) + Loki (logs) + Alertmanager; giữ đúng lựa chọn Grafana Agent tại edge, remote_write qua tunnel với external labels `{tenant, park, site}`. Retention: metrics 13 tháng (khớp yêu cầu lưu ≥12 tháng), logs 90 ngày (đúng policy POC).
- R2. OpenTelemetry SDK trong Go services; trace tối thiểu: ingest → Kafka → consumer → DB; đo KPI telemetry ≤5s bằng synthetic probe mỗi site (publish tag test → đo tới dashboard).
- R3. Fleet dashboard chuẩn: trạng thái tunnel (primary/backup), bridge queue, gateway heartbeat (đã có ở tầng app), backfill backlog, cert expiry. Đây là màn hình NOC trung tâm — khác dashboard nghiệp vụ IOC.
- R4. Alert routing: Alertmanager → Telegram + email (kênh đã chốt trong docs) + escalation theo bảng P1–P4; on-call schedule bằng Grafana OnCall (self-host, free) thay vì quy trình giấy.

**Alternative:** VNPT Cloud Monitoring cho hạ tầng cloud + tự host phần fleet — giảm ops một phần nhưng phân mảnh 2 hệ thống; ELK thay Loki — nặng ops hơn, chỉ khi cần full-text search mạnh. **Trade-offs:** LGTM self-host thêm ~2 node data-pool nhưng là xương sống vận hành 30 site.

**Priority: HIGH.**

---

## 9. Security (IAM, PKI, VPN, Firewall, Zero Trust)

**Current Design:** Keycloak + JWT, 2FA TOTP + dynamic QR (stack đích; POC dùng JWT tự build, middleware sẵn sàng plug Keycloak); per-gateway credential/cert do đội Phần mềm cấp, cấm dùng chung, thu hồi khi thay thiết bị; MQTT TLS; FortiGate NGFW + VPN; RBAC 3 nhóm + audit log; encryption at rest PG/CH; VNPT-CA ký số tài liệu; certificate rotation "nhắc đến như chủ đề"; VNPT IAM/STS cho tài khoản chủ đầu tư.

**Gaps / Risks:**
- G1. **Không có PKI lifecycle design** — ai phát hành cert gateway, CA nào, rotation/revocation thế nào ở 30 site × ~10 gateway/site? Đây là gap an ninh lớn nhất.
- G2. Secrets plaintext (.env POC), chưa có secrets manager; CI/CD secrets chưa quy hoạch.
- G3. Quản trị từ xa: SSL-VPN FortiGate per-site → 30 site = 30 cấu hình rời rạc, chưa có central access control + session audit.
- G4. Chưa có image/dependency scanning, patch policy cloud; PDPD (NĐ 13/2023) — camera footage/biển số = dữ liệu cá nhân, chưa có chính sách xử lý; điểm cộng: dữ liệu nằm VNPT Cloud VN = data residency ổn.
- G5. Keycloak multi-tenant model chưa thiết kế (realm per tenant? groups?).

**Recommendations:**
- R1. **Private PKI 2 tầng:** offline root CA + intermediate per môi trường, vận hành bằng **Vault PKI (self-host VKS) hoặc step-ca**. Device identity: mỗi gateway 1 cert (CN=`{tenant}:{park}:{gw}`), hạn 1 năm, tự động rotate qua EST/SCEP hoặc script Ansible site (ECU-1051 quản lý qua EdgeLink — cần verify khả năng nạp cert tự động; fallback: rotation theo kỳ bảo trì 6 tháng). CRL/OCSP tại EMQX để revoke tức thời.
- R2. **Vault (hoặc tối thiểu SOPS+age trong Git)** cho toàn bộ secrets; External Secrets Operator bơm vào VKS; cấm secrets trong .env/manifest. DB credentials dynamic (Vault database engine) — phase 2.
- R3. IAM: **Keycloak 1 realm platform, organization/group per tenant** (đơn giản hơn realm-per-tenant khi 10–30 tenant, vẫn tách được khi cần); OIDC SSO cho: platform web, Grafana, GitLab, Temporal UI; 2FA TOTP bắt buộc role điều khiển ngược (đúng yêu cầu TechStack); service-to-service bằng client credentials + mTLS nội cluster (phase sau: mesh).
- R4. Admin access: bastion + ZTNA (FortiClient ZTNA tận dụng hệ Fortinet sẵn có, hoặc WireGuard + SSO) → mọi phiên quản trị site/cloud đều qua 1 cửa, log tập trung. Không mở SSH/mgmt từ Internet.
- R5. Chuỗi CI: Trivy scan image + dependency; chính sách vá: critical CVE ≤7 ngày (cloud), edge theo ring rollout.
- R6. PDPD: chính sách retention footage (đã có 30 ngày local, 6 tháng object storage cho vi phạm), masking biển số trên dashboard public, DPA với chủ đầu tư — đưa vào hợp đồng tenant.
- Zero Trust: lộ trình — năm 1 dừng ở device mTLS + ZTNA admin + deny-by-default network; chưa cần service mesh.

**Alternative:** dùng hoàn toàn VNPT IAM + VNPT CA thay Keycloak/private PKI — giảm ops nhưng lock-in + khó tùy biến RBAC nghiệp vụ đa tenant; giữ VNPT-CA đúng vai trò ký số văn bản pháp lý (như docs), private PKI cho machine identity. **Trade-offs:** Vault thêm 1 hệ stateful phải HA; đổi lại giải quyết G1+G2 cùng lúc.

**Priority: HIGH (cao nhất trong report cùng mục 3, 4).**

---

## 10. Backup & Disaster Recovery

**Current Design:** POC: pgBackRest (WAL hourly + full daily), clickhouse-backup (incremental daily), rclone → VNPT Object Storage; off-site cross-region HN↔HCM weekly full + daily incremental; retention 30d/12w/12m; RPO 1h / RTO 4h; kịch bản DRP gồm mất node, mất region (restore 4h), ransomware (4–6h), mất edge server (PLC tự trị + sync bù).

**Gaps / Risks:**
- G1. Backup chưa **immutable** — ransomware scenario có trong DRP nhưng backup xóa/sửa được thì DRP vô nghĩa.
- G2. Không có restore testing tự động (SLO "backup success 100%" đo job chạy, không đo restore được).
- G3. Thiếu backup: Keycloak realm, EMQX config, Grafana, K8s state (Velero), GitLab; edge site DB chưa có backup offsite.
- G4. RTO 4h là backup-restore; chưa có warm standby → như mục 5, phụ thuộc câu trả lời DR posture.

**Recommendations:**
- R1. **Warm standby region 2 (đề xuất, chờ xác nhận):** PG managed replica async cross-region (nếu VNPT hỗ trợ; fallback pgBackRest standby-restore liên tục); ClickHouse: backup-based (chấp nhận RPO cao hơn cho TSDB vì edge buffer 30 ngày truyền bù được — chính kiến trúc edge đã là backup của telemetry); Object Storage cross-region replication (footage/event evidence); toàn bộ stack còn lại dựng lại bằng IaC/GitOps trong ≤1h. Kết quả: RPO metadata ~5–15 phút, RPO telemetry ≈ 0 (nhờ edge), RTO 1–2h.
- R2. Bucket backup bật **object lock/immutability + versioning**, credential ghi-một-chiều (append-only) tách khỏi credential vận hành.
- R3. Velero cho VKS; config-as-code hóa Keycloak (realm export trong Git), EMQX/Grafana (đã GitOps thì backup = Git). GitLab backup daily → Object Storage.
- R4. Edge: pg_dump/timescale backup nightly đẩy lên Object Storage per-site (băng thông nhỏ, chạy đêm); restore test site = 1 phần của kỳ bảo trì.
- R5. **DR drill mỗi quý** trên STG: kịch bản mất region — đo RTO thật, cập nhật runbook (gắn vào quy trình Gate/QA sẵn có của Collab Guidelines).

**Alternative:** giữ backup-restore RPO 1h/RTO 4h (rẻ nhất — hợp lý nếu <10 KCN và SLA khách chấp nhận 4h mất giám sát tập trung). **Trade-offs:** warm standby +20–30% chi phí data layer; active-active bị loại (chi phí x2, độ phức tạp không tương xứng khi edge đã tự trị).

**Priority: HIGH** (R2 immutable + R5 drill); Medium (R1 tùy xác nhận DR posture).

---

## 11. CI/CD & Infrastructure as Code

**Current Design:** GitLab CI/CD (TechStack); Terraform với VNPT Cloud Provider + VNPT Container Registry (kỹ năng yêu cầu trong POC); Ansible cho backup/bàn giao (giai đoạn 5); DEV/STG/PROD + quy trình release, freeze, CR, as-built versioning (Collab Guidelines — rất tốt); Watchtower auto-update edge (POC — mâu thuẫn).

**Gaps / Risks:**
- G1. Chưa chọn GitOps tool; release lên PROD đang là quy trình giấy + kubectl/helm tay.
- G2. Terraform state management/locking chưa quy hoạch.
- G3. Edge fleet deployment pipeline không tồn tại (Watchtower = anti-pattern, đã nêu mục 1).
- G4. Môi trường DEV cấm nối thiết bị thật (đúng), nhưng chưa có bộ **simulator dữ liệu chuẩn bản tin** dạng sản phẩm dùng chung (Collab doc yêu cầu song song hóa bằng dữ liệu mô phỏng — nên biến thành tool có version).

**Recommendations:**
- R1. **GitLab self-host (VKS/VServer)** — phù hợp data residency + đã là lựa chọn stack; runner trong subnet mgmt.
- R2. **Argo CD** cho VKS (app-of-apps; project per env; sync tự động STG, manual-gate PROD — khớp quy trình release + freeze hiện có). Helm charts trong monorepo platform.
- R3. **Terraform**: modules cho VPC/VKS/DB/LB/DNS; state backend = Object Storage + lock (DynamoDB-equivalent không có → dùng GitLab-managed Terraform state, có sẵn locking). Mọi resource cloud PHẢI qua Terraform (no console-ops sau go-live).
- R4. Edge pipeline: image build → registry → release train theo **ring** (lab → canary site → fleet batch 25%) điều khiển bằng Argo CD/Fleet agent trên K3s site hoặc Ansible-pull; version pin trong Git per-site (chính là "cấu hình lưu kho có phiên bản" mà Collab doc bắt buộc — hiện thực hóa nó).
- R5. Simulator bản tin (Go CLI, dùng JSON Schema từ registry mục 6-R4) là artifact chính thức của DEV — phục vụ cả G2-gate testing của quy trình 2 đội.
- R6. Pipeline chuẩn: lint/test → build → Trivy scan → push → deploy DEV → integration test (simulator) → STG → P2P/SIT theo quy trình → manual approve → PROD.

**Alternative:** Flux thay Argo (nhẹ hơn, ít UI); GitLab environments + auto-deploy không GitOps (đơn giản nhưng mất drift detection). **Trade-offs:** Argo thêm component nhưng UI + RBAC + drift detection đáng giá khi nhiều env × nhiều site.

**Priority: MEDIUM-HIGH** (R3/R4 trước khi site thứ 2 go-live).

---

## 12. Scalability: 10 → 100 → 1000 KCN

**Current Design:** POC multi-tenant: namespace per tenant, `deploy-tenant.sh` (helm install backend per tenant, schema per tenant, MQTT broker per tenant), RLS PostgreSQL; scale-up notes: Kafka khi >100k events/s, Keycloak SSO, Device Registry + OTA, Temporal/Camunda tách workflow.

**Gaps / Risks:**
- G1. **Per-tenant backend + per-tenant broker (POC script) không scale vận hành**: 100 tenant = 100 bộ deployment/upgrade — chi phí vận hành nổ tung trước chi phí hạ tầng.
- G2. Onboarding site thủ công (script + tay) — mục tiêu phải là zero-touch.
- G3. Chưa có Device Registry thực thụ (bảng `sensors` là POC; chính docs thừa nhận cần nâng cấp).
- G4. Không có khái niệm cell/shard → 100+ KCN sẽ đụng trần cluster đơn (blast radius, giới hạn managed DB, cardinality observability).

**Recommendations:**
- R1. **10–30 KCN (bây giờ):** shared services multi-tenant THẬT — 1 bộ backend chung đọc tenant context từ JWT/topic, KHÔNG helm-install per tenant; EMQX chung + ACL (không broker per tenant); PG RLS + schema; ClickHouse database per tenant (nén + TTL riêng được). Namespace per tenant chỉ giữ cho workload đặc thù nếu phát sinh.
- R2. **Cell design (đặt nền bây giờ, dùng ở 100+):** mọi định danh routing mang `cell_id`; 1 cell = {VKS + EMQX + Kafka + CH + PG} phục vụ ~30–50 KCN; global control plane = Keycloak, Device Registry, fleet mgmt, GitOps, observability tổng (Grafana đa datasource). Site gán cell lúc onboard; di chuyển tenant giữa cell = re-point bridge + replicate data (hiếm khi cần). Blast radius = 1 cell.
- R3. **Onboarding = Temporal workflow** (đúng chỗ dùng Temporal của stack đích): tạo tenant/park → cấp cert → EMQX ACL → schema/DB → dashboard template → simulator smoke test → bàn giao G2. Mục tiêu ≤1 ngày kỹ thuật/site (khớp quy trình G0–G6 vốn chạy nhiều tuần cho phần hiện trường — cloud không được là nút cổ chai).
- R4. Device Registry: bảng thiết bị + trạng thái + phiên bản + cert serial, đồng bộ từ tag list as-built (nguồn sự thật hiện có) — làm trước khi nghĩ tới OTA.
- R5. **1000 KCN (nguyên tắc):** nhiều cell theo region (bám 8 DC VNPT), data locality per cell, global chỉ giữ identity + catalog + billing + cross-cell reporting (ClickHouse cluster riêng nhận aggregate); ops model chuyển từ "quản site" sang "quản cell"; chi phối chi phí lúc đó là logistics phần cứng site + đội field service, không phải cloud. Không thiết kế chi tiết bây giờ (YAGNI) — chỉ cần R2 để không khóa đường.

**Trade-offs:** shared multi-tenant tăng yêu cầu kỷ luật code (tenant isolation bug = data leak) so per-tenant deploy; bù bằng RLS + ACL test tự động trong CI (test tenant A không đọc được tenant B — checklist POC đã yêu cầu, tự động hóa nó).

**Priority: HIGH** (R1 — sửa hướng POC trước khi nhân bản); MEDIUM (R2–R4).

---

## 13. Overall Production Infrastructure Architecture (đề xuất)

### 13.1. Sơ đồ tổng thể

```
                        ┌─────────────────────────── VNPT CLOUD — REGION 1 (HN, primary) ──────────────────────────┐
                        │  VPC-PROD                                                                                 │
  Internet users        │  ┌─ edge-ingest ─────────────┐  ┌─ app (VKS app/ingest pools) ────────────────────────┐  │
  (web/mobile/API)      │  │ LB L4 :8883 mTLS ── EMQX×3 │  │ Go microservices (multi-tenant, HPA)               │  │
     │                  │  │ VPN GW (IPsec backup)      │  │ Keycloak · Temporal · API svc · Rule/Alarm consumers│  │
     ▼                  │  └─────────────┬──────────────┘  └──────────────┬──────────────────────────────────────┘  │
  LB L7 + WAAP ─────────┼────────────────┼────────► API/Web               │                                          │
                        │                ▼                                ▼                                          │
                        │  ┌─ data (VKS data pool + managed) ──────────────────────────────────────────────────┐    │
                        │  │ Kafka (managed, RF3) → ClickHouse×2+Keeper │ PG managed HA │ Redis managed         │    │
                        │  │ LGTM: Mimir·Loki·Grafana·Alertmanager │ Vault PKI/secrets │ Object Storage (S3)    │    │
                        │  └────────────────────────────────────────────────────────────────────────────────────┘    │
                        │  ┌─ mgmt ─┐ GitLab+runners · Argo CD · bastion/ZTNA · Terraform state                      │
                        └──────────┴──────────────────────────────┬───────────────────────────────────────────────┘
                                                                  │ async replica (PG) · backup replication (immutable)
                        ┌─────────────────────────── REGION 2 (HCM, warm standby) ─────────────────────────────────┐
                        │ PG replica · Object Storage replicated · IaC sẵn sàng dựng full stack (RTO 1–2h)          │
                        └────────────────────────────────────────────────────────────────────────────────────────────┘
                                     ▲ PRIMARY: VNPT MPLS/L3VPN (SLA, QoS)   ▲ BACKUP: Internet + IPsec (SD-WAN failover)
        ┌────────────────────────────┴──────────────┐        ┌───────────────┴───────────────┐
        │ KCN SITE (mẫu Đồng Văn III — CỐ ĐỊNH)      │        │ KCN site #2..N (site blueprint)│  ×10–30
        │ FortiGate 80F ── DMZ site (Z3.5):          │        └────────────────────────────────┘
        │   EMQX bridge · MediaMTX relay · sync      │
        │ Z3 server room: IOC on-prem · TSDB ≥12mo   │
        │   2×R660xs + R760xs (+DL380 GPU AI) · NVR  │
        │ Z0–2 OT VLANs: 9 tủ IoT ECU-1051(buffer30d)│
        │   ADAM-3600 · PLC (read-only) · Edge AI Box│
        │ Camera VLAN (no Internet) · 4G cabinets→VPN│
        └────────────────────────────────────────────┘
```

### 13.2. Nguyên tắc kiến trúc (chốt)

1. **Edge tự trị là hàng phòng thủ số 1** — cloud down không dừng sản xuất; mọi quyết định HA/DR cloud được "chiết khấu" bởi buffer 30 ngày + PLC fail-safe. Vì vậy: warm standby đủ, active-active là lãng phí.
2. **Ranh giới nghiệm thu tại broker giữ nguyên và nhân đôi:** edge EMQX (ranh giới 2 đội tại site) bridge lên cloud EMQX (ranh giới site↔platform). Mọi dữ liệu vào cloud chỉ qua 1 cửa MQTT mTLS + 1 cửa Object Storage pre-signed.
3. **Managed-first trên VNPT Cloud** (PG/Kafka/Redis/Object Storage/LB/WAAP); self-host có Operator cho phần không có managed (EMQX, ClickHouse, Keycloak, Temporal, LGTM, Vault).
4. **Một pipeline dữ liệu duy nhất:** EMQX → Kafka → ingest → CH/PG/Redis. Không big-data stack cho tới khi có nhu cầu thật.
5. **Shared multi-tenant + cell-ready:** không per-tenant deployment; mọi routing identity mang cell_id từ ngày đầu.
6. **Mọi thứ là code:** Terraform (cloud), Argo CD (workloads), site blueprint (edge), Keycloak/Grafana config trong Git; backup immutable; PKI tự động.

### 13.3. Roadmap triển khai

| Phase | Thời gian | Nội dung | Exit criteria |
|---|---|---|---|
| A — Landing zone | 0–3 tháng | VPC/VKS/managed DB/Kafka; PKI + Vault; GitLab + Argo CD + Terraform; EMQX cloud + bridge ĐV3; LGTM; DMZ site ĐV3; bỏ Watchtower | ĐV3 telemetry hiển thị trên cloud dashboard ≤5s; DEV/STG/PROD hoạt động; 0 secret plaintext |
| B — Production hardening | 3–6 tháng | Warm standby region 2 + DR drill lần 1; immutable backup; onboarding workflow (Temporal) + site blueprint; simulator bản tin; NOC fleet dashboard; RLS/ACL isolation test trong CI | Site #2 onboard ≤1 ngày cloud-side; DR drill đạt RTO ≤2h; tenant isolation test pass tự động |
| C — Scale-out 10–30 | 6–18 tháng | Nhân bản site theo blueprint; capacity theo số liệu thật; Device Registry; tối ưu chi phí (retention, tiering); đánh giá cell #2 khi >30 KCN | ≥10 KCN live; SLO 99.9% đo được; chi phí/site giảm theo scale |

### 13.4. Bảng ưu tiên tổng hợp

| # | Hạng mục | Priority | Ghi chú |
|---|---|---|---|
| 1 | PKI + secrets management (Vault) | HIGH | Gap an ninh lớn nhất; chặn scale nếu thiếu |
| 2 | Bỏ Watchtower + edge GitOps/ring rollout | HIGH | Rủi ro OT trực tiếp |
| 3 | DMZ site + egress whitelist + cloud segmentation | HIGH | Config-only, không đổi hardware |
| 4 | Data plane HA (EMQX×3, Kafka RF3, CH×2, PG HA) | HIGH | POC manifests chưa đạt |
| 5 | Topic standard + command spec (idempotency, 2FA) | HIGH | An toàn điều khiển ngược |
| 6 | Shared multi-tenant (sửa hướng per-tenant của POC) | HIGH | Phải sửa trước khi nhân bản site |
| 7 | LGTM fleet observability + NOC dashboard | HIGH | Xương sống vận hành 30 site |
| 8 | Immutable backup + restore test + DR drill | HIGH | DRP hiện tại chưa kiểm chứng |
| 9 | Hybrid MPLS+IPsec (✅ đã chốt) | HIGH | Internet-only là fallback chấp nhận được |
| 10 | Warm standby region 2 (✅ đã chốt) | MEDIUM-HIGH | Backup-restore là fallback |
| 11 | Terraform + Argo CD + pipeline chuẩn | MEDIUM-HIGH | Trước site #2 |
| 12 | Onboarding automation (Temporal) + Device Registry | MEDIUM | Phase B |
| 13 | Cell architecture chi tiết, Sparkplug, mesh, big-data | LOW | Chỉ khi có tín hiệu nhu cầu thật |

### 13.5. Ước tính chi phí thô `[assumption — cần báo giá VNPT]`

- Cloud shared platform (10 KCN đầu): ~40–70 triệu VNĐ/tháng (VKS 6 worker + managed PG/Kafka/Redis + Object Storage + LB) — so POC 15–20tr/KCN đơn lẻ → shared rẻ hơn rõ khi ≥3 KCN.
- Warm standby region 2: +20–30% data layer (~10–20tr/tháng).
- MPLS/L3VPN: ~3–8tr/site/tháng (tùy băng thông/khoảng cách) + FTTH backup ~1tr/site.
- Edge per site: giữ nguyên BOM ĐV3 (cố định).

---

## Unresolved Questions

1. **[VNPT]** Region nào có multi-AZ thực sự trong 1 region? SLA managed PG/Kafka/Redis (uptime, failover time, phiên bản, PG có PostGIS không)? Managed PG có cross-region read replica không?
2. **[VNPT]** Giá + khả năng cung cấp L3VPN/MPLS site→cloud private peering tại các tỉnh có KCN mục tiêu.
3. **[Đo thực tế]** Message rate + dung lượng thật của ĐV3 sau go-live (số tag active, chu kỳ, event AI/ngày) để thay các con số `[assumption]` mục 6.
4. **[Kỹ thuật]** ECU-1051/EdgeLink có hỗ trợ nạp/rotate cert tự động (EST/SCEP) không? Nếu không → quy trình rotation thủ công theo kỳ bảo trì.
5. **[Sản phẩm]** Nền tảng IOC on-prem ĐV3 "phát triển nội bộ" và Cloud Platform: cùng 1 codebase Go hay 2 sản phẩm? Ảnh hưởng lớn tới CI/CD và blueprint site (report giả định cùng 1 tổ chức phát triển, 2 deployment target).
6. **[Business]** SLA cam kết với chủ đầu tư (99.5%?) — quyết định mức đầu tư HA/DR cuối cùng; và yêu cầu cách ly dữ liệu cứng trong hợp đồng tenant nào không (ảnh hưởng lựa chọn tenancy — nếu có, chuyển tenant đó sang mode DB riêng).
7. **[Compliance]** Rà PDPD (NĐ 13/2023) cho footage/biển số: cần DPA với từng chủ đầu tư + chính sách masking chưa được docs đề cập.
