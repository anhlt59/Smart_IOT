package config

import (
	"testing"
	"time"
)

func TestLoadDefaults(t *testing.T) {
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if cfg.HTTPAddr != ":8080" {
		t.Errorf("HTTPAddr = %q, want :8080", cfg.HTTPAddr)
	}
	if cfg.TopicPrefix != "v1/demo/park01" {
		t.Errorf("TopicPrefix = %q, want v1/demo/park01", cfg.TopicPrefix)
	}
	if cfg.ShutdownTimeout != 10*time.Second {
		t.Errorf("ShutdownTimeout = %v, want 10s", cfg.ShutdownTimeout)
	}
}

func TestLoadEnvOverrides(t *testing.T) {
	t.Setenv("HTTP_ADDR", ":9090")
	t.Setenv("MQTT_BROKER_URL", "tcp://emqx:1883")
	t.Setenv("SHUTDOWN_TIMEOUT_S", "3")

	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	if cfg.HTTPAddr != ":9090" {
		t.Errorf("HTTPAddr = %q, want :9090", cfg.HTTPAddr)
	}
	if cfg.MQTTBrokerURL != "tcp://emqx:1883" {
		t.Errorf("MQTTBrokerURL = %q, want tcp://emqx:1883", cfg.MQTTBrokerURL)
	}
	if cfg.ShutdownTimeout != 3*time.Second {
		t.Errorf("ShutdownTimeout = %v, want 3s", cfg.ShutdownTimeout)
	}
}

func TestLoadRejectsInvalidShutdownTimeout(t *testing.T) {
	for _, bad := range []string{"abc", "0", "-5"} {
		t.Setenv("SHUTDOWN_TIMEOUT_S", bad)
		if _, err := Load(); err == nil {
			t.Errorf("SHUTDOWN_TIMEOUT_S=%q: expected error, got nil", bad)
		}
	}
}
