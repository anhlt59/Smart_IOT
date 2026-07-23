package events

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"sync"

	"github.com/redis/go-redis/v9"
)

// envelope wraps every payload crossing Redis so a process can drop its own
// messages when they echo back (local delivery already happened in Publish).
type envelope struct {
	Src  string          `json:"src"`
	Data json.RawMessage `json:"data"`
}

// RedisBus delivers events to local subscribers in-process (hot path) and
// bridges them across roles through Redis pub/sub (e.g. worker → api for
// WebSocket fan-out). One RedisBus per process.
type RedisBus struct {
	local      *InProcessBus
	rdb        *redis.Client
	pubsub     *redis.PubSub
	instanceID string
	logger     *slog.Logger

	mu         sync.Mutex
	subscribed map[string]bool // channels with an active Redis subscription
	cancel     context.CancelFunc
}

// NewRedisBus starts the bridge. The returned bus is ready; Redis
// subscriptions are added lazily per channel on first Subscribe.
func NewRedisBus(rdb *redis.Client, logger *slog.Logger) *RedisBus {
	ctx, cancel := context.WithCancel(context.Background())

	b := &RedisBus{
		local:      NewInProcessBus(logger),
		rdb:        rdb,
		instanceID: newInstanceID(),
		logger:     logger,
		subscribed: make(map[string]bool),
		cancel:     cancel,
	}
	// Connection-less PubSub: channels are added via pubsub.Subscribe.
	b.pubsub = rdb.Subscribe(ctx)
	go b.receiveLoop(ctx)
	return b
}

// Publish delivers locally first (no Redis latency on the hot path), then
// bridges to other roles via Redis. A Redis failure is returned AFTER local
// delivery already happened — per the Bus contract, do not retry on error.
func (b *RedisBus) Publish(ctx context.Context, channel string, v any) error {
	payload, err := json.Marshal(v)
	if err != nil {
		return err
	}
	b.local.dispatch(channel, payload)

	env, err := json.Marshal(envelope{Src: b.instanceID, Data: payload})
	if err != nil {
		return err
	}
	if err := b.rdb.Publish(ctx, channel, env).Err(); err != nil {
		return fmt.Errorf("redis publish %s: %w", channel, err)
	}
	return nil
}

// Subscribe registers h locally and ensures this process receives the
// channel from other roles via Redis. Unsubscribing stops local delivery
// only; the Redis channel subscription stays open (channels are few and
// fixed, refcounting is not worth the complexity).
func (b *RedisBus) Subscribe(channel string, h Handler) (func(), error) {
	unsub, err := b.local.Subscribe(channel, h)
	if err != nil {
		return nil, err
	}

	b.mu.Lock()
	defer b.mu.Unlock()
	if !b.subscribed[channel] {
		if err := b.pubsub.Subscribe(context.Background(), channel); err != nil {
			unsub()
			return nil, fmt.Errorf("redis subscribe %s: %w", channel, err)
		}
		b.subscribed[channel] = true
	}
	return unsub, nil
}

func (b *RedisBus) Close() error {
	b.cancel()
	err := b.pubsub.Close()
	_ = b.local.Close()
	return err
}

// receiveLoop dispatches messages arriving from other processes. Messages
// originating here are dropped: their local delivery happened in Publish.
func (b *RedisBus) receiveLoop(ctx context.Context) {
	ch := b.pubsub.Channel()
	for {
		select {
		case <-ctx.Done():
			return
		case msg, ok := <-ch:
			if !ok {
				return
			}
			var env envelope
			if err := json.Unmarshal([]byte(msg.Payload), &env); err != nil {
				b.logger.Warn("events: dropping malformed bridge message",
					"channel", msg.Channel, "error", err)
				continue
			}
			if env.Src == b.instanceID {
				continue
			}
			b.local.dispatch(msg.Channel, env.Data)
		}
	}
}

func newInstanceID() string {
	buf := make([]byte, 8)
	if _, err := rand.Read(buf); err != nil {
		// crypto/rand failing means the OS entropy source is broken;
		// nothing sensible to fall back to.
		panic(fmt.Sprintf("events: cannot generate instance id: %v", err))
	}
	return hex.EncodeToString(buf)
}
