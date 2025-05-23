ALTER TABLE "job_ads" ADD COLUMN "derived_audience_primitives" jsonb;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "audience_cluster_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "audience_confidence" numeric(5, 4);