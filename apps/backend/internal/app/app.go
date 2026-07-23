// Package app wires infrastructure clients (PostgreSQL, Redis, EMQX) and
// starts the modules selected by the process role. Feature modules (ingest,
// rules, jobs, api) plug into runRole as they are implemented; the skeleton
// proves connectivity and lifecycle.
package app

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/redis/go-redis/v9"

	"github.com/anhlt59/Smart_IOT/apps/backend/internal/config"
	"github.com/anhlt59/Smart_IOT/apps/backend/internal/events"
)

// Role selects which modules run in this process.
type Role string

const (
	RoleAPI    Role = "api"
	RoleIngest Role = "ingest"
	RoleWorker Role = "worker" // ingest + rules + jobs in one process (hot path)
	RoleAll    Role = "all"
)

// ValidateRole rejects unknown --role values before any client connects.
func ValidateRole(role string) error {
	switch Role(role) {
	case RoleAPI, RoleIngest, RoleWorker, RoleAll:
		return nil
	}
	return fmt.Errorf("unknown role %q (expected api|ingest|worker|all)", role)
}

// Run connects all infrastructure clients, starts the health server and the
// role modules, then blocks until ctx is cancelled and shuts down gracefully.
func Run(ctx context.Context, role Role, logger *slog.Logger) error {
	cfg, err := config.Load()
	if err != nil {
		return err
	}

	pool, err := connectPostgres(ctx, cfg)
	if err != nil {
		return fmt.Errorf("postgres: %w", err)
	}
	defer pool.Close()
	logger.Info("postgres connected")

	rdb := redis.NewClient(&redis.Options{Addr: cfg.RedisAddr, Password: cfg.RedisPassword})
	defer rdb.Close()
	if err := rdb.Ping(ctx).Err(); err != nil {
		return fmt.Errorf("redis: %w", err)
	}
	logger.Info("redis connected")

	mqttClient, err := connectMQTT(cfg, role, logger)
	if err != nil {
		return fmt.Errorf("mqtt: %w", err)
	}
	defer mqttClient.Disconnect(uint(cfg.ShutdownTimeout.Milliseconds()))
	logger.Info("mqtt connected", "broker", cfg.MQTTBrokerURL)

	// Cross-role event bus: in-process fan-out + Redis pub/sub bridge.
	bus := events.NewRedisBus(rdb, logger)
	defer bus.Close()

	health := newHealthServer(cfg.HTTPAddr, func(ctx context.Context) error {
		if err := pool.Ping(ctx); err != nil {
			return fmt.Errorf("postgres: %w", err)
		}
		if err := rdb.Ping(ctx).Err(); err != nil {
			return fmt.Errorf("redis: %w", err)
		}
		if !mqttClient.IsConnectionOpen() {
			return errors.New("mqtt: connection not open")
		}
		return nil
	})
	healthErr := make(chan error, 1)
	go func() { healthErr <- health.start() }()

	runRole(ctx, role, logger)
	logger.Info("ready", "role", role, "http_addr", cfg.HTTPAddr, "topic_prefix", cfg.TopicPrefix)

	select {
	case <-ctx.Done():
	case err := <-healthErr:
		return fmt.Errorf("health server: %w", err)
	}

	logger.Info("shutting down", "role", role)
	shutdownCtx, cancel := context.WithTimeout(context.Background(), cfg.ShutdownTimeout)
	defer cancel()
	return health.stop(shutdownCtx)
}

// runRole starts the modules owned by each role. The stubs below hold each
// module's lifecycle slot until the real ingest/rules/jobs/api
// implementations replace them.
func runRole(ctx context.Context, role Role, logger *slog.Logger) {
	start := func(name string) {
		go func() {
			logger.Info("module stub started (implementation pending)", "module", name)
			<-ctx.Done()
			logger.Info("module stopped", "module", name)
		}()
	}
	if role == RoleAPI || role == RoleAll {
		start("api")
	}
	if role == RoleIngest || role == RoleWorker || role == RoleAll {
		start("ingest")
	}
	if role == RoleWorker || role == RoleAll {
		start("rules")
		start("jobs")
	}
}

func connectPostgres(ctx context.Context, cfg *config.Config) (*pgxpool.Pool, error) {
	pingCtx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	pool, err := pgxpool.New(pingCtx, cfg.PostgresDSN)
	if err != nil {
		return nil, err
	}
	if err := pool.Ping(pingCtx); err != nil {
		pool.Close()
		return nil, err
	}
	return pool, nil
}

func connectMQTT(cfg *config.Config, role Role, logger *slog.Logger) (mqtt.Client, error) {
	opts := mqtt.NewClientOptions().
		AddBroker(cfg.MQTTBrokerURL).
		SetClientID(fmt.Sprintf("%s-%s", cfg.MQTTClientIDPrefix, role)).
		SetUsername(cfg.MQTTUsername).
		SetPassword(cfg.MQTTPassword).
		// Persistent session: broker keeps QoS1 messages while this
		// consumer is down (Interface Agreement delivery chain).
		SetCleanSession(false).
		SetAutoReconnect(true).
		SetConnectRetry(true).
		SetConnectRetryInterval(2 * time.Second).
		SetConnectionLostHandler(func(_ mqtt.Client, err error) {
			logger.Warn("mqtt connection lost, reconnecting", "error", err)
		})

	client := mqtt.NewClient(opts)
	token := client.Connect()
	if !token.WaitTimeout(30 * time.Second) {
		return nil, errors.New("connect timeout")
	}
	if err := token.Error(); err != nil {
		return nil, err
	}
	return client, nil
}
