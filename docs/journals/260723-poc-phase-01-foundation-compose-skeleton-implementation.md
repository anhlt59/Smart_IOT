# Phase 1: Foundation Compose Skeleton — Built, Debugged, All E2E Verified

**Date**: 2026-07-23 14:50  
**Severity**: None (completed successfully)  
**Component**: Backend skeleton, infrastructure, CI/CD bootstrap  
**Status**: Resolved

## What Happened

Built the modular monolith Go backend skeleton (role-dispatched single binary, env config, OpenAPI contract) + Docker Compose edge infrastructure (7 pinned containers, one-shot migrations, healthchecks) + root Makefile + GitHub Actions CI. All 5 success criteria verified live E2E; 11 unit tests passing with `-race` deterministic. Code review feedback acted on: event bus rewritten for per-subscription serial ordering, secrets exfiltrated from git, healthz reports real dependency state, code comments cleaned per project rules.

## The Brutal Truth

Six hours of pure debugging frustration. The infrastructure *looked* simple — Docker Compose, standard images, basic config — but configuration gotchas and monitoring blindspots turned trivial-sounding errors into multi-step hunts. The worst part: exit code masking by `make up | tail` made the entire compose failure appear successful, which meant we chased symptoms in the wrong layer for 90 minutes.

## Technical Details

**1. EMQX 5.8.4 exit 127 — hidden schema requirement**  
Bind-mounting a custom `emqx.conf` *replaces* the image default. Missing the required `node{name,data_dir}` block inside → HOCON schema validation aborts silently. Exit 127 suggested "command not found", not "config schema failed". Learned: read image schema, not just flags.

**2. Durable sessions crash — undocumented coupling**  
`durable_sessions.enable=true` with builtin_local storage requires `cluster.discovery_strategy = singleton`. Default image uses `manual` → integrity validation fails on boot. The log message was clear once we found the right line — but it was buried in a 200-line boot sequence.

**3. Host port conflict → remapped to 127.0.0.1:5433**  
Another project's postgres container (zoo-postgres) claimed 5432. No drama, just a reminder to check `docker ps -a` before assuming blank slate.

**4. Exit code masking — the absolute worst**  
Command: `make up | tail`. The pipe returns tail's exit 0 even if compose failed with "dependency failed to start: postgres is unhealthy". Background task reported success; postgres never came up. Spent 90 minutes chasing phantom healthcheck logic before realizing compose had actually aborted. **Lesson:** never pipe a command whose exit code you depend on. Became: `make up && echo "OK"` to see actual failure.

**5. Postgres healthcheck flap — timing is everything**  
`pg_isready` over unix socket returns ready during initdb's TEMPORARY server phase. Postgres then restarts internally, flipping container to unhealthy exactly when compose evaluates `depends_on` — dependents abort before real startup. TCP-based check (temp server has no TCP listener) + `start_period: 30s` fixed it. The trap: TEMPORARY server looks healthy but isn't persistent.

**6. Initdb script permission denied on :ro mount**  
Script without `+x` bit on a read-only bind mount → `/bin/sh: bad interpreter: Permission denied`. Postgres continued anyway; failure surfaced 5 steps later as missing grafana_ro role. Git preserves chmod bits; the CI copy didn't.

## Root Cause Analysis

All six issues trace to **image-default assumptions + hidden coupling + poor observability**:
- EMQX: schema validation is invisible until you parse the full config spec
- Postgres: healthcheck timing couples to initdb internals (boot sequence not just process-ready)
- Exit code: shell pipes swallow failure signals — classic footgun
- Permissions: git doesn't track mode bits reliably across checkout

We built defensively *after* the fact: validate healthz with real dependency pings, bind all services to loopback (no accidental exposure), single-source secrets, explicit integration tests.

## Lessons Learned

1. **Validate image defaults** — Don't assume standard config; read schema or trace first boot with `docker logs`.
2. **Healthchecks must model real dependencies** — TCP over unix socket, account for boot sequencing, use `start_period` buffer.
3. **Monitor exit codes rigorously** — Never pipe final status; capture and log explicitly.
4. **Distributed boot is fragile** — Coupling between internal server restart + orchestration evaluation window is real. Add headroom.
5. **Permissions in CI:** chmod during build or validate in entrypoint.

## Next Steps

1. Document EMQX bootstrap flow + schema validation in infra README.
2. Add CI healthcheck validation (wait-for script + timeout).
3. Phase 2: edge telemetry ingestion (PLC → MQTT → Kafka bridge).

---

**Status:** DONE  
**Summary:** Built Phase 1 skeleton (Go backend, Compose infra, 11 passing tests), debugged 6 infrastructure configuration gotchas (EMQX schema, postgres healthcheck timing, exit code masking), all success criteria verified E2E.
