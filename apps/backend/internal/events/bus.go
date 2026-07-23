package events

import (
	"context"
	"encoding/json"
	"log/slog"
	"sync"
)

// Handler receives the JSON-encoded payload published on a channel. Handlers
// of one subscription run serially; a slow handler eventually backpressures
// publishers of its channel (see Bus delivery semantics).
type Handler func(ctx context.Context, payload []byte)

// Bus is the cross-module event contract. Payloads are marshalled to JSON at
// publish time so in-process and Redis-bridged delivery carry identical bytes.
//
// Delivery semantics (all implementations):
//   - Per subscription, events of a channel arrive serially in publish order.
//     Distinct subscriptions are independent and run concurrently.
//   - Each subscription has a bounded queue; when it fills up, Publish blocks
//     (backpressure) rather than dropping or growing unbounded.
//   - Publish may return an error AFTER local delivery already happened
//     (e.g. the Redis bridge failed). Callers must not retry a failed
//     Publish, or local subscribers will observe duplicates.
type Bus interface {
	// Publish sends v (marshalled as JSON) to all subscribers of channel.
	Publish(ctx context.Context, channel string, v any) error
	// Subscribe registers h for channel and returns an unsubscribe func.
	// Unsubscribing stops delivery promptly; queued events may be discarded.
	Subscribe(channel string, h Handler) (unsubscribe func(), err error)
	// Close stops delivery; subsequent Publish calls are dropped.
	Close() error
}

// subscriptionQueueSize bounds each subscriber's backlog. Sized for telemetry
// bursts (gateway backfill replay) while keeping worst-case memory small.
const subscriptionQueueSize = 1024

type subscription struct {
	queue chan []byte
	done  chan struct{}
	once  sync.Once
}

func (s *subscription) stop() { s.once.Do(func() { close(s.done) }) }

// InProcessBus fans events out to local subscribers — the hot path within a
// single role (e.g. ingest → rules inside role worker). One worker goroutine
// per subscription preserves per-subscriber ordering.
type InProcessBus struct {
	mu     sync.RWMutex
	nextID int
	subs   map[string]map[int]*subscription
	closed bool
	ctx    context.Context // passed to handlers, cancelled on Close
	cancel context.CancelFunc
	logger *slog.Logger
}

// NewInProcessBus returns a bus that delivers only within this process.
func NewInProcessBus(logger *slog.Logger) *InProcessBus {
	ctx, cancel := context.WithCancel(context.Background())
	return &InProcessBus{
		subs:   make(map[string]map[int]*subscription),
		ctx:    ctx,
		cancel: cancel,
		logger: logger,
	}
}

func (b *InProcessBus) Publish(_ context.Context, channel string, v any) error {
	payload, err := json.Marshal(v)
	if err != nil {
		return err
	}
	b.dispatch(channel, payload)
	return nil
}

// dispatch enqueues raw bytes to every subscription of the channel, blocking
// per full queue (backpressure). Also used by the Redis bridge to hand off
// remote messages without re-marshalling.
func (b *InProcessBus) dispatch(channel string, payload []byte) {
	b.mu.RLock()
	if b.closed {
		b.mu.RUnlock()
		return
	}
	targets := make([]*subscription, 0, len(b.subs[channel]))
	for _, s := range b.subs[channel] {
		targets = append(targets, s)
	}
	b.mu.RUnlock()

	for _, s := range targets {
		select {
		case s.queue <- payload:
		case <-s.done: // unsubscribed while we were blocked
		case <-b.ctx.Done(): // bus closed while we were blocked
			return
		}
	}
}

func (b *InProcessBus) Subscribe(channel string, h Handler) (func(), error) {
	sub := &subscription{
		queue: make(chan []byte, subscriptionQueueSize),
		done:  make(chan struct{}),
	}

	b.mu.Lock()
	if b.subs[channel] == nil {
		b.subs[channel] = make(map[int]*subscription)
	}
	id := b.nextID
	b.nextID++
	b.subs[channel][id] = sub
	b.mu.Unlock()

	// Serial worker: preserves publish order for this subscriber.
	go func() {
		for {
			select {
			case payload := <-sub.queue:
				h(b.ctx, payload)
			case <-sub.done:
				return
			case <-b.ctx.Done():
				return
			}
		}
	}()

	return func() {
		sub.stop()
		b.mu.Lock()
		delete(b.subs[channel], id)
		b.mu.Unlock()
	}, nil
}

func (b *InProcessBus) Close() error {
	b.mu.Lock()
	b.closed = true
	b.subs = make(map[string]map[int]*subscription)
	b.mu.Unlock()
	b.cancel()
	return nil
}
