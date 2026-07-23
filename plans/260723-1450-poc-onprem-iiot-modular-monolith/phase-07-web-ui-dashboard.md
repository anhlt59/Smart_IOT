---
phase: 7
title: "Web UI Dashboard"
status: pending
priority: P1
effort: "8d"
dependencies: [4]
---

# Phase 7: Web UI Dashboard

## Overview
Web UI React cho operator: dashboard realtime, lịch sử, alarm, điều khiển, camera. Bắt đầu tuần 1 với mock từ OpenAPI — không chờ API xong.

## Requirements
- Functional: login; dashboard telemetry realtime (chart + bảng last-value); history chart (range picker); alarm list + ack/close + toast realtime; control panel (nút whitelist + trạng thái ack); camera grid live view.
- Non-functional: 50 user đồng thời; dashboard load <3s; layout responsive desktop-first (phòng điều khiển); tiếng Việt.

## Architecture
- Vite + React 18 + TypeScript; TanStack Query (server state) + TanStack Router; WS client tự viết (reconnect + resubscribe); chart: ECharts (time-series lớn, streaming tốt); UI: Tailwind + shadcn/ui.
- Types sinh từ `apps/backend/api/openapi.yaml` (openapi-typescript) — contract-first, đổi API là build fail.
- WS message → Query cache update (setQueryData) — 1 nguồn state, không duplicate store.
- Video: WHEP player (native WebRTC) + hls.js fallback.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/web/` (Vite app): `src/routes/{login,dashboard,history,alarms,control,cameras}.tsx`
- Create: `apps/web/src/lib/{api-client.ts,ws-client.ts,generated-types.ts}`
- Create: `apps/web/src/components/{realtime-chart,last-value-table,alarm-toast,command-button,camera-player}.tsx`
- Modify: `infra/edge/docker-compose.yml` (serve web build qua app-api static hoặc nginx container — chọn app-api static cho ít container)

## Implementation Steps
1. Tuần 1: scaffold + auth flow + layout shell + mock server từ OpenAPI (msw) — demo được UI khung.
2. Dashboard: last-value table nhóm theo subsys (4 phân hệ); realtime line chart (window 15 phút, downsample client).
3. History: range picker (1h/24h/7d/30d) → API bucket; export CSV client-side.
4. Alarms: bảng filter (severity, state, time), ack/close với confirm, toast khi WS alarm event, badge đếm alarm open.
5. Control: panel nút theo command_catalog (fetch từ API), confirm dialog, trạng thái pending→acked/timeout realtime, disable khi role=viewer.
6. Cameras: grid 2×2, click mở player WHEP (hls.js fallback), hiển thị offline state.
7. Tích hợp thật thay mock ngay khi endpoint sẵn (theo dõi qua OpenAPI diff).

## Success Criteria
- [ ] Cuối tuần 1: UI shell + login + dashboard mock chạy được (demo nội bộ)
- [ ] Telemetry xuất hiện trên chart ≤5s từ simulator publish (E2E)
- [ ] Alarm toast ≤2s; ack từ UI đổi state + audit
- [ ] Command button: bấm → thấy acked ≤5s; viewer không thấy nút control
- [ ] Camera live view hoạt động Chrome + Safari (WHEP/HLS)
- [ ] Build production serve từ app-api; load <3s trên LAN

## Risk Assessment
- 1 dev FE là bottleneck → contract-first + mock cho phép chạy độc lập 100%; Dev 5 hỗ trợ camera player tuần 3.
- ECharts streaming 2k msg/s làm đơ browser → chỉ render last-value + chart theo subscription chọn lọc (không subscribe all), throttle 1s/frame.
