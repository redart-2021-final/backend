-- upgrade --
CREATE TABLE IF NOT EXISTS "device" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(256) NOT NULL,
    "extra" JSONB NOT NULL,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "owner_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);;
CREATE TABLE IF NOT EXISTS "event" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "extra" JSONB NOT NULL,
    "processed" BOOL NOT NULL  DEFAULT False,
    "device_id" UUID NOT NULL REFERENCES "device" ("id") ON DELETE CASCADE
);-- downgrade --
DROP TABLE IF EXISTS "device";
DROP TABLE IF EXISTS "event";
