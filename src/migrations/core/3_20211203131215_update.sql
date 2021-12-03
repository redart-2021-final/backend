-- upgrade --
ALTER TABLE "user" ADD "color" VARCHAR(6);
ALTER TABLE "event" ADD "speed" DOUBLE PRECISION;
-- downgrade --
ALTER TABLE "user" DROP COLUMN "color";
ALTER TABLE "event" DROP COLUMN "speed";
