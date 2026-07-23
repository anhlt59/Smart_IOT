// Package config loads application configuration from environment variables.
// POC convention: env vars only (compose injects them from infra/edge/.env);
// no config files, no external config libraries.
package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

// Config holds all runtime settings shared by every role.
type Config struct {
	// HTTPAddr is the listen address of the role's HTTP server (health + API).
	HTTPAddr string

	// PostgresDSN is a pgx-compatible connection string.
	PostgresDSN string

	// RedisAddr is host:port of the Redis instance (last-value cache + pub/sub bridge).
	RedisAddr string
	// RedisPassword is empty for the POC default deployment.
	RedisPassword string

	// MQTTBrokerURL e.g. tcp://emqx:1883.
	MQTTBrokerURL string
	MQTTUsername  string
	MQTTPassword  string
	// MQTTClientIDPrefix is suffixed with the role name to keep client IDs unique.
	MQTTClientIDPrefix string

	// TopicPrefix is the fixed tenant/park prefix of the Interface Agreement
	// topic tree: v1/{tenant}/{park}. Single tenant in POC, kept as a
	// production seam.
	TopicPrefix string

	// ShutdownTimeout bounds graceful shutdown of servers and client disconnects.
	ShutdownTimeout time.Duration
}

// Load reads configuration from the environment. In compose, every value is
// injected explicitly (see infra/edge/docker-compose.yml). The defaults below
// target the compose stack's host-published ports (PG on host 5433) —
// passwords cannot default, so run via `make run-all`, which exports them
// from infra/edge/.env.
func Load() (*Config, error) {
	cfg := &Config{
		HTTPAddr:           getenv("HTTP_ADDR", ":8080"),
		PostgresDSN:        getenv("POSTGRES_DSN", "postgres://iot:iot@localhost:5433/iot?sslmode=disable"),
		RedisAddr:          getenv("REDIS_ADDR", "localhost:6379"),
		RedisPassword:      os.Getenv("REDIS_PASSWORD"),
		MQTTBrokerURL:      getenv("MQTT_BROKER_URL", "tcp://localhost:1883"),
		MQTTUsername:       getenv("MQTT_USERNAME", "app"),
		MQTTPassword:       os.Getenv("MQTT_PASSWORD"),
		MQTTClientIDPrefix: getenv("MQTT_CLIENT_ID_PREFIX", "iot-app"),
		TopicPrefix:        getenv("MQTT_TOPIC_PREFIX", "v1/demo/park01"),
	}

	timeoutSec, err := strconv.Atoi(getenv("SHUTDOWN_TIMEOUT_S", "10"))
	if err != nil || timeoutSec <= 0 {
		return nil, fmt.Errorf("config: invalid SHUTDOWN_TIMEOUT_S: %q", os.Getenv("SHUTDOWN_TIMEOUT_S"))
	}
	cfg.ShutdownTimeout = time.Duration(timeoutSec) * time.Second

	return cfg, nil
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
