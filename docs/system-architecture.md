# System Architecture — Industrial IoT Platform (Production)

**Version:** 1.0 · 2026-07-22 · Trạng thái: Đã duyệt (3 quyết định kiến trúc chốt 2026-07-22)
**Phân tích đầy đủ (gaps/alternatives/trade-offs):** `plans/reports/brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md`
**DDD Bounded Context Map (application layer, POC → Production):** `docs/ddd-bounded-context-map.md` (2026-07-24)
**Tài liệu nguồn:** `docs/description.md`, `docs/POC_architecture.md`, `docs/TechStack_Pipeline.docx.md`, `docs/Industrial_Park_Technical_Report.pdf`, `docs/IoT_Software_Team_Collaboration_Guidelines.pdf`

---

## 1. Tổng quan & Quyết định kiến trúc

Nền tảng quản lý vận hành tập trung cho nhiều khu công nghiệp (KCN), mô hình Hybrid:
- **On-Premise Platform** tại từng KCN — cố định theo mẫu Đồng Văn III, tự trị khi mất kết nối.
- **Cloud Platform** trên VNPT Cloud — quản lý tập trung, multi-tenant (tenant = chủ đầu tư, sở hữu ≥1 KCN).

### Quyết định đã chốt

| # | Quyết định | Lựa chọn |
|---|---|---|
| D1 | Edge baseline | Cố định 100% theo mẫu ĐV3 (hardware BOM không đổi; chỉ can thiệp software/ops) |
| D2 | Tech stack đích | Go/Gin · EMQX · Kafka · ClickHouse · PostgreSQL · Redis · Keycloak · Temporal |
| D3 | Scale target | Thiết kế cho 10–30 KCN; cell-ready để lên 100+; mốc 1000 chỉ nguyên tắc |
| D4 | Hybrid connectivity | VNPT MPLS/L3VPN primary + Internet IPsec backup (FortiGate SD-WAN failover) |
| D5 | DR posture | Warm standby region 2 (HN primary ↔ HCM standby); RPO 5–15 phút, RTO 1–2h |
| D6 | Tenancy | Shared cluster + PostgreSQL RLS/schema + EMQX ACL; mọi routing identity mang `cell_id` |
| D7 | On-Prem runtime | **Docker Compose** — KHÔNG dùng Kubernetes/K3s tại site (xác nhận 2026-07-22); K8s chỉ dùng trên Cloud (VKS) |

### Nguyên tắc kiến trúc

1. **Edge tự trị là hàng phòng thủ số 1:** PLC giữ ngưỡng cục bộ + fail-safe (NĐ 40/2015); gateway buffer 30 ngày truyền bù. Cloud down không dừng sản xuất → cloud chỉ cần warm standby, không active-active.
2. **Một cửa vào cloud:** mọi dữ liệu qua MQTT mTLS (EMQX edge bridge → EMQX cloud) hoặc Object Storage pre-signed URL. Không có đường nào khác từ site vào cloud.
3. **Managed-first:** dùng managed VNPT cho PG/Kafka/Redis/Object Storage/LB/WAAP; self-host bằng Operator trên VKS cho phần không có managed (EMQX, ClickHouse, Keycloak, Temporal, LGTM, Vault).
4. **Một pipeline dữ liệu duy nhất:** EMQX → Kafka → ingest (Go) → ClickHouse/PG/Redis. Không big-data stack (Spark/Flink/HDFS/Trino) cho tới khi có nhu cầu vượt ClickHouse. Không MinIO (dùng VNPT Object Storage).
5. **Shared multi-tenant thật sự:** một bộ backend chung đọc tenant context, KHÔNG deploy backend/broker per tenant.
6. **Mọi thứ là code:** Terraform (cloud resources), Argo CD (workloads), site blueprint Git (edge), Keycloak/Grafana config trong Git; backup immutable; PKI tự động.
7. **Ranh giới nghiệm thu tại broker** (theo Quy chế phối hợp 2 đội) giữ nguyên và nhân đôi: edge broker = ranh giới đội IoT/Phần mềm tại site; cloud broker = ranh giới site/platform.

---

## 2. Sơ đồ tổng thể

```
                        ┌─────────────────── VNPT CLOUD — REGION 1 (HN, primary) ───────────────────┐
                        │  VPC-PROD                                                                  │
  Internet users        │  ┌─ edge-ingest ─────────────┐  ┌─ app (VKS app/ingest pools) ──────────┐ │
  (web/mobile/API)      │  │ LB L4 :8883 mTLS ── EMQX×3 │  │ Go microservices (multi-tenant, HPA)  │ │
     │                  │  │ VPN GW (IPsec backup)      │  │ Keycloak · Temporal · API · consumers │ │
     ▼                  │  └─────────────┬──────────────┘  └───────────────┬────────────────────────┘ │
  LB L7 + WAAP ─────────┼────────────────┼────────► API/Web                │                           │
                        │                ▼                                 ▼                           │
                        │  ┌─ data (VKS data pool + managed) ─────────────────────────────────────┐   │
                        │  │ Kafka (managed RF3) → ClickHouse×2+Keeper │ PG managed HA │ Redis     │   │
                        │  │ LGTM (Mimir·Loki·Grafana·AM) │ Vault PKI/secrets │ Object Storage     │   │
                        │  └───────────────────────────────────────────────────────────────────────┘   │
                        │  ┌─ mgmt ─┐ GitLab+runners · Argo CD · bastion/ZTNA · TF state               │
                        └──────────┴──────────────────────┬────────────────────────────────────────┘
                                                          │ PG async replica · backup repl (immutable)
                        ┌───────────────── REGION 2 (HCM, warm standby) ──────────────────────────┐
                        │ PG replica · Object Storage replicated · IaC dựng full stack (RTO 1–2h)  │
                        └──────────────────────────────────────────────────────────────────────────┘
                              ▲ PRIMARY: VNPT MPLS/L3VPN (SLA, QoS)  ▲ BACKUP: Internet + IPsec
        ┌─────────────────────┴───────────────┐       ┌──────────────┴────────────────┐
        │ KCN SITE (mẫu Đồng Văn III — CỐ ĐỊNH)│       │ KCN site #2..N (site blueprint)│ ×10–30
        │ FortiGate 80F ── DMZ site (Z3.5):    │       └────────────────────────────────┘
        │   EMQX bridge · MediaMTX · sync      │
        │ Z3 server room: IOC on-prem · TSDB   │
        │   2×R660xs + R760xs + DL380 GPU · NVR│
        │ Z0–2 OT VLANs: tủ IoT ECU-1051 (30d) │
        │   ADAM-3600 · PLC read-only · AI Box │
        │ Camera VLAN (no Internet) · 4G→VPN   │
        └──────────────────────────────────────┘
```

---

## 3. Edge / On-Premise (cố định theo ĐV3)

> Sơ đồ (Mermaid `.mmd` trong `docs/diagrams/`): `overall-hybrid-architecture` · `cloud-platform-architecture` · `on-premise-platform-architecture`

**Hardware (BOM cố định):** 9 tủ IoT ECU-1051 (Modbus RTU/TCP⇄MQTT, SD buffer 30 ngày, 4 tủ kèm 4G EG25-G), ADAM-3600 datalogger (TT 10/2021, ISO 27001), 2× Edge AI Box Jetson Orin, FortiGate 80F, server room: 2× Dell R660xs (app) + R760xs (data) + HPE DL380 GPU 48GB (AI) + NVR + 2× UPS 6kVA. OT read-only; điều khiển ngược chỉ: 9 lộ chiếu sáng + PTZ camera.

**Chuẩn software/ops trên hardware đó:**
- **Site Blueprint** (Git repo): manifests + config template, mỗi site 1 thư mục as-built có version. Site mới = instantiate blueprint.
- Runtime: **Docker Compose** (D7 — KHÔNG K8s/K3s tại site): app services trên 2× R660xs active/standby qua keepalived VIP; data services (PG, TimescaleDB, Redis) trên R760xs; VMS+AI trên DL380 GPU.
- **Cấm Watchtower / auto-update.** Cập nhật qua Ansible-pull, version pin trong Git per-site, rollout theo ring (lab → canary site → fleet).
- Edge broker: EMQX open-source (thay Mosquitto POC) — đồng nhất stack, có sẵn bridge/ACL/mTLS.
- NTP: chrony local (nguồn GPS/4G khi mất WAN) — bản tin bắt buộc NTP timestamp.
- iDRAC/iLO vào VLAN mgmt, chỉ truy cập qua tunnel quản trị.
- Video: footage ở NVR local (30 ngày); cloud chỉ nhận metadata + snapshot sự kiện; live view từ xa qua MediaMTX relay (DMZ) theo yêu cầu, giới hạn concurrent stream.

---

## 4. Hybrid Connectivity (D4)

- **Primary:** VNPT MPLS/L3VPN site ↔ VNPT Cloud private peering. Băng thông tham chiếu 20–50 Mbps/site (telemetry <1 Mbps; event ảnh ~5 Mbps burst; video on-demand 2–8 Mbps/stream).
- **Backup:** Internet FTTH + IPsec (FortiGate → cloud VPN GW), SD-WAN rule tự failover.
- **Data plane:** EMQX edge bridge → EMQX cloud qua tunnel, mTLS cert per-site; file lớn upload thẳng Object Storage bằng pre-signed URL, metadata đi MQTT. Bỏ bash sync script của POC.
- Backfill: giữ nguyên cờ truyền bù + sequence number (Interface Agreement); dữ liệu bù không tính realtime.
- Endpoint failover: `mqtt.{env}.<domain>`, `api.{env}.<domain>` TTL thấp, health-checked, trỏ region 2 khi DR.
- Tủ 4G phân tán: giữ mô hình VPN về FortiGate site. **Không** cho gateway nối thẳng cloud (bảo toàn ranh giới nghiệm thu tại broker site).

---

## 5. Network Segmentation (IT/OT/DMZ)

**Site (ánh xạ Purdue / IEC 62443):**

| Zone | VLAN | Thành phần | Conduit cho phép |
|---|---|---|---|
| Z0–2 (OT) | VLAN OT | PLC, tủ IoT, datalogger | → Z3: MQTT; đọc Modbus nội vùng |
| Z3 (Site ops) | VLAN server | IOC on-prem, edge EMQX, TSDB, AI server | → Z3.5 only |
| Z3.5 (DMZ) | VLAN DMZ (mới) | MQTT bridge, MediaMTX relay, sync | → cloud qua MPLS/IPsec only |
| Camera | VLAN camera | Camera, NVR | → Z3 (VMS); **không route Internet** |
| Z4 (IT) | VLAN office | Máy trạm văn phòng | Internet qua firewall policy |
| Mgmt | VLAN mgmt | iDRAC/iLO, FortiGate mgmt | ← bastion cloud qua tunnel |

- Deny-by-default giữa VLAN; egress whitelist theo FQDN (registry, cloud endpoints, NTP).
- **Cloud:** subnets `edge-ingest` / `app` / `data` / `mgmt`, security group deny-by-default; VKS NetworkPolicy default-deny per namespace, tenant namespaces không giao tiếp chéo.

---

## 6. Cloud Platform (VNPT Cloud)

- **Environments:** DEV / STG / PROD (bắt buộc theo Quy chế 2 đội). PROD VPC riêng; DEV+STG chung VPC tách subnet.
- **VKS PROD node pools:** `app-pool` (microservices, Keycloak, Temporal, Grafana), `data-pool` (NVMe cao IOPS: ClickHouse, EMQX, Loki/Mimir), `ingest-pool` (EMQX + Kafka consumers). GPU pool: chưa cần (AI inference ở edge).
- **Managed:** PostgreSQL HA (verify PostGIS), Redis, Kafka, Object Storage, LB, WAAP, Backup.
- **Self-host (Operator trên VKS):** EMQX (≥3 node), ClickHouse (Altinity operator, 2 replica + 3 Keeper), Keycloak, Temporal, LGTM, Vault.
- **Ingress:** LB L4 cho MQTT :8883 mTLS + VPN; LB L7 + WAAP chỉ cho Web/API HTTPS public. WAAP không đặt trước MQTT (L7 HTTP only).
- **Registry:** VNPT Container Registry (prod), GitLab registry (dev).

---

## 7. Data Plane (Compute / Storage / DB / Cache / Broker)

**Pipeline chuẩn:** `EMQX cloud → Kafka → Go ingest/normalize/validate → ClickHouse (telemetry, events) + PG (metadata, alarm lifecycle, audit, PostGIS) + Redis (last-value cache, session)`. Alarm path tách consumer riêng (KPI sự kiện ≤2s không bị bulk ingest ảnh hưởng).

- **Kafka topics theo domain, không theo tenant:** `telemetry.raw`, `events.alarm`, `commands.audit`…; partition key `{tenant}/{park}` (ordering per site, tránh topic explosion). Retention 3–7 ngày (replay window).
- **Schema:** JSON + JSON Schema registry trong Git (số hóa Interface Agreement); versioning qua Change Request.
- **ClickHouse:** ReplicatedMergeTree; TTL raw 30 ngày, aggregate 1 năm (đúng retention policy POC); database per tenant.
- **Retention & alerting thresholds:** giữ nguyên bảng POC (raw 30d / aggregate 1y / footage 6mo / audit 2y / logs 90d; ngưỡng CPU/RAM/disk/MQTT/API).
- **Capacity khởi điểm** (10 KCN, `[assumption — hiệu chỉnh theo số liệu ĐV3]`): 2.000–6.000 msg/s fleet đỉnh @ 30 KCN; VKS ~6 worker (4× 8vCPU/16GB + 2× 8vCPU/32GB NVMe 2TB); managed PG 2× 4vCPU/16GB HA; Kafka 3 broker; Redis 4GB.
- **Hoãn (YAGNI):** Spark, Flink, HDFS, Trino, Atlas, Airflow, MinIO, service mesh, Sparkplug B.

---

## 8. IoT Communication

- **Field:** Modbus RTU/TCP chuẩn hóa tại ECU-1051; OPC UA bật ở gateway cho PLC hỗ trợ (tùy site); BACnet/IP, DNP3 sẵn có ở gateway khi cần; 4–20mA/DI qua datalogger; EVN REST API (polling 15–30 phút); video RTSP/ONVIF tách luồng telemetry.
- **Topic standard toàn nền tảng:**
  - Uplink: `v1/{tenant}/{park}/{subsys}/{node}/telemetry|event|heartbeat`
  - Downlink: `v1/{tenant}/{park}/{subsys}/{node}/cmd` + `.../cmd/ack`
  - EMQX ACL theo cert CN `{tenant}:{park}:{gateway}` — chỉ pub/sub đúng prefix.
- **QoS:** telemetry QoS1; event/alarm QoS1 + dedup theo sequence; command QoS1 + **ack tầng ứng dụng** (idempotency key, timeout 5s) — không dựa QoS2.
- **Bản tin bắt buộc** (theo Interface Agreement): NTP timestamp, gateway ID, sequence number, cờ truyền bù, cờ chất lượng (tốt/nghi ngờ/lỗi); scale/quy đổi đơn vị MỘT lần duy nhất tại gateway.
- **Chữ ký/định danh tại gateway** (không tại PLC): ECU-1051 giữ private key, mTLS với broker. PLC chỉ làm ngưỡng cục bộ + fail-safe.
- **Điều khiển ngược qua cloud:** `Cloud API (2FA TOTP + RBAC + audit) → Kafka commands → EMQX cloud → bridge → EMQX edge → gateway → PLC`; whitelist đúng danh mục site (chiếu sáng, PTZ); phản hồi ≤5s; mở rộng danh mục qua Change Request.

---

## 9. Monitoring / Logging / Observability

- **Cloud:** LGTM trên VKS — Grafana + Mimir (metrics 13 tháng, multi-tenant) + Loki (logs 90 ngày) + Alertmanager.
- **Edge:** Grafana Agent (đã có trong thiết kế site) remote_write qua tunnel, external labels `{tenant, park, site}`.
- **Tracing:** OpenTelemetry trong Go services (ingest → Kafka → consumer → DB); synthetic probe per site đo KPI telemetry ≤5s end-to-end.
- **NOC fleet dashboard** (khác dashboard nghiệp vụ IOC): trạng thái tunnel primary/backup, bridge queue lag, gateway heartbeat, backfill backlog, cert expiry.
- **Alert routing:** Alertmanager → Telegram + email theo bảng mức P1–P4 (SLA phối hợp 2 đội); on-call schedule bằng Grafana OnCall.
- **SLO:** uptime 99.9% / API p95 <200ms / sync <60s / MQTT delivery 99.99% (giữ bảng POC), thêm burn-rate alerts.

---

## 10. Security

- **PKI private 2 tầng:** offline root CA + intermediate per env, vận hành bằng Vault PKI (self-host VKS). Device identity: cert per gateway (CN `{tenant}:{park}:{gw}`, hạn 1 năm, rotate trước hạn 90 ngày, tự động qua EST/SCEP nếu EdgeLink hỗ trợ — fallback rotation theo kỳ bảo trì 6 tháng). Revocation: CRL/OCSP tại EMQX. VNPT-CA giữ đúng vai trò ký số văn bản pháp lý.
- **Secrets:** Vault + External Secrets Operator; cấm secrets trong `.env`/manifest/Git plaintext; CI secrets từ Vault.
- **IAM:** Keycloak 1 realm platform, organization/group per tenant; OIDC SSO cho platform web, Grafana, GitLab, Temporal UI; **2FA TOTP bắt buộc cho role điều khiển ngược**; RBAC 3 nhóm Admin/Operator/Viewer per tenant; audit log đầy đủ (stream Kafka → ClickHouse, immutable).
- **Admin access:** bastion + ZTNA (FortiClient ZTNA hoặc WireGuard+SSO) — một cửa duy nhất cho quản trị site + cloud, session log tập trung. Không mở SSH/mgmt từ Internet.
- **Vá & scan:** Trivy trong CI (image + dependency); critical CVE ≤7 ngày (cloud), edge theo ring rollout.
- **Compliance:** dữ liệu tại VNPT Cloud VN (data residency ✓); PDPD NĐ 13/2023: footage/biển số = dữ liệu cá nhân → DPA với từng chủ đầu tư, retention đúng policy, masking biển số trên dashboard công khai.
- **Zero Trust roadmap:** năm 1 = device mTLS + ZTNA admin + network deny-by-default; service mesh để sau.

---

## 11. Backup & Disaster Recovery (D5)

| Thành phần | Cơ chế | RPO | Ghi chú |
|---|---|---|---|
| PostgreSQL | Managed replica async cross-region (fallback pgBackRest standby) | 5–15 phút | metadata/alarm/audit |
| ClickHouse | clickhouse-backup daily + Object Storage replication | ≤24h | telemetry RPO≈0 thực tế nhờ edge buffer 30d truyền bù |
| Object Storage | Cross-region replication | ~0 | footage/evidence |
| Kafka | Không replicate (transient) | — | consumer replay từ edge backfill |
| K8s state | Velero | 24h | |
| Keycloak/EMQX/Grafana | Config-as-code trong Git | ≈0 | realm export định kỳ |
| Edge site DB | Nightly dump → Object Storage per-site | 24h | chạy đêm, băng thông nhỏ |
| GitLab | Daily backup → Object Storage | 24h | |

- **Backup immutable:** bucket versioning + object lock, credential append-only tách khỏi credential vận hành (chống ransomware — kịch bản đã có trong DRP).
- **Restore test tự động hàng tháng** (ephemeral namespace, restore, checksum). **DR drill mỗi quý** trên STG — đo RTO thật, cập nhật runbook, gắn vào quy trình Gate/QA.
- **RTO tổng:** 1–2h (DNS failover + IaC dựng stack tại region 2). Retention backup: daily 30d / weekly 12w / monthly 12m (giữ POC).

---

## 12. CI/CD & Infrastructure as Code

- **GitLab self-host** (VKS/VServer, data residency) + runners trong subnet mgmt.
- **Argo CD** cho VKS: app-of-apps, project per env; auto-sync STG, manual gate PROD (khớp quy trình release + freeze 48h trước SIT/UAT của Quy chế 2 đội).
- **Terraform** cho mọi resource VNPT Cloud; state = GitLab-managed Terraform state (có locking). Không console-ops sau go-live.
- **Edge pipeline:** build → registry → release train theo **ring** (lab → canary site → fleet 25%/batch), Ansible-pull trên host Docker Compose; version pin per-site trong Git (= "cấu hình lưu kho có phiên bản" của Quy chế, được số hóa).
- **Simulator bản tin** (Go CLI, dùng JSON Schema registry): artifact chính thức cho DEV (DEV cấm nối thiết bị thật) + integration test.
- **Pipeline chuẩn:** lint/test → build → Trivy scan → push → DEV + integration test → STG → P2P/SIT theo quy trình 2 đội → manual approve → PROD.

---

## 13. Multi-tenancy & Scalability (D6)

**10–30 KCN (hiện tại):**
- Shared backend multi-tenant (tenant context từ JWT/topic) — **không** helm-install per tenant, **không** broker per tenant (bỏ hướng `deploy-tenant.sh` của POC).
- Isolation: PG RLS + schema per tenant; ClickHouse database per tenant; EMQX ACL; Kafka partition key; VKS NetworkPolicy.
- **Isolation test tự động trong CI:** tenant A không đọc được data tenant B (mọi tầng: API, DB, MQTT).
- Onboarding site = **Temporal workflow** zero-touch: tạo tenant/park → cấp cert → EMQX ACL → schema/DB → dashboard template → simulator smoke test → bàn giao G2. Mục tiêu ≤1 ngày cloud-side/site.
- **Device Registry:** bảng thiết bị + trạng thái + version + cert serial, đồng bộ từ tag list as-built (nguồn sự thật hiện có).

**100+ KCN (cell architecture — nền đặt sẵn từ bây giờ):**
- Mọi định danh routing mang `cell_id`. 1 cell = {VKS + EMQX + Kafka + CH + PG} phục vụ ~30–50 KCN.
- Global control plane: Keycloak, Device Registry, fleet mgmt, GitOps, observability tổng (Grafana đa datasource).
- Blast radius = 1 cell; site gán cell lúc onboard.

**1000 KCN (nguyên tắc):** nhiều cell theo region (bám 8 DC VNPT IDC), data locality per cell, global chỉ giữ identity + catalog + billing + cross-cell reporting; ops model "quản cell" thay vì "quản site". Không thiết kế chi tiết bây giờ.

---

## 14. Roadmap triển khai

| Phase | Thời gian | Nội dung chính | Exit criteria |
|---|---|---|---|
| **A — Landing zone** | 0–3 tháng | VPC/VKS/managed DB/Kafka; Vault + PKI; GitLab + Argo CD + Terraform; EMQX cloud + bridge ĐV3; LGTM; DMZ site ĐV3; bỏ Watchtower | ĐV3 telemetry lên cloud dashboard ≤5s; DEV/STG/PROD chạy; 0 secret plaintext |
| **B — Hardening** | 3–6 tháng | Warm standby region 2 + DR drill #1; backup immutable; onboarding Temporal + site blueprint; simulator; NOC dashboard; isolation test trong CI | Site #2 onboard ≤1 ngày cloud-side; DR drill RTO ≤2h; isolation test pass tự động |
| **C — Scale-out** | 6–18 tháng | Nhân bản site theo blueprint; capacity theo số liệu thật; Device Registry; cost tuning; đánh giá cell #2 khi >30 KCN | ≥10 KCN live; SLO 99.9% đo được; chi phí/site giảm theo scale |

**Chi phí thô** `[assumption — cần báo giá VNPT]`: cloud shared ~40–70tr/tháng (10 KCN) + warm standby ~10–20tr/tháng + MPLS ~3–8tr/site/tháng + FTTH backup ~1tr/site. Edge giữ BOM ĐV3.

---

## 15. Open Items (cần xác minh)

1. **[VNPT]** Multi-AZ trong 1 region? SLA managed PG/Kafka/Redis; managed PG có PostGIS + cross-region replica không?
2. **[VNPT]** Giá + khả năng cấp L3VPN/MPLS site→cloud tại các tỉnh có KCN mục tiêu.
3. **[Đo thực tế]** Message rate/dung lượng ĐV3 sau go-live → hiệu chỉnh capacity mục 7.
4. **[Kỹ thuật]** ECU-1051/EdgeLink hỗ trợ nạp/rotate cert tự động (EST/SCEP)? Nếu không → rotation theo kỳ bảo trì.
5. **[Sản phẩm]** IOC on-prem ĐV3 và Cloud Platform: 1 codebase 2 deployment target (giả định hiện tại) hay 2 sản phẩm?
6. **[Business]** SLA cam kết với chủ đầu tư; tenant nào yêu cầu cách ly DB cứng → chuyển tenant đó sang mode DB riêng.
7. **[Compliance]** DPA per chủ đầu tư + chính sách masking biển số (PDPD NĐ 13/2023).
