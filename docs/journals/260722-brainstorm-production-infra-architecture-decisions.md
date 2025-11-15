# Brainstorm: Production Infrastructure Architecture — Hybrid VNPT Cloud + Edge

**Date:** 2026-07-22 14:57  
**Severity:** High  
**Component:** Infrastructure / Cloud / Hybrid Connectivity  
**Status:** Resolved (6 decisions locked, 7 open items remain)

## What Happened

Session brainstorm (skill `/brainstorm`) phân tích kiến trúc hạ tầng production cho nền tảng Industrial IoT quản lý 10–30 KCN với mô hình hybrid: edge on-premise tự trị (Đồng Văn III) + cloud VNPT multi-tenant. Đầu ra: [brainstorm report](../plans/reports/brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md) + [docs/system-architecture.md v1.0](../system-architecture.md). User chốt 6 quyết định chính.

## The Brutal Truth

POC hiện tại **không phải production-ready**. Stack POC (Mosquitto/TimescaleDB/Watchtower) khác target stack (EMQX/ClickHouse/Keycloak/Temporal). Docs tồn tại **gaps nghiêm trọng**: không có PKI lifecycle, secrets plaintext, Watchtower auto-update trong OT là rủi ro cao, POC deploy per-tenant DB sẽ nổ chi phí vận hành. Chưa có DMZ, chưa quy hoạch VPC/AZ VNPT, node pool strategy chưa rõ.

## Technical Details

**6 Quyết định chốt:**
- D1: Edge cố định theo Đồng Văn III (chỉ software/ops intervention)
- D2: Tech stack đích Go + EMQX + Kafka + ClickHouse + PG + Redis + Keycloak + Temporal
- D3: Thiết kế cho 10–30 KCN, không khóa lối lên 100+
- D4: Connectivity VNPT MPLS/L3VPN primary + Internet IPsec backup (SD-WAN failover)
- D5: DR warm standby region 2 (HN↔HCM, RPO 5–15ph, RTO 1–2h)
- D6: Tenancy shared cluster + PG RLS + EMQX ACL + cell_id routing identity

**Verified qua web:** VNPT VKS/managed PG/Kafka/Redis/Object Storage; VNPT 8 DC (6 Tier III) → multi-region DR khả thi. EMQX/ClickHouse/Keycloak/Temporal không managed → self-host VKS.

## What We Tried

Alternatives xem xét: active-active DR (chi phí quá cao, complexity), full-mesh SD-WAN (vận hành phức tạp), self-host toàn bộ (DevOps overhead). Chốt: managed-first (stateless dùng managed; stateful + custom dùng Operator trên VKS).

## Root Cause Analysis

POC tập trung vào quickstart/proof-of-concept, không xem xét production concerns (HA, security, observability, cost). Thiếu sự coordinate giữa network (VNPT MPLS), platform (K8s/multi-tenant), ops (GitOps vs Watchtower). Chưa có "Site Blueprint" code = khó nhân bản 30 site.

## Lessons Learned

**YAGNI critical:** hoãn Spark/Flink/Trino/Airflow/MinIO/service mesh. **Tenancy-first design:** shared cluster + namespace/RLS từ phase 1 saves replatforming. **Edge-first autonomy:** gateway buffer 30d + fail-safe PLC → cloud chỉ cần warm standby, không cần active-active. **Config-as-code ngay từ đầu:** chưa có GitOps ring rollout (bỏ Watchtower, dùng Argo CD agent).

## Next Steps

**Immediate (before phase 2 design):**
1. Verify VNPT multi-AZ/SLA/PostGIS support PG managed
2. Verify VNPT MPLS pricing/lead time
3. Message rate test thực tế Đồng Văn III (design 1000 msg/s spike)
4. Est. SCEP/EST trên ECU-1051 cho mTLS cert rotation
5. Finalize: 1 vs 2 codebase (edge + cloud)
6. Define SLA business (KPI telemetry ≤5s, gateway availability ≥99.5%)
7. Verify PDPD compliance + data residency VNPT

**Deliverables pending:** Site Blueprint repo (phase 2), GitOps ring strategy, PKI lifecycle plan, DMZ design ĐV3.

---

**References:** [Brainstorm Report](../plans/reports/brainstorm-260722-1457-production-infra-architecture-vnpt-cloud-hybrid-report.md) | [System Architecture v1.0](../system-architecture.md)
