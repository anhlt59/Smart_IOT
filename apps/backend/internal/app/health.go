package app

import (
	"context"
	"errors"
	"net/http"
	"time"
)

// healthServer exposes GET /healthz for container healthchecks. It reports
// 200 only when every infrastructure dependency (PG, Redis, MQTT) is
// reachable, so `docker compose ps` reflects real readiness.
type healthServer struct {
	srv   *http.Server
	check func(ctx context.Context) error
}

func newHealthServer(addr string, check func(ctx context.Context) error) *healthServer {
	h := &healthServer{check: check}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
		defer cancel()
		if err := h.check(ctx); err != nil {
			http.Error(w, "unhealthy: "+err.Error(), http.StatusServiceUnavailable)
			return
		}
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	h.srv = &http.Server{
		Addr:              addr,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}
	return h
}

// start blocks until the server stops; a graceful stop() returns nil.
func (h *healthServer) start() error {
	err := h.srv.ListenAndServe()
	if errors.Is(err, http.ErrServerClosed) {
		return nil
	}
	return err
}

func (h *healthServer) stop(ctx context.Context) error {
	return h.srv.Shutdown(ctx)
}
