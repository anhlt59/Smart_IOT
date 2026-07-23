# Project Roadmap — Industrial IoT Platform

**Phiên bản:** 1.0 · **Ngày:** 2026-07-22

---

## Roadmap triển khai (3 Phase)

| Phase | Thời gian | Mục tiêu chính | Exit Criteria | Ghi chú |
|---|---|---|---|---|
| **A — Landing zone** | 0–3 tháng | VPC/VKS setup, managed DB/Kafka, Vault PKI, GitLab+Argo CD+Terraform, EMQX cloud+bridge ĐV3, LGTM, DMZ ĐV3, remove Watchtower | ĐV3 telemetry lên cloud ≤5s; DEV/STG/PROD chạy; 0 secret plaintext (Vault PKI); Gate G1 pass | **Deliverable:** VKS cluster + cloud platform v0.1 + site ĐV3 bridge |
| **B — Hardening** | 3–6 tháng | Warm standby region 2, backup immutable, Temporal onboarding + site blueprint, simulator, NOC dashboard, isolation test tự động | Site #2 onboard ≤1 ngày cloud-side; DR drill RTO ≤2h + runbook; isolation test pass CI; Gate G2-G3 pass | **Deliverable:** Region 2 active + 2nd site production-ready |
| **C — Scale-out** | 6–18 tháng | Replicate site per blueprint, capacity tuning per số liệu thật, Device Registry, cost optimization, cell #2 evaluation (>30 KCN) | ≥10 KCN live; SLO 99.9% measured end-to-end; cost/site ↓ scaling curve; Gates G4-G6 pass | **Deliverable:** 10+ KCN production fleet, SLO verified, cost model mature |

---

## Timeline chi tiết — Giai đoạn A

| Tháng | Nội dung | Owner | Exit |
|---|---|---|---|
| **Tháng 1 (0–4 tuần)** | Setup VPC (VNPT), VKS cluster 3 master+6 worker, managed PG/Kafka/Redis, GitLab + runners, Terraform state, Vault PKI private root+intermediate | Cloud team | VKS cluster green, Terraform apply-able |
| **Tháng 1–2** | Argo CD app-of-apps, pipeline lint/test/build/scan (Trivy), registry (VNPT + GitLab), DEV/STG/PROD env separation | DevOps | Pipeline end-to-end working |
| **Tháng 2** | EMQX cloud 3-node cluster (managed or Operator), Kafka topic schema registry (Git), ClickHouse Altinity operator (2 replica + Keeper), Keycloak realm | Cloud team | Broker bridge testable |
| **Tháng 2–3** | Go ingest service (MQTT → normalize → Kafka), ClickHouse ingest consumer, PG schema + RLS (per tenant), Redis cache layer, LGTM stack (Grafana+Mimir+Loki+AM) | Backend team | Telemetry flow end-to-end testable |
| **Tháng 3 (parallel)** | DMZ site ĐV3: EMQX edge → bridge mTLS to cloud, MediaMTX setup, FortiGate IPsec backup test | Site IoT team | Site telemetry flowing to cloud, cloud dashboard shows ĐV3 data ≤5s |
| **Tháng 3** | Remove Watchtower from ĐV3, replace with Ansible-pull + site Git versioning, cert distribution via Vault | Ops team | Site ĐV3 fully self-managed |
| **Gate G1** | ✓ ĐV3 lên cloud ≤5s; ✓ DEV/STG/PROD chạy; ✓ 0 plaintext secret; ✓ Dr drill runbook v0.1 | QA + Ops | Approval → Phase B |

---

## Timeline — Giai đoạn B

| Tháng | Nội dung | Owner | Exit |
|---|---|---|---|
| **Tháng 4 (3–6 tuần)** | Region 2 (HCM) setup: PG replica async, Object Storage replication, IaC to spin up full stack | Cloud team | Region 2 ready for failover test |
| **Tháng 4–5** | Warm standby test: inject chaos → trigger DR → measure RTO actual; runbook v1.0; DR drill scheduled quarterly | QA + Ops | RTO measured ≤2h; runbook verified |
| **Tháng 5** | Temporal workflow onboarding: site registration, cert provisioning, schema creation, dashboard template, smoke test automation | Backend team | Onboarding <1 day cloud-side |
| **Tháng 5–6** | Site blueprint (Docker Compose templates, config per-site, as-built Git repo), simulator (bản tin test per Interface Agreement), integration test in CI | Backend + IoT team | Site #2 canary deployment |
| **Tháng 6** | NOC dashboard v1.0 (tunnel status, bridge lag, cert expiry, NOC team alerting), per-tenant dashboard (from ĐV3 data) | Frontend team | Ops can monitor fleet |
| **Tháng 6** | Isolation test in CI: verify tenant A ≠ B data (API, DB, MQTT) | QA | Test passing automatically |
| **Gate G2–G3** | ✓ Site #2 live (cloud-side ≤1d); ✓ DR RTO ≤2h measured; ✓ Isolation test pass; ✓ NOC dashboard shows ≥2 sites | Product | Approval → Phase C |

---

## Timeline — Giai đoạn C

| Tháng | Nội dung | Owner | Exit |
|---|---|---|---|
| **Tháng 7–9 (6–9 tuần)** | Replicate sites #3–#10 per blueprint; measure telemetry rate, storage growth, Kafka lag; cost per site trending down | Ops + Backend | 10 KCN cumulative |
| **Tháng 9–12** | SLO monitoring dashboard (burn-rate, uptime % per KCN), analyze failure modes, tune capacity (VKS/PG/Kafka/CH pools) | Platform team | SLO 99.9% verified (≥90 days baseline) |
| **Tháng 12–18** | Device Registry v1.0 (source-of-truth device list), cost model per site + tenant, start evaluating cell #2 arch when >30 KCN forecast | Product + Platform | Cost/site curve optimized; cell roadmap drafted |
| **Gate G4–G6** | ✓ 10+ KCN live; ✓ SLO 99.9% measured; ✓ Cost/site budget-aligned; ✓ Cell architecture roadmap approved | Board | Approval Phase D (scale to 100+) |

---

## 5 giai đoạn phần mềm (từ TechStack_Pipeline)

Hợp nhất 5 giai đoạn từ tài liệu TechStack_Pipeline (9 tháng):

| Giai đoạn | Nội dung | Sprint | Kết quả |
|---|---|---|---|
| **1 — Setup** | Dev env setup, team onboarding, stack proof-of-concept (Go Hello, EMQX test, ClickHouse DDL test) | Week 1–2 | Ready for sprint 2 |
| **2 — Ingest** | MQTT bridge, message normalization (Interface Agreement), Kafka producer, ClickHouse ingest, PG schema | Week 3–6 | Telemetry flow verified |
| **3 — API** | REST API v1 (CRUD telemetry/alarm/device), JWT auth, multi-tenant context, RLS test | Week 7–10 | API contract approved by IoT |
| **4 — UI** | Cloud web dashboard (React), Grafana dashboard, real-time chart (WebSocket or Server-Sent Events) | Week 11–16 | UI approved by stakeholder |
| **5 — Ops** | Helm/Argo deployment, monitoring (Prometheus/Grafana), backup automation, dr runbook, production rollout checklist | Week 17–26 | Production-ready |

---

## Gates (Quy chế 2 đội)

**6 gates từ IoT_Software_Team_Collaboration_Guidelines (ranh giới MQTT broker):**

| Gate | Milestone | Criteria | Owner |
|---|---|---|---|
| **G0** | Design review | ✓ Interface Agreement v1.0; ✓ tag list; ✓ bản tin spec | IoT + SW |
| **G1** | Phase A complete | ✓ ĐV3 telemetry ≤5s; ✓ cloud DEV/STG/PROD; ✓ 0 secret plaintext | SW (infra) |
| **G2** | Phase B complete (site #2) | ✓ Site #2 production; ✓ DR tested RTO ≤2h; ✓ Isolation pass | SW (platform) |
| **G3** | P2P test readiness | ✓ Simulator + integration test pass; ✓ SIT checklist sign-off | QA + IoT |
| **G4** | UAT readiness | ✓ ≥2 sites running; ✓ SLA verify; ✓ runbook tested | Ops + Product |
| **G5** | Go-live approval | ✓ ≥10 KCN staging; ✓ SLO 99.9% verified; ✓ disaster recovery drill passed | CTO + CISO |
| **G6** | Scale-out (cell #2) | ✓ Evaluate cell #2 when >30 KCN; ✓ cost model + roadmap | Product + Arch |

---

## Timeline thi công Đồng Văn III (Site 1)

**Từ Industrial_Park_Technical_Report (thực tế ~4 tháng):**

| Giai đoạn | Thời gian | Nội dung |
|---|---|---|
| **Thiết kế & lập kế hoạch** | Tuần 0–2 | Kiến trúc network (VLAN, firewall), server layout, đặt hàng hardware |
| **Chuẩn bị site** | Tuần 3–4 | Cable farm, server room setup, UPS + generator test, network commissioning |
| **Cài đặt hardware** | Tuần 5–8 | Cài server (R660/R760/DL380), NVR, switch, FortiGate, ECU-1051, ADAM-3600, camera |
| **Cấu hình network & OT** | Tuần 9–12 | VLAN (OT/IT/DMZ), FortiGate firewall policy, iDRAC/iLO, Modbus gateway test, camera ONVIF test |
| **Cloud integration & UAT** | Tuần 13–16 | EMQX bridge test, Docker Compose on-prem, telemetry flow verify, cloud dashboard, user UAT |

**Điểm kiểm tra:**
- Week 4: Network ready (VLAN, firewall, MPLS/IPsec up)
- Week 8: All hardware installed + iDRAC/iLO accessible
- Week 12: Modbus devices + camera detected → MQTT broker
- Week 16: Telemetry flowing to cloud, users can view dashboard

---

## Trạng thái hiện tại (2026-07-23)

✓ **Hoàn tất:** Thiết kế kiến trúc (7 quyết định D1-D7 đã chốt)
✓ **Hoàn tất:** PDR (yêu cầu chức năng + phi chức năng)
✓ **Hoàn tất:** Roadmap 3 phase
✓ **Hoàn tất:** Sơ đồ kiến trúc (diagrams)
✓ **Hoàn tất (2026-07-23):** POC Phase 1 foundation on-prem (Go monolith + Docker Compose, E2E verified)

⏳ **Chưa bắt đầu:** Phase A (landing zone) — sắp start tháng 8/2026 (after POC insights)

---

## Open Items

1. **[VNPT]** Confirmed SLA + price per managed service?
2. **[VNPT]** L3VPN/MPLS available tất cả tỉnh KCN mục tiêu?
3. **[Product]** IOC on-prem + Cloud = 1 codebase 2 target hay 2 products?
4. **[Tester]** Test environment (ITCO? internal lab?) cho integration test Phase 1?
5. **[Business]** SLA commitment vs 99.9% design target?
