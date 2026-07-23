---
phase: 6
title: "Camera Integration"
status: pending
priority: P2
effort: "4d"
dependencies: [1, 2]
---

# Phase 6: Camera Integration

## Overview
Camera live view trong web UI qua MediaMTX (RTSP → WebRTC/HLS) + AI event từ Jetson box đi qua pipeline event chuẩn. KHÔNG build VMS/recording — NVR sẵn có đảm nhiệm.

## Requirements
- Functional: camera registry; API trả stream URL; web UI xem live; AI event (motion/intrusion) thành alarm hiển thị + notification.
- Non-functional: latency live view <2s (WebRTC) trên LAN; giới hạn concurrent stream (config, default 8); camera down hiển thị trạng thái offline.

## Architecture
- MediaMTX pull RTSP từ camera/NVR → serve WebRTC (WHEP) primary + HLS fallback. App KHÔNG proxy video — chỉ trả URL + trạng thái (path status từ MediaMTX API `:9997`).
- AI event: Jetson publish `v1/{tenant}/{park}/security/{node}/event` (IA fields + event_type, camera_id, snapshot ref) → ingest pipeline có sẵn → rule "event security = alarm" (Phase 3 engine, rule type event-passthrough).
- POC không có camera thật khi dev → ffmpeg test source hoặc MediaMTX synthetic stream; simulator thêm mode AI event.

## Related Code Files
<!-- Updated: Validation Session 1 - cấu trúc code: apps/backend + apps/web + infra/edge + deploy/scripts (user recommend 15:19) -->
- Create: `apps/backend/internal/camera/registry.go`, `apps/backend/internal/camera/mediamtx_client.go`, `apps/backend/internal/api/handlers_cameras.go`
- Create: `apps/backend/migrations/0008_cameras.up.sql` (cameras: id, name, location, rtsp_url, mediamtx_path, enabled)
- Modify: `infra/edge/mediamtx/mediamtx.yml` (paths per camera, WebRTC/HLS enable, auth read token)
- Modify: `apps/backend/cmd/simulator/main.go` (mode ai-event), `apps/backend/api/openapi.yaml`

## Implementation Steps
1. Migration + seed 2–4 camera (test source khi dev).
2. MediaMTX config: path template `cam_{id}`, sourceOnDemand true (tiết kiệm băng thông), WebRTC + HLS enable.
3. `mediamtx_client`: gọi API v3 lấy path status (ready, readers) → camera online/offline + đếm concurrent.
4. Endpoints: `GET /cameras` (+status), `GET /cameras/{id}/stream` → `{whep_url, hls_url}`; enforce max concurrent (429 khi vượt).
5. AI event mapping: event_type → severity (intrusion=critical, motion=warning); snapshot ref lưu như URL metadata (không lưu binary).
6. E2E: ffmpeg RTSP test source → MediaMTX → WHEP xem được từ browser; simulator ai-event → alarm + Telegram.

## Success Criteria
- [ ] Live view WebRTC <2s latency trên LAN, HLS fallback hoạt động (Safari)
- [ ] Camera nguồn chết → API báo offline ≤30s, UI hiện trạng thái
- [ ] AI event từ simulator → alarm record + WS push + Telegram ≤2s
- [ ] Concurrent stream thứ 9 bị 429 (limit 8)
- [ ] Camera thật (nếu có tại lab) pull được qua RTSP

## Risk Assessment
- WebRTC qua network phức tạp (NAT) → demo trên LAN (đúng bối cảnh on-prem); HLS fallback luôn sẵn.
- Codec camera không tương thích browser (H.265) → MediaMTX không transcode; yêu cầu camera output H.264 hoặc dùng NVR substream — kiểm tra NGÀY 1 của phase với camera thật.
