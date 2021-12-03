-- upgrade --
ALTER TABLE "event" ADD "accuracy" DOUBLE PRECISION;
ALTER TABLE "event" ADD "latitude" DOUBLE PRECISION;
ALTER TABLE "event" ADD "longitude" DOUBLE PRECISION;
ALTER TABLE "event" ADD "battery" DOUBLE PRECISION;
CREATE UNIQUE INDEX "uid_user_usernam_9987ab" ON "user" ("username");
-- downgrade --
DROP INDEX "idx_user_usernam_9987ab";
ALTER TABLE "event" DROP COLUMN "accuracy";
ALTER TABLE "event" DROP COLUMN "latitude";
ALTER TABLE "event" DROP COLUMN "longitude";
ALTER TABLE "event" DROP COLUMN "battery";
