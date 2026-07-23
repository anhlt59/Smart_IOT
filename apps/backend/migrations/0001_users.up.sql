-- Users and RBAC roles (POC: 3 fixed roles; consumed by the API JWT auth).
CREATE TABLE users (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    pass_hash  TEXT NOT NULL, -- bcrypt
    role       TEXT NOT NULL CHECK (role IN ('admin', 'operator', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed admin. Default password: ChangeMe123! (bcrypt, cost 10) — POC only,
-- must be rotated before any demo outside the team.
INSERT INTO users (username, pass_hash, role)
VALUES ('admin', '$2a$10$rUdFTgRJltbGpJ7ECkYqROM/HjQbUhuDts2GUevJicoJv.ncF/CaK', 'admin');
