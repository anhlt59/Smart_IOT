package events

import (
	"context"
	"encoding/json"
	"log/slog"
	"testing"
	"time"
)

func waitFor(t *testing.T, ch <-chan []byte) []byte {
	t.Helper()
	select {
	case p := <-ch:
		return p
	case <-time.After(2 * time.Second):
		t.Fatal("timed out waiting for event delivery")
		return nil
	}
}

func TestInProcessBusDeliversToAllSubscribers(t *testing.T) {
	bus := NewInProcessBus(slog.Default())
	defer bus.Close()

	got1 := make(chan []byte, 1)
	got2 := make(chan []byte, 1)
	if _, err := bus.Subscribe(ChannelTelemetry, func(_ context.Context, p []byte) { got1 <- p }); err != nil {
		t.Fatal(err)
	}
	if _, err := bus.Subscribe(ChannelTelemetry, func(_ context.Context, p []byte) { got2 <- p }); err != nil {
		t.Fatal(err)
	}

	point := TelemetryPoint{DeviceID: "dev-1", Metric: "ph", Value: 7.2, Quality: "good", Ts: time.Now().UTC()}
	if err := bus.Publish(context.Background(), ChannelTelemetry, point); err != nil {
		t.Fatal(err)
	}

	for _, ch := range []<-chan []byte{got1, got2} {
		var decoded TelemetryPoint
		if err := json.Unmarshal(waitFor(t, ch), &decoded); err != nil {
			t.Fatal(err)
		}
		if decoded.DeviceID != point.DeviceID || decoded.Value != point.Value {
			t.Errorf("decoded %+v, want %+v", decoded, point)
		}
	}
}

func TestInProcessBusDeliversInPublishOrder(t *testing.T) {
	bus := NewInProcessBus(slog.Default())
	defer bus.Close()

	const n = 500
	got := make(chan uint64, n)
	if _, err := bus.Subscribe(ChannelTelemetry, func(_ context.Context, p []byte) {
		var point TelemetryPoint
		if err := json.Unmarshal(p, &point); err != nil {
			t.Error(err)
			return
		}
		got <- point.Seq
	}); err != nil {
		t.Fatal(err)
	}

	for i := uint64(0); i < n; i++ {
		if err := bus.Publish(context.Background(), ChannelTelemetry, TelemetryPoint{Seq: i}); err != nil {
			t.Fatal(err)
		}
	}
	for want := uint64(0); want < n; want++ {
		select {
		case seq := <-got:
			if seq != want {
				t.Fatalf("out-of-order delivery: got seq %d, want %d", seq, want)
			}
		case <-time.After(2 * time.Second):
			t.Fatalf("timed out at seq %d", want)
		}
	}
}

func TestInProcessBusChannelIsolation(t *testing.T) {
	bus := NewInProcessBus(slog.Default())
	defer bus.Close()

	alarmCh := make(chan []byte, 1)
	if _, err := bus.Subscribe(ChannelAlarm, func(_ context.Context, p []byte) { alarmCh <- p }); err != nil {
		t.Fatal(err)
	}

	if err := bus.Publish(context.Background(), ChannelTelemetry, TelemetryPoint{DeviceID: "dev-1"}); err != nil {
		t.Fatal(err)
	}

	select {
	case <-alarmCh:
		t.Error("alarm subscriber received telemetry event")
	case <-time.After(100 * time.Millisecond):
	}
}

func TestInProcessBusUnsubscribeStopsDelivery(t *testing.T) {
	bus := NewInProcessBus(slog.Default())
	defer bus.Close()

	got := make(chan []byte, 1)
	unsub, err := bus.Subscribe(ChannelCommand, func(_ context.Context, p []byte) { got <- p })
	if err != nil {
		t.Fatal(err)
	}
	unsub()

	if err := bus.Publish(context.Background(), ChannelCommand, CommandState{CommandID: "c1"}); err != nil {
		t.Fatal(err)
	}

	select {
	case <-got:
		t.Error("unsubscribed handler received event")
	case <-time.After(100 * time.Millisecond):
	}
}

func TestInProcessBusPublishAfterCloseIsDropped(t *testing.T) {
	bus := NewInProcessBus(slog.Default())

	got := make(chan []byte, 1)
	if _, err := bus.Subscribe(ChannelAlarm, func(_ context.Context, p []byte) { got <- p }); err != nil {
		t.Fatal(err)
	}
	if err := bus.Close(); err != nil {
		t.Fatal(err)
	}

	if err := bus.Publish(context.Background(), ChannelAlarm, AlarmEvent{AlarmID: 1}); err != nil {
		t.Fatal(err)
	}
	select {
	case <-got:
		t.Error("closed bus delivered event")
	case <-time.After(100 * time.Millisecond):
	}
}
