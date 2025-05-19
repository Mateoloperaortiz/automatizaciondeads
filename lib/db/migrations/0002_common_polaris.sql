ALTER TABLE "job_ads" ALTER COLUMN "status" SET DATA TYPE varchar(50);--> statement-breakpoint
ALTER TABLE "job_ads" ALTER COLUMN "status" SET DEFAULT 'draft';--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "company_name" varchar(100);--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "video_thumbnail_url" varchar(2048);--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "meta_campaign_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "meta_ad_set_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "meta_ad_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "x_campaign_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "x_line_item_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "x_promoted_tweet_id" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "google_campaign_resource_name" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "google_ad_group_resource_name" text;--> statement-breakpoint
ALTER TABLE "job_ads" ADD COLUMN "google_ad_resource_name" text;--> statement-breakpoint
ALTER TABLE "social_platform_connections" ADD COLUMN "token_secret" text;--> statement-breakpoint
ALTER TABLE "social_platform_connections" ADD COLUMN "funding_instrument_id" varchar(255);