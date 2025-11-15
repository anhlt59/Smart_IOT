# Product Development Requirements (PDR) — Industrial IoT Platform

**Phiên bản:** 1.0 · **Ngày:** 2026-07-22 · **Trạng thái:** Đã duyệt

---

## 1. Mục tiêu sản phẩm

Xây dựng **nền tảng quản lý vận hành tập trung (Industrial IoT Platform)** cho múi khu công nghiệp thông minh (KCN), cho phép:
- **Giám sát telemetry & event** từ 4 phân hệ (môi trường, an ninh-PCCC, năng lượng-nước, IOC) trên 10–30 KCN
- **Cảnh báo & báo cáo** theo ngưỡng kỹ thuật + quy định pháp luật (NĐ 40/2015, TT 10/2021)
- **Điều khiển ngược whitelist** (9 lộ chiếu sáng, PTZ camera) qua cloud với 2FA TOTP
- **Độc lập site** khi mất Internet (on-prem buffer 30 ngày, fail-safe PLC)
- **Scaling tới 100+ KCN** bằng cell architecture + shared multi-tenant

---

## 2. Stakeholders

| Vai trò | Mục tiêu | Input |
|---|---|---|
| **Chủ đầu tư KCN** | Quản lý tập trung, SLA 99.9%, compliance NĐ 40/2015 | Yêu cầu nghiệp vụ, SLA hợp đồng |
| **Đội IOT (Mạnh Networks)** | Dữ liệu sạch qua chuẩn Interface Agreement (IA) | Tag list, gateway config, IA versioning |
| **Đội Phần mềm (Smart IoT)** | API stable, cloud infrastructure, roadmap 9 tháng | Spec, tech stack D2, gate G0-G6 |
| **Đội vận hành IOC on-prem** | Monitoring local, failover tự động, easy ops | Dashboard on-prem, runbook |
| **VNPT (Cloud provider)** | Triển khai VKS + managed services | VPC, Kafka, PG, Redis, MPLS, Object Storage |

---

## 3. Phạm vi (Đồng Văn III — Site 1)

**4 phân hệ:**
1. **Môi trường:** CO₂, độ ẩm, nhiệt độ từ 9× ECU-1051 + cảm biến Modbus RTU/TCP
2. **An ninh-PCCC:** Camera ONVIF (30 stream), cảnh báo chuyển động AI, sự kiện cửa
3. **Năng lượng-nước:** Power meter (kWh, kVAR), flow meter, nhiệt độ tựa sưởi, UPS status
4. **IOC on-prem:** IOC web dashboard, SCADA local, archiving 30 ngày

**Hardware cố định (D1):** 2× Dell R660xs (app), 1× R760xs (data), 1× DL380 GPU (AI), 4 tủ IoT ECU-1051, ADAM-3600 datalogger, 2× Jetson Orin AI Box, NVR, UPS, FortiGate 80F.

---

## 4. Yêu cầu chức năng (Functional Requirements)

### Cloud Platform
1. **Multi-site dashboard** — xem telemetry 4 phân hệ tất cả KCN (chart, table, map)
2. **Alarm management** — cảnh báo khi vượt ngưỡng, ack/close, escalation Telegram/email
3. **Historical data** — Query telemetry/event 30 ngày raw + 1 năm aggregate (ClickHouse)
4. **API REST** — CRUD telemetry, alarm, device, report (multi-tenant JWT)
5. **Remote control** — downlink command (whitelist PTZ, chiếu sáng), ack tầng ứng dụng
6. **Reporting** — PDF monthly: avg/min/max per KCN + compliance NĐ 40/2015
7. **User mgmt** — Keycloak OIDC, 3 role per tenant (Admin/Operator/Viewer), 2FA TOTP cho control

### On-Premise Platform
1. **IOC local dashboard** — tương tự cloud, phục vụ local LAN (offline-first)
2. **MQTT broker** — EMQX open-source, bridge tới cloud qua mTLS
3. **Data buffer** — 30 ngày telemetry/event trên local PG + TSDB (truyền bù khi cloud up)
4. **Fail-safe** — PLC cục bộ giữ ngưỡng độc lập (NĐ 40/2015), không depend cloud
5. **Gateway sync** — Ansible-pull per-site từ Git (version pin), KHÔNG Watchtower

### Shared
1. **Event streaming** — Kafka topic per domain, partition key `{tenant}/{park}`
2. **Multi-tenant isolation** — PG RLS, EMQX ACL per cert CN, API tenant context
3. **Monitoring** — Grafana dashboard (NOC + per-tenant), Prometheus metrics, Loki logs

---

## 5. Yêu cầu phi chức năng (Non-Functional Requirements)

| Yêu cầu | Target | Ghi chú |
|---|---|---|
| **Uptime (SLO)** | 99.9% | cloud warm standby; edge tự trị khi cloud down |
| **Telemetry latency** | ≤5s end-to-end | edge → cloud, KPI đo qua synthetic probe |
| **Event latency** | ≤2s | sự kiện alarm (không ảnh hưởng bulk ingest) |
| **Command response** | ≤5s | cloud → edge → device, ack tầng app |
| **Data retention** | 30d raw / 1y agg | ClickHouse TTL + archival |
| **Backup RPO** | 5–15 phút | PG async replica cross-region |
| **DR RTO** | 1–2h | warm standby region 2, IaC dựng stack |
| **Scale** | 10–30 KCN | 2000–6000 msg/s fleet đỉnh; cell-ready 100+ |
| **API p95** | <200ms | ingest + query ClickHouse |
| **Concurrency** | 10 simultaneous users cloud + 50 on-prem local | baseline ĐV3 |
| **Security** | mTLS device, OIDC user, 2FA TOTP control, RLS data isolation | compliance PDPD NĐ 13/2023 |

---

## 6. Ràng buộc (Constraints)

1. **Cloud provider:** VNPT Cloud VN (data residency ✓, MPLS peering)
2. **Edge hardware:** Cố định ĐV3 (BOM không đổi sau go-live)
3. **On-prem runtime:** Docker Compose (D7 sticky) → KHÔNG K8s/K3s tại site
4. **Tech stack:** Go/Gin, EMQX, Kafka, ClickHouse, PostgreSQL, Redis, Keycloak, Temporal (D2 sticky)
5. **Connectivity:** VNPT MPLS/L3VPN primary + Internet IPsec backup (FortiGate SD-WAN)
6. **Compliance:** NĐ 40/2015 (môi trường), TT 10/2021 (datalogger), PDPD NĐ 13/2023 (privacy), VNPT Cloud data residency
7. **Roadmap:** Phase A (0–3 tháng) landing zone → B (3–6) hardening → C (6–18) scale-out (gates G0-G6)

---

## 7. Interface Agreement

**Ranh giới nghiệm thu tại MQTT broker (edge & cloud)** per Quy chế 2 đội:
- Đội IoT: PLC → gateway MQTT (EMQX edge broker), topic per Interface Agreement v1.0
- Đội Phần mềm: EMQX edge → EMQX cloud (bridge), EMQX cloud → backend services
- **Bản tin bắt buộc:** timestamp NTP, gateway ID, sequence, backfill flag, quality flag; scale/convert MỘT lần duy nhất tại gateway
- **Topic standard:** `v1/{tenant}/{park}/{subsys}/{node}/telemetry|event|heartbeat` (uplink), `v1/{tenant}/{park}/{subsys}/{node}/cmd` (downlink)
- **QoS:** telemetry QoS1, event QoS1 + dedup, command QoS1 + app ack

---

## 8. Success Criteria

- ✓ ĐV3 telemetry tới cloud dashboard ≤5s trong Phase A (exit gate)
- ✓ Site #2 onboard ≤1 ngày cloud-side trong Phase B
- ✓ DR drill RTO ≤2h + runbook verified hàng quý
- ✓ SLO 99.9% uptime đo được end-to-end
- ✓ 0 secret plaintext (Vault PKI, External Secrets)
- ✓ Isolation test tự động: tenant A ≠ tenant B data (mọi tầng)
- ✓ ≥10 KCN live end-of Phase C

---

## 9. Open Questions

1. **[VNPT]** Multi-AZ trong 1 region HN? SLA managed PG/Kafka/Redis?
2. **[Đo]** Message rate ĐV3 thực tế (đang +dùng POC)
3. **[Product]** IOC on-prem + Cloud Platform = 1 codebase 2 target hay 2 sản phẩm?
4. **[Business]** SLA cam kết hợp đồng vs 99.9% design target?
