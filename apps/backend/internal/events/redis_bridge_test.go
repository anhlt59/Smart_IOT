package events

import (
	"context"
	"encoding/json"
	"log/slog"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
)

func newTestRedis(t *testing.T) *redis.Client {
	t.Helper()
	mr := miniredis.RunT(t)
	return redis.NewClient(&redis.Options{Addr: mr.Addr()})
}

func TestRedisBusBridgesBetweenProcesses(t *testing.T) {
	rdb := newTestRedis(t)

	// Two buses on one Redis simulate the worker and api processes.
	worker := NewRedisBus(rdb, slog.Default())
	defer worker.Close()
	api := NewRedisBus(rdb, slog.Default())
	defer api.Close()

	got := make(chan []byte, 1)
	if _, err := api.Subscribe(ChannelAlarm, func(_ context.Context, p []byte) { got <- p }); err != nil {
		t.Fatal(err)
	}

	alarm := AlarmEvent{AlarmID: 42, DeviceID: "dev-9", Severity: "critical", State: AlarmOpen}
	// Redis pub/sub drops messages published before SUBSCRIBE settles, so
	// retry until the api-side bus observes one delivery.
	deadline := time.After(2 * time.Second)
	for {
		if err := worker.Publish(context.Background(), ChannelAlarm, alarm); err != nil {
			t.Fatal(err)
		}
		select {
		case p := <-got:
			var decoded AlarmEvent
			if err := json.Unmarshal(p, &decoded); err != nil {
				t.Fatal(err)
			}
			if decoded.AlarmID != alarm.AlarmID || decoded.State != alarm.State {
				t.Errorf("decoded %+v, want %+v", decoded, alarm)
			}
			return
		case <-deadline:
			t.Fatal("timed out waiting for bridged event")
		case <-time.After(50 * time.Millisecond):
		}
	}
}

func TestRedisBusDropsOwnEcho(t *testing.T) {
	rdb := newTestRedis(t)

	bus := NewRedisBus(rdb, slog.Default())
	defer bus.Close()

	got := make(chan []byte, 4)
	if _, err := bus.Subscribe(ChannelCommand, func(_ context.Context, p []byte) { got <- p }); err != nil {
		t.Fatal(err)
	}
	// Give the Redis SUBSCRIBE time to settle so the echo would arrive.
	time.Sleep(100 * time.Millisecond)

	if err := bus.Publish(context.Background(), ChannelCommand, CommandState{CommandID: "c1"}); err != nil {
		t.Fatal(err)
	}

	// Exactly one delivery: the local dispatch. The Redis echo is dropped.
	waitFor(t, got)
	select {
	case <-got:
		t.Error("received duplicate delivery via Redis echo")
	case <-time.After(300 * time.Millisecond):
	}
}

func TestRedisBusDropsMalformedBridgeMessage(t *testing.T) {
	rdb := newTestRedis(t)

	bus := NewRedisBus(rdb, slog.Default())
	defer bus.Close()

	got := make(chan []byte, 1)
	if _, err := bus.Subscribe(ChannelTelemetry, func(_ context.Context, p []byte) { got <- p }); err != nil {
		t.Fatal(err)
	}
	time.Sleep(100 * time.Millisecond)

	if err := rdb.Publish(context.Background(), ChannelTelemetry, "not-json").Err(); err != nil {
		t.Fatal(err)
	}

	select {
	case <-got:
		t.Error("malformed message was delivered")
	case <-time.After(300 * time.Millisecond):
	}
}
