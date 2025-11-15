# Architecture Review — Industrial IoT Platform (2026-07-22)

**Phạm vi:** toàn bộ `docs/` (5 tài liệu chính, 2 PDF, 2 tài liệu tham chiếu nặng, 3 sơ đồ draw.io) + README, journal, brainstorm report.
**Vai trò review:** Principal Solution/Infrastructure Architect · Industrial IoT Architect · Senior Technical Reviewer.
**Ràng buộc tuân thủ:** review chỉ phân tích và đề xuất — **không sửa tài liệu, không đảo ngược quyết định sticky D1–D7**. Các phát hiện chạm quyết định của user được đánh dấu `[USER-DECISION]` và trình user. Nhận định dựa trên kiến thức ngoài tài liệu đánh dấu `[external — cần verify]`.

---

## Cấu trúc bộ review

| File | Nội dung |
|---|---|
| [`document-summary.md`](./document-summary.md) | 15 tài liệu đã đọc, mục đích từng tài liệu, 7 điểm trùng lặp/chồng chéo |
| [`architecture-review.md`](./architecture-review.md) | Đánh giá 12 lĩnh vực (overall → infrastructure): điểm mạnh/yếu/thiếu/rủi ro + bảng 14 rủi ro AR-01…AR-14 |
| [`consistency-review.md`](./consistency-review.md) | 18 điểm không nhất quán C-01…C-18 + danh sách các điểm ĐÃ nhất quán tốt |
| [`gap-analysis.md`](./gap-analysis.md) | 24 gap G-01…G-24 + 13 mục Missing Information M-01…M-13 |
| [`recommendations.md`](./recommendations.md) | 28 đề xuất R-01…R-28 xếp Critical/High/Medium/Low, kèm vấn đề–ảnh hưởng–giải pháp |

---

## Đánh giá tổng quan

**Kết luận chung:** bộ tài liệu ở mức **tốt so với giai đoạn thiết kế** — lõi kiến trúc (D1–D7, nguyên tắc, data plane, security, DR posture) chặt chẽ, có trace quyết định, nhất quán cao giữa system-architecture ↔ brainstorm ↔ diagrams, và trung thực về giả định (`[assumption]`). Vấn đề tập trung ở: (1) hai tuyên bố kỹ thuật chưa có thiết kế đỡ (RPO telemetry, EMQX→Kafka), (2) tài liệu quy trình xung đột nhau (gates, 5 giai đoạn), (3) PDR sai số liệu, (4) scope bị drop im lặng khỏi tài liệu nguồn.

| Lĩnh vực | Đánh giá | Ghi chú ngắn |
|---|---|---|
| Overall Architecture | 🟢 Tốt | Nguyên tắc chặt, trace tốt; drift đếm quyết định (C-03) |
| On-Premise | 🟡 Khá | D7 hợp lý; data host SPOF chưa có defined behavior (AR-04) |
| Cloud | 🟡 Khá | Landing zone rõ; EMQX→Kafka chưa chốt (AR-02 Critical) |
| Hybrid Connectivity | 🟢 Tốt | D4 vững; thiếu spec failover bridge + test định kỳ |
| Network Design | 🟡 Khá | Zoning IEC 62443 tốt; thiếu IP/VLAN plan 30 site (AR-07) |
| Security | 🟢 Tốt | PKI/IAM/secrets đầy đủ; thiếu threat model + security IR (AR-05/06) |
| High Availability | 🟡 Khá | Tier hóa đúng; phụ thuộc multi-AZ chưa verify (AR-03) |
| Disaster Recovery | 🟡 Khá | Immutable + drill tốt; RPO telemetry tuyên bố chưa có cơ chế (AR-01 Critical) |
| Scalability | 🟢 Tốt | Shared multi-tenant + cell-ready + isolation test CI |
| Observability | 🟢 Tốt | LGTM + synthetic probe KPI ≤5s; agent EOL cần thay (AR-10) |
| CI/CD | 🟢 Tốt | GitOps + ring rollout + simulator; thiếu rollback spec |
| Infrastructure | 🟡 Khá | IaC kỷ luật; cost/quota/provider VNPT chưa verify |

---

## Top findings (đọc nhanh 2 phút)

### Critical — 4

1. **AR-01 / R-01:** "Telemetry RPO≈0 nhờ edge buffer" chưa có cơ chế kỹ thuật — store-and-forward không truyền lại dữ liệu đã ACK bị mất do DR. RPO thực ≤24h. Cần thiết kế replay-on-request (không đổi D5).
2. **AR-02 / R-03:** Pipeline `EMQX → Kafka` không nêu thành phần thực hiện; `[external]` Kafka integration là EMQX Enterprise. Chọn: license Enterprise hoặc Go ingest consume MQTT → produce Kafka (khuyến nghị). Phase A blocker.
3. **C-01 / R-02:** Roadmap định nghĩa lại gates G0–G6 khác hoàn toàn Quy chế 2 đội (tài liệu có chữ ký) — cùng nhãn 2 nghĩa, nguy cơ nhầm lẫn nghiệm thu.
4. **C-04 / R-04:** PDR (spec chính thức) sai số liệu: 4 tủ IoT (đúng 9), cảm biến CO₂ (không tồn tại), 50 user on-prem (giới hạn nền tảng 10), 30 stream (đúng 32 camera).

### High — nổi bật

- **C-02 / R-05 `[USER-DECISION]`:** Mobile App, GIS 3D/Digital Twin, voice control, dynamic QR bị drop khỏi PDR/roadmap không ghi chú — cần user quyết định scope, không tự cắt.
- **G-02 / R-06:** Interface Agreement v1.0 + JSON Schema registry được mọi thứ tham chiếu nhưng chưa tồn tại trong repo.
- **AR-03 / R-07:** 5 câu hỏi VNPT (multi-AZ, PostGIS, MPLS, quota region 2, Terraform provider) chặn thiết kế chi tiết — chưa có deadline/owner.
- **G-07 / R-11:** Luồng báo cáo quan trắc về Sở TN&MT (TT 10/2021) chưa được thiết kế/phân trách nhiệm ở bất kỳ tài liệu nào.
- **AR-07 / R-09:** Chưa có IP/VLAN addressing plan — phải chốt trước site #2.

### Điểm mạnh đáng ghi nhận

- Edge tự trị → chiết khấu HA/DR cloud: lập luận nhất quán xuyên suốt, đúng bản chất IIoT.
- Bỏ Watchtower + ring rollout + site blueprint: xử lý đúng rủi ro OT lớn nhất.
- Isolation test tự động trong CI + simulator bản tin là artifact chính thức: hiếm thấy ở giai đoạn design.
- Immutable backup + restore test hàng tháng + DR drill quý gắn vào gates.
- Deployment model (Docker Compose on-prem / VKS cloud) nhất quán tuyệt đối trên mọi tài liệu.

---

## Thống kê phát hiện

| Mức | Architecture (AR) | Consistency (C) | Gap (G) | Recommendations (R) |
|---|---|---|---|---|
| Critical | 2 | — | 1 | 4 |
| High | 6 | 4 | 7 | 7 |
| Medium | 6 | 7 | 11 | 9 |
| Low | — | 7 | 5 | 8 |

**Missing Information:** 13 mục (M-01…M-13) cần VNPT / đo thực tế / user / bảng khối lượng gốc trả lời — chi tiết tại `gap-analysis.md` §3.

---

## Đề xuất trình tự xử lý

1. **Tuần này:** R-04 (sửa PDR), R-02 (gates), R-07 (gửi RFI VNPT) — chi phí thấp, chặn hiểu nhầm.
2. **Trước Phase A kickoff (tháng 8):** R-03 (EMQX→Kafka), R-05 `[USER-DECISION]` (scope), R-06 (Interface Agreement), R-08 (crypto standards tối thiểu).
3. **Trong Phase A:** R-01 (thiết kế replay DR), R-09, R-10, R-11, R-13, R-17.
4. **Trước Phase B:** nhóm Medium còn lại (R-12, R-14→R-20).

---

*Review thực hiện theo quy tắc `review-audit-self-decision.md`: audit là input cho user, không phải lệnh; mọi phát hiện chạm quyết định đã chốt chỉ ghi trạng thái và trình user.*
