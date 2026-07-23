// Command app is the single POC binary. The --role flag selects which
// modules run in this process (modular monolith, D7 Docker Compose):
//
//	api    – REST API + WebSocket hub
//	ingest – MQTT telemetry consumer
//	worker – ingest + rules/alarms + jobs in one process so rule evaluation
//	         stays in-process on the hot path (KPI: event/alarm <= 2s)
//	all    – everything in one process (local development)
package main

import (
	"context"
	"flag"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/anhlt59/Smart_IOT/apps/backend/internal/app"
)

func main() {
	role := flag.String("role", "all", "process role: api|ingest|worker|all")
	flag.Parse()

	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: logLevel(),
	}))
	slog.SetDefault(logger)

	if err := app.ValidateRole(*role); err != nil {
		logger.Error("invalid --role flag", "error", err)
		os.Exit(2)
	}

	// Cancelled on SIGINT/SIGTERM; app.Run drains and closes everything.
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := app.Run(ctx, app.Role(*role), logger); err != nil {
		logger.Error("application exited with error", "role", *role, "error", err)
		os.Exit(1)
	}
	logger.Info("shutdown complete")
}

func logLevel() slog.Level {
	switch os.Getenv("LOG_LEVEL") {
	case "debug":
		return slog.LevelDebug
	case "warn":
		return slog.LevelWarn
	case "error":
		return slog.LevelError
	default:
		return slog.LevelInfo
	}
}
