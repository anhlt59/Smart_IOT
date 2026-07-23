// Package events defines the cross-module event contract of the modular
// monolith: typed payloads, channel names, and an EventBus that fans out
// in-process (hot path within one role) and bridges roles via Redis pub/sub.
//
// Contract consumers: ingest publishes TelemetryPoint, rules publishes
// AlarmEvent, control publishes CommandState, the API WebSocket hub
// subscribes to all three.
package events

import "time"

// Channel names shared between roles. The API role subscribes to these via
// Redis; within one process, delivery is direct (no Redis round-trip).
const (
	ChannelTelemetry = "rt:telemetry"
	ChannelAlarm     = "rt:alarm"
	ChannelCommand   = "rt:command"
)

// TelemetryPoint is one normalized measurement after ingest decode/validate.
// Field semantics follow the Interface Agreement: NTP timestamp, gateway ID,
// sequence number, backfill flag, quality flag are mandatory on the wire.
type TelemetryPoint struct {
	DeviceID  string    `json:"device_id"`
	GatewayID string    `json:"gateway_id"`
	Subsys    string    `json:"subsys"`
	Node      string    `json:"node"`
	Metric    string    `json:"metric"`
	Value     float64   `json:"value"`
	Quality   string    `json:"quality"`  // good|bad|uncertain (IA quality flag)
	Backfill  bool      `json:"backfill"` // true = replayed from gateway buffer, excluded from realtime KPI
	Seq       uint64    `json:"seq"`
	Ts        time.Time `json:"ts"` // device-side NTP timestamp
}

// AlarmState is the alarm lifecycle state machine.
type AlarmState string

const (
	AlarmOpen   AlarmState = "open"
	AlarmAcked  AlarmState = "acked"
	AlarmClosed AlarmState = "closed"
)

// AlarmEvent is emitted on every alarm state transition.
type AlarmEvent struct {
	AlarmID  int64      `json:"alarm_id"`
	RuleID   int64      `json:"rule_id"`
	DeviceID string     `json:"device_id"`
	Metric   string     `json:"metric"`
	Severity string     `json:"severity"` // info|warning|critical
	State    AlarmState `json:"state"`
	Value    float64    `json:"value"` // measurement that triggered the transition
	Ts       time.Time  `json:"ts"`
}

// CommandStatus is the downlink command lifecycle.
type CommandStatus string

const (
	CommandPending  CommandStatus = "pending"
	CommandSent     CommandStatus = "sent"
	CommandAcked    CommandStatus = "acked"
	CommandFailed   CommandStatus = "failed"
	CommandTimedOut CommandStatus = "timeout"
)

// CommandState is emitted on every command state transition so the UI can
// show button state in realtime.
type CommandState struct {
	CommandID      string        `json:"command_id"`
	DeviceID       string        `json:"device_id"`
	Command        string        `json:"command"` // whitelist catalog entry, e.g. lighting_1_on
	Status         CommandStatus `json:"status"`
	IdempotencyKey string        `json:"idempotency_key"`
	Actor          string        `json:"actor"` // username that issued the command (audit trail)
	Detail         string        `json:"detail,omitempty"`
	Ts             time.Time     `json:"ts"`
}
