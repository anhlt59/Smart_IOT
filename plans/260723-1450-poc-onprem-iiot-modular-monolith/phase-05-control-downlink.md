---
phase: 5
title: "Control Downlink"
status: pending
priority: P1
effort: "3d"
dependencies: [4]
---

# Phase 5: Control Downlink

## Overview
Điều khiển ngược an toàn: whitelist action + idempotency + MQTT QoS1 + app-level ack ≤5s + audit trail đầy đủ. Đây là phần KHÔNG được cắt góc (an toàn công nghiệp).

## Requirements
- Functional: POST command (operator+) → validate whitelist → publish `v1/{tenant}/{park}/{subsys}/{node}/cmd` QoS1 kèm idempotency key → nhận `cmd/ack` → update state → push WS. Timeout 5s → state `timeout`.
- Non-functional: mọi command có audit row TRƯỚC khi publish; idempotent (retry cùng key không tạo command mới); KHÔNG dựa QoS2.

## Architecture
- State machine: `pending → sent → acked | timeout | failed`. Ack listener chạy trong role worker (subscribe `v1/+/+/+/+/cmd/ack`).
- Whitelist = bảng `command_catalog` (subsys, node pattern, action, params schema) — seed đúng danh mục ĐV3: 9 lộ chiếu sáng + PTZ camera. Ngoài danh mục → 403, có audit.
- Idempotency key do client sinh (UUID); unique index; request trùng trả command hiện có.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/internal/control/service.go`, `apps/backend/internal/control/ack_listener.go`, `apps/backend/internal/api/handlers_commands.go`
- Create: `apps/backend/migrations/0007_commands.up.sql` (commands + command_catalog + unique idempotency_key)
- Modify: `apps/backend/cmd/simulator/main.go` (mode gateway: nhận cmd → trả ack sau delay configurable, mode no-ack để test timeout)
- Modify: `apps/backend/api/openapi.yaml`

## Implementation Steps
1. Migration + seed command_catalog (lighting_1..9 on/off, ptz_move camera params).
2. Service: transaction {insert command + audit} → publish MQTT → timer 5s (goroutine + context) → timeout nếu chưa ack.
3. Ack listener: match theo command id trong payload ack, validate gateway ID đúng node → update state + publish CommandState lên bus.
4. Endpoints: `POST /commands`, `GET /commands?device&state`, `GET /commands/{id}`.
5. WS đẩy `rt:command` để UI hiện trạng thái nút bấm realtime.
6. Tests: happy path, duplicate idempotency key, action ngoài whitelist, timeout, ack muộn sau timeout (ignore + log).

## Success Criteria
- [ ] Command hợp lệ: state `acked` ≤5s với simulator ack mode; UI thấy trạng thái đổi realtime
- [ ] Action ngoài whitelist → 403 + audit row
- [ ] Retry cùng idempotency key → trả command cũ, không publish lại
- [ ] Simulator no-ack mode → state `timeout` đúng 5s
- [ ] Audit trail đọc được: ai, lúc nào, lệnh gì, kết quả gì

## Risk Assessment
- Ack muộn sau timeout gây state nhảy lùi → state machine chỉ cho phép chuyển tiến; ack-sau-timeout ghi log + metric, không đổi state.
- Timer goroutine leak khi nhiều command → context cancel khi ack tới; giới hạn concurrent pending commands (100).
