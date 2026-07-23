# Build stage
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

# Runtime stage — alpine (not scratch) so busybox wget serves compose healthchecks
FROM alpine:3.21
RUN adduser -D -u 10001 app
USER app
COPY --from=build /out/app /usr/local/bin/app
ENTRYPOINT ["app"]
CMD ["--role=all"]
