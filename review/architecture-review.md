# Architecture Review — Industrial IoT Platform

**Ngày:** 2026-07-22 · **Cơ sở:** `docs/system-architecture.md` v1.0 (D1–D7 sticky) + toàn bộ tài liệu `docs/`
**Quy tắc tuân thủ:** review này KHÔNG đề xuất đảo ngược quyết định D1–D7 đã chốt. Phát hiện chạm tới quyết định sticky được ghi trạng thái và trình user quyết định (đánh dấu `[USER-DECISION]`). Nhận định dựa trên kiến thức ngoài tài liệu được đánh dấu `[external — cần verify]`.

---

## Mục lục

1. [Overall Architecture](#1-overall-architecture)
2. [On-Premise Architecture](#2-on-premise-architecture)
3. [Cloud Architecture](#3-cloud-architecture)
4. [Hybrid Connectivity](#4-hybrid-connectivity)
5. [Network Design](#5-network-design)
6. [Security](#6-security)
7. [High Availability](#7-high-availability)
8. [Disaster Recovery](#8-disaster-recovery)
9. [Scalability](#9-scalability)
10. [Observability](#10-observability)
11. [CI/CD](#11-cicd)
12. [Infrastructure](#12-infrastructure)
13. [Bảng tổng hợp rủi ro](#13-bảng-tổng-hợp-rủi-ro)

---

## 1. Overall Architecture

**Điểm mạnh**
- Nguyên tắc "Edge tự trị là hàng phòng thủ số 1" nhất quán xuyên suốt và được dùng đúng để chiết khấu chi phí HA/DR cloud (warm standby thay vì active-active) — lập luận kiến trúc chặt chẽ.
- 7 quyết định D1–D7 rõ ràng, có trace từ brainstorm report (12 chủ đề, trade-offs) → journal → system-architecture. Hiếm dự án giai đoạn design có audit trail tốt như vậy.
- YAGNI kỷ luật: hoãn Spark/Flink/HDFS/Trino/MinIO/service mesh/Sparkplug có lý do ghi rõ.
- Số liệu chưa đo được đánh dấu `[assumption]` — trung thực về độ tin cậy dữ liệu.
- Ranh giới nghiệm thu tại broker (Quy chế 2 đội) được giữ nguyên và nhân đôi lên cloud — thiết kế tổ chức khớp thiết kế kỹ thuật.

**Điểm yếu**
- Header `system-architecture.md` ghi "3 quyết định chốt", bảng có 7, journal ghi 6 — trace "quyết định nào do user xác nhận trực tiếp" bị mờ (quan trọng vì quy tắc sticky phân biệt user-confirmed vs Claude-proposed). — **Medium**
- Open Items §15 chứa 7 câu hỏi nền tảng (multi-AZ, PostGIS, MPLS coverage, 1-vs-2 codebase) nhưng chưa gắn deadline/owner; một số quyết định thiết kế (HA, DR) phụ thuộc trực tiếp câu trả lời. — **High**

**Thiếu sót**
- Chưa có ADR chính thức (brainstorm report là ADR de-facto nhưng trộn 12 chủ đề trong 1 file, khó version từng quyết định). — **Medium**
- Câu hỏi "IOC on-prem và Cloud Platform: 1 codebase hay 2 sản phẩm" (open item #5) ảnh hưởng toàn bộ CI/CD + site blueprint nhưng vẫn treo. `[USER-DECISION]` — **High**

**Rủi ro**
- Thiết kế cloud dựa trên năng lực VNPT chưa xác minh (multi-AZ, managed PG PostGIS/cross-region replica, Kafka SLA). Nếu VNPT không đáp ứng, D5/HA phải điều chỉnh mức triển khai (không đổi quyết định, đổi cách thực hiện). — **High**

**Đề xuất:** xem `recommendations.md` R-05, R-10, R-12.

---

## 2. On-Premise Architecture

**Điểm mạnh**
- D7 Docker Compose khớp năng lực đội vận hành site, tránh gánh nặng K8s ×30 site; keepalived VIP cho app host active/standby là giải pháp đúng tầm.
- Bỏ Watchtower, thay bằng Ansible-pull + version pin per-site + ring rollout (lab → canary → fleet) — xử lý đúng rủi ro OT lớn nhất mà brainstorm phát hiện.
- Site Blueprint (Git repo, as-built có version) — số hóa đúng yêu cầu "cấu hình lưu kho có phiên bản" của Quy chế; nền tảng cho nhân bản 30 site.
- DMZ Z3.5 mới trên FortiGate: cô lập OT khỏi Internet, chỉ EMQX bridge + MediaMTX + sync được ra cloud — đúng chuẩn IIoT, chỉ đổi config không đổi hardware (tôn trọng D1).
- NTP chrony local nguồn GPS/4G — giải quyết yêu cầu bản tin bắt buộc NTP timestamp khi mất WAN.
- Video giữ tại site (NVR 30 ngày), cloud chỉ nhận metadata + snapshot — đúng bài toán băng thông.

**Điểm yếu**
- **Data host R760xs là SPOF ở tầng software:** PG + TimescaleDB + Redis local đều trên 1 máy, không có cơ chế failover/hành vi khi hỏng được mô tả. App tier có VIP nhưng mất data tier thì IOC local dashboard + rule engine mất theo. Brainstorm G1 đã nêu "mất 1 server → chưa rõ hành vi" nhưng system-architecture chỉ giải quyết app tier. Hardware cố định (D1) → chỉ có thể xử lý bằng software: định nghĩa degraded mode, backup/restore nhanh, runbook. — **High**
- DL380 GPU đơn chiếc: hỏng = mất VMS + AI toàn site (chấp nhận được vì không phải safety function — PLC fail-safe độc lập — nhưng chưa ghi nhận rõ trong docs). — **Medium**
- NVR đơn + 1 HDD 10TB không RAID: mất footage 30 ngày nếu hỏng ổ — dữ liệu có thể là bằng chứng pháp lý (PDPD/an ninh). Hardware cố định → ghi nhận rủi ro, cân nhắc backup footage sự kiện quan trọng lên Object Storage. — **Medium**
- Giới hạn nền tảng IOC theo hợp đồng duy trì: 10 user đồng thời, 5.000 I/O, 300 camera (Technical Report §7.4) — PDR lại ghi "50 on-prem local users". Mâu thuẫn spec (xem consistency C-07). — **Medium**

**Thiếu sót**
- Chưa có spec failover thủ công app host (thao tác keepalived, thời gian chấp nhận được).
- Chưa có UPS runtime target (2× 6kVA nuôi được bao lâu? hành vi shutdown có trật tự?). — **Medium**
- Edge TSDB cho site mới theo blueprint: brainstorm R4 nói "site mới dùng 1 chuẩn duy nhất" nhưng chuẩn nào (TimescaleDB?) chưa chốt thành văn. — **Low**

**Rủi ro**
- 30 site × thao tác thủ công khi sự cố data host = chi phí vận hành tăng tuyến tính (đúng trade-off đã chấp nhận ở D7, cần runbook để kiểm soát). — **Medium**

---

## 3. Cloud Architecture

**Điểm mạnh**
- Landing zone rõ: VPC PROD riêng, DEV+STG chung VPC tách subnet; 4 subnet chức năng (edge-ingest/app/data/mgmt); 3 node pools tách theo workload profile (app/data-NVMe/ingest) — burst ingest không ảnh hưởng app.
- Managed-first có nguyên tắc rõ (stateful có managed → managed; còn lại Operator trên VKS) + danh sách self-host cụ thể (EMQX, ClickHouse Altinity, Keycloak, Temporal, LGTM, Vault).
- Phân biệt đúng WAAP (L7 HTTP only) không đặt trước MQTT — sửa đúng lỗi POC.
- GPU pool hoãn có lý do (AI inference tại edge).

**Điểm yếu**
- **Pipeline `EMQX cloud → Kafka` không nêu thành phần thực hiện.** §7 viết "EMQX → Kafka → Go ingest" nhưng không nói cái gì đưa message từ EMQX vào Kafka. `[external — cần verify]`: Kafka data-integration của EMQX là tính năng Enterprise; bản open-source (đang chọn cho edge, chưa rõ cho cloud) không có. Hai phương án hợp lệ: (a) EMQX Enterprise license, (b) Go ingest consume MQTT (shared subscription) rồi produce Kafka — khi đó pipeline thực tế là `EMQX → Go ingest → Kafka → consumers` và sơ đồ/§7 phải sửa lại thứ tự. Đây là quyết định Phase A blocker. — **Critical**
- `API Gateway` xuất hiện trong `description.md` và cloud diagram ("routing · rate limit · JWT verify") nhưng **không có** trong system-architecture §6 Ingress — thành phần này có tồn tại không, là sản phẩm gì (VNPT API Gateway managed? tự dựng?), chưa chốt. — **Medium**
- Keycloak/Temporal/Vault: chưa có sizing + HA topology (Vault HA cần raft ≥3 node; Keycloak cluster mode). Chỉ ghi "self-host trên VKS". — **Medium**

**Thiếu sót**
- Chưa có chính sách phiên bản/upgrade VKS (K8s minor version cadence, ai vá control plane — VNPT hay đội?). **Missing Information** — cần tài liệu SLA VKS từ VNPT. — **Medium**
- Chưa quy hoạch DNS (ai quản `mqtt.{env}.<domain>`, provider nào hỗ trợ health-checked failover TTL thấp — VNPT DNS có không?). **Missing Information** — **Medium**

**Rủi ro**
- Nếu managed PG VNPT không có PostGIS hoặc cross-region replica (open item #1) → phải chuyển CloudNativePG self-host, tăng ops đáng kể — cần trả lời trước khi thiết kế chi tiết Phase A. — **High**

---

## 4. Hybrid Connectivity

**Điểm mạnh**
- Underlay 2 lớp MPLS primary + IPsec backup với SD-WAN failover trên FortiGate (D4) — tận dụng VNPT vừa là ISP vừa là cloud; có ước tính băng thông theo loại lưu lượng (telemetry <1Mbps, event ảnh ~5Mbps, video 2–8Mbps/stream).
- Data plane chuẩn hóa 1 cửa: MQTT bridge mTLS + Object Storage pre-signed URL; bỏ bash sync POC; backfill giữ cờ truyền bù + sequence theo Interface Agreement.
- Tủ 4G giữ VPN về FortiGate site, không nối thẳng cloud — bảo toàn ranh giới nghiệm thu tại broker. Nhất quán trên cả 3 sơ đồ.
- Endpoint failover: FQDN TTL thấp, health-checked, trỏ region 2 khi DR.

**Điểm yếu**
- Hành vi EMQX bridge khi failover (MPLS→IPsec, region 1→2): thời gian phát hiện, reconnect, resume session, khả năng duplicate khi retry — chưa spec. QoS1 + dedup theo sequence có cover nhưng chưa ghi thành thiết kế bridge. — **Medium**
- Chưa có kịch bản kiểm thử failover định kỳ tại site (rút MPLS, đo thời gian chuyển IPsec, xác nhận không mất bản tin) — Quy chế có test truyền bù 4G (rút antenna 10 phút) nhưng chưa có tương đương cho WAN site. — **Medium**

**Thiếu sót**
- QoS policy cụ thể trên MPLS (class cho command/alarm vs bulk backfill) mới ở mức nguyên tắc. — **Low**
- MPLS coverage + giá theo tỉnh chưa xác minh (open item #2) — ảnh hưởng roadmap Phase C chọn site. **Missing Information** — **High**

**Rủi ro**
- Backfill sau mất kết nối dài (giờ→ngày) tạo burst khi khôi phục; chưa có rate-limit/backpressure spec cho bridge → có thể đè ingest path đúng lúc nhạy cảm. — **Medium**

---

## 5. Network Design

**Điểm mạnh**
- Site zoning ánh xạ Purdue/IEC 62443 rõ ràng (Z0–2 OT / Z3 ops / Z3.5 DMZ / Z4 IT / camera / mgmt) kèm bảng conduit cho phép; deny-by-default; egress whitelist theo FQDN.
- Camera VLAN không route Internet; iDRAC/iLO vào mgmt VLAN chỉ truy cập qua tunnel — đóng đúng 2 lỗ hổng phổ biến.
- Cloud: subnet chức năng + security group deny-by-default + VKS NetworkPolicy default-deny per namespace.

**Điểm yếu**
- FortiGate 80F là thiết bị duy nhất phân đoạn mọi VLAN + terminate mọi VPN (sơ đồ on-prem ghi rõ "một thiết bị vật lý"). Hỏng firewall = site mất phân đoạn + mất uplink (edge vẫn tự trị nhưng mù giám sát). Hardware cố định (D1) → ghi nhận rủi ro, cần spare/RMA plan + config backup tự động. — **Medium**
- EVN REST API polling (Internet) — thành phần nào poll, đứng ở zone nào, đi qua egress whitelist ra sao? Chưa quy hoạch (chỉ ghi ở §8 như 1 nguồn dữ liệu). — **Medium**

**Thiếu sót**
- **Chưa có IP addressing plan / VLAN numbering:** zone mới ở mức khái niệm; 30 site cần scheme địa chỉ không trùng lặp (site-to-cloud routing qua MPLS sẽ đụng nếu site nào cũng 192.168.x). Đây là việc phải chốt trước site #2. — **High**
- Chưa có firewall rule matrix chi tiết (bảng conduit là mức zone; cần port/protocol/direction cụ thể để cấu hình FortiGate nhất quán 30 site qua blueprint). — **Medium**

---

## 6. Security

**Điểm mạnh**
- PKI 2 tầng (offline root + intermediate per env, Vault PKI), cert per gateway CN `{tenant}:{park}:{gw}`, rotation trước hạn 90 ngày, CRL/OCSP tại EMQX, fallback rotation theo kỳ bảo trì — PKI lifecycle từ chỗ "gap lớn nhất" (brainstorm G1) thành thiết kế cụ thể.
- Secrets: Vault + External Secrets Operator, cấm plaintext, CI secrets từ Vault — đóng gap `.env` POC.
- IAM hợp lý: Keycloak 1 realm + organization/group per tenant (tránh realm explosion), OIDC SSO đồng nhất, **2FA TOTP bắt buộc cho role điều khiển ngược**, RBAC 3 nhóm khớp Technical Report.
- Admin 1 cửa: bastion + ZTNA, không mở SSH/mgmt từ Internet, session log tập trung.
- Điều khiển ngược: whitelist đúng danh mục site + idempotency key + timeout 5s + audit stream Kafka→ClickHouse immutable — chain an toàn tốt.
- Compliance: data residency VNPT ✓, PDPD NĐ 13/2023 nhận diện đúng (footage/biển số = dữ liệu cá nhân, cần DPA + masking).
- Zero Trust roadmap thực dụng (năm 1: mTLS device + ZTNA + deny-by-default; mesh để sau).

**Điểm yếu**
- Chưa có **threat model** chính thức (STRIDE hoặc IEC 62443 SL-target per zone). Các kiểm soát hiện tại tốt nhưng không chứng minh được độ phủ. — **High**
- Chưa có **security incident response plan** — bảng P1–P4 của Quy chế là sự cố vận hành, không phải security incident (compromise cert, ransomware edge, insider). DRP có kịch bản ransomware cho backup nhưng không có quy trình phát hiện/cô lập/điều tra. — **High**
- Tài liệu tham chiếu TechStack_Pipeline ghi "Encrypted sensitive data: md5" và "tls 1.2" `[external]`: MD5 không phải mã hóa và đã broken; TLS floor nên là 1.2+ với cipher hiện đại, khuyến nghị 1.3. Docs đích chưa có **crypto standards** chính thức để phủ quyết các đề xuất cũ này — rủi ro dev đọc tài liệu tham chiếu và làm theo. — **High**
- Cert rotation tự động phụ thuộc ECU-1051/EdgeLink hỗ trợ EST/SCEP — chưa verify (open item #4); fallback 6 tháng thủ công ×30 site ×~10 gateway = gánh nặng đáng kể. **Missing Information** — **Medium**
- OT monitoring: nguyên tắc read-only PLC được cấu hình nhưng không có giám sát vi phạm conduit (NIDS/OT anomaly detection) — chấp nhận được ở quy mô này nhưng nên ghi nhận là quyết định có ý thức. — **Low**

**Thiếu sót**
- SBOM / ký image (cosign/notation) chưa đề cập — Trivy scan là detective, chưa có preventive supply-chain control. — **Medium**
- Chính sách masking biển số + DPA template (open item #7) chưa có. — **Medium**

---

## 7. High Availability

**Điểm mạnh**
- HA phân tier đúng trọng số: Tier-0 ingest (EMQX×3, Kafka RF3, LB) phải sống vì realtime alarm; Tier-1 data (PG HA, CH 2 replica + 3 Keeper, Redis replica); Tier-2 app (replicas ≥2 + PDB) mất vài phút chấp nhận được.
- SLO kế thừa có căn cứ: uptime 99.9%, MQTT delivery 99.99%, API p95 <200ms, kèm burn-rate alerts.
- Alarm path tách consumer riêng để KPI ≤2s không bị bulk ingest ảnh hưởng.

**Điểm yếu**
- **Toàn bộ HA có thể đang nằm trong 1 AZ** — multi-AZ VNPT chưa xác nhận (open item #1). Brainstorm R2 có phương án chấp nhận single-AZ + ghi rõ trong SLA khách hàng, nhưng system-architecture chưa ghi hệ quả này vào §9/SLO. — **High**
- Error budget chưa phân bổ cho thành phần (99.9% tổng = bao nhiêu cho ingest, API, dashboard?) — khó vận hành SLO khi chưa chia. — **Medium**
- Chaos test định kỳ (kill broker pod, drain node) có trong brainstorm R3 nhưng **không được mang sang** system-architecture — rơi mất một kiểm soát tốt. — **Medium**

**Thiếu sót**
- Chưa định nghĩa hành vi degraded mode cloud (EMQX cloud chết: edge vẫn buffer — nhưng dashboard hiển thị gì, alarm nghiệp vụ đứt ở đâu, thông báo tenant thế nào). — **Medium**

---

## 8. Disaster Recovery

**Điểm mạnh**
- Bảng backup per thành phần với RPO riêng + cơ chế cụ thể (PG replica async, clickhouse-backup, Velero, config-as-code, edge nightly dump) — đầy đủ hơn đa số thiết kế cùng giai đoạn.
- Backup immutable (object lock + versioning + credential append-only tách riêng) — xử lý đúng kịch bản ransomware của DRP.
- Restore test tự động hàng tháng + DR drill mỗi quý đo RTO thật, gắn vào quy trình Gate/QA — hiếm và rất tốt.

**Điểm yếu**
- **Tuyên bố "telemetry RPO≈0 thực tế nhờ edge buffer 30d truyền bù" chưa có cơ chế kỹ thuật đỡ.** Store-and-forward của gateway/bridge chỉ giữ dữ liệu **chưa gửi thành công**; dữ liệu đã ACK lên cloud rồi mất do DR (ClickHouse RPO ≤24h, Kafka không replicate) sẽ **không tự truyền bù** — không có thiết kế "cloud yêu cầu site replay lại khoảng thời gian X→Y" (từ TSDB site hoặc buffer gateway). Nếu không bổ sung cơ chế re-request/replay, RPO telemetry thực = RPO ClickHouse backup (≤24h), không phải ≈0. Không đảo D5 — chỉ cần bổ sung thiết kế để D5 đạt được đúng như tuyên bố. — **Critical**
- Region 2 sizing chưa nêu: warm standby "IaC dựng full stack" nhưng quota/capacity region HCM có sẵn để nhận full fleet trong 1–2h không? **Missing Information** (phụ thuộc VNPT). — **High**
- DR drill trên STG đo được quy trình, không đo được capacity thật region 2. — **Medium**

**Thiếu sót**
- DR runbook chưa tồn tại (kế hoạch Phase B — chấp nhận được, nhưng G1 exit criteria roadmap ghi "DR drill runbook v0.1" ngay Phase A: cần khớp). — **Low**
- Chưa có tiêu chí failback (quay về region 1 sau DR: đồng bộ ngược dữ liệu phát sinh ở region 2 thế nào?). — **Medium**

---

## 9. Scalability

**Điểm mạnh**
- Shared multi-tenant thật (không per-tenant deploy) sửa đúng hướng POC trước khi nhân bản — kèm biện pháp bù kỷ luật: **isolation test tự động trong CI** (tenant A ≠ B ở mọi tầng API/DB/MQTT).
- Cell-ready từ ngày đầu (mọi routing identity mang `cell_id`, blast radius = 1 cell) mà không thiết kế chi tiết sớm (YAGNI đúng chỗ).
- Kafka topic theo domain + partition key `{tenant}/{park}` — tránh topic explosion, giữ ordering per site.
- Onboarding = Temporal workflow zero-touch ≤1 ngày cloud-side — đúng chỗ dùng Temporal, exit criteria đo được (Phase B).

**Điểm yếu**
- Tenancy model PG ghi không nhất quán: D6 "RLS/schema", §13 "RLS + schema per tenant", PDR chỉ "RLS". RLS và schema-per-tenant là 2 mô hình khác nhau về migration/ops — cần chốt 1 (hoặc rõ tiêu chí dùng cái nào cho bảng nào). — **Medium**
- Capacity toàn bộ `[assumption]` chờ số liệu ĐV3 (open item #3) — đúng kế hoạch, nhưng chưa có **kế hoạch đo** cụ thể (metric nào, bao lâu sau go-live, ai chịu trách nhiệm hiệu chỉnh §7). — **Medium**
- Chưa có load test kế hoạch xác nhận 2.000–6.000 msg/s + alarm ≤2s dưới tải (simulator có thể tái dùng). — **Medium**

**Thiếu sót**
- ClickHouse database-per-tenant: chưa nêu quy trình schema migration ×N tenant (30 OK, 100+ cần tooling). — **Low**

---

## 10. Observability

**Điểm mạnh**
- LGTM stack multi-tenant với retention khớp yêu cầu (metrics 13 tháng ≥ yêu cầu 12 tháng, logs 90 ngày); external labels `{tenant, park, site}` chuẩn cho fleet.
- Tracing OpenTelemetry xuyên pipeline + **synthetic probe per site đo KPI ≤5s end-to-end** — cách duy nhất đo KPI hợp đồng một cách khách quan, rất tốt.
- Phân biệt NOC fleet dashboard (tunnel, bridge lag, heartbeat, backfill backlog, cert expiry) với dashboard nghiệp vụ IOC — đúng nhu cầu 2 đối tượng.
- Alert routing khớp bảng P1–P4 của Quy chế; on-call bằng tool thay quy trình giấy.

**Điểm yếu**
- `[external — cần verify]` **Grafana Agent đã EOL (2025-11-01)** — thiết kế edge ghi "Grafana Agent remote_write"; nên chuyển sang Grafana Alloy (tương thích cấu hình) trước khi triển khai Phase A. — **Medium**
- `[external — cần verify]` **Grafana OnCall OSS đã vào maintenance mode (2025)** — lựa chọn on-call tool nên xác minh lại trạng thái dự án trước khi commit. — **Medium**
- SLO 99.9% uptime: chưa định nghĩa đo tại đâu (API? dashboard? per tenant hay toàn platform?) — burn-rate alert cần định nghĩa SLI trước. — **Medium**

**Thiếu sót**
- Alert catalog (danh mục alert chuẩn kèm ngưỡng, mức P, kênh) — bảng ngưỡng POC được "giữ nguyên" bằng tham chiếu vào file base64 nặng; nên trích thành doc chính thức. — **Medium**
- Chưa có audit/monitoring cho chính hệ observability (Loki/Mimir down thì ai biết?) — meta-monitoring. — **Low**

---

## 11. CI/CD

**Điểm mạnh**
- GitLab self-host (data residency) + Argo CD app-of-apps + auto-sync STG / manual gate PROD — khớp chính xác quy trình release + freeze 48h của Quy chế 2 đội.
- Terraform toàn bộ resource + GitLab-managed state có locking + "không console-ops sau go-live" — kỷ luật IaC rõ.
- Edge pipeline ring rollout (lab → canary → fleet 25%/batch) + version pin per-site — số hóa đúng yêu cầu as-built versioning.
- **Simulator bản tin là artifact chính thức** (DEV cấm thiết bị thật theo Quy chế) dùng chung cho dev + integration test + P2P chuẩn bị — thiết kế thông minh, phục vụ cả gate G3.
- Pipeline chuẩn có Trivy scan + isolation test trong CI.

**Điểm yếu**
- Chưa có quy trình **rollback** tường minh (cloud: Argo rollback OK; edge: revert version pin + Ansible-pull — cần viết thành thao tác chuẩn kèm thời gian). — **Medium**
- Image signing/provenance (cosign) chưa có — pipeline hiện chỉ scan. — **Medium**
- Site blueprint validation trong CI (lint compose, diff config per-site, test instantiate) chưa mô tả. — **Low**

**Thiếu sót**
- `[external — cần verify]` Terraform provider cho VNPT Cloud: mức độ trưởng thành/coverage resource chưa được xác minh trong docs — nếu provider thiếu, "mọi resource qua Terraform" không khả thi 100%. **Missing Information** — **Medium**

---

## 12. Infrastructure

**Điểm mạnh**
- "Mọi thứ là code" nhất quán: Terraform / Argo CD / site blueprint / Keycloak+Grafana config trong Git / backup immutable / PKI tự động.
- Node pool + managed service sizing khởi điểm có con số cụ thể (dù `[assumption]`) — đủ để lập dự toán.
- Registry tách prod (VNPT) / dev (GitLab).

**Điểm yếu**
- Chi phí ước tính thô chưa có báo giá VNPT đối chiếu (đã đánh dấu `[assumption]`) — quyết định go/no-go Phase A cần số thật. — **Medium**
- Chưa có naming/tagging convention cho cloud resources (cost allocation per tenant/site về sau cần từ đầu). — **Low**

**Thiếu sót**
- Quota management VNPT Cloud (limit account, quota region 2 cho DR) chưa đề cập. **Missing Information** — **Medium**

---

## 13. Bảng tổng hợp rủi ro

| ID | Rủi ro | Lĩnh vực | Mức | Ghi chú |
|---|---|---|---|---|
| AR-01 | RPO telemetry ≈0 tuyên bố nhưng không có cơ chế replay sau DR | DR | **Critical** | Cần thiết kế bổ sung, không đổi D5 |
| AR-02 | Thành phần EMQX→Kafka chưa xác định (license/kiến trúc) | Cloud/Data | **Critical** | Phase A blocker |
| AR-03 | Multi-AZ + PostGIS + MPLS coverage chưa verify với VNPT | Cloud/HA/Connectivity | **High** | Open items chưa có deadline |
| AR-04 | Data host on-prem (R760xs) SPOF không có defined behavior | On-Prem | **High** | Software-only mitigation (D1 giữ nguyên) |
| AR-05 | Thiếu threat model + security incident response | Security | **High** | |
| AR-06 | Crypto standards chưa phủ quyết MD5/TLS cũ trong tài liệu tham chiếu | Security | **High** | |
| AR-07 | Chưa có IP/VLAN addressing plan cho 30 site | Network | **High** | Trước site #2 |
| AR-08 | Region 2 capacity/quota chưa xác nhận | DR | **High** | Missing Information |
| AR-09 | Cert rotation phụ thuộc EST/SCEP chưa verify | Security | **Medium** | Open item #4 |
| AR-10 | Grafana Agent EOL / OnCall maintenance mode | Observability | **Medium** | [external — cần verify] |
| AR-11 | FortiGate 80F đơn chiếc phân đoạn toàn site | Network | **Medium** | D1 cố định — spare/RMA plan |
| AR-12 | Backfill burst không có backpressure spec | Connectivity | **Medium** | |
| AR-13 | PG tenancy model (RLS vs schema) chưa chốt 1 | Scalability | **Medium** | |
| AR-14 | NVR/HDD đơn — mất footage khi hỏng ổ | On-Prem | **Medium** | D1 cố định — backup evidence lên Object Storage |
