ALTER TABLE "job_ads" ADD COLUMN "audience_cluster_profile_name" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "mapped_targeting" jsonb;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "segmentation_processed_at" timestamp;