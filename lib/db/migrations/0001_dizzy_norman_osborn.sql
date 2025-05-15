CREATE TABLE "job_ads" (
	"id" serial PRIMARY KEY NOT NULL,
	"team_id" integer NOT NULL,
	"title" varchar(100) NOT NULL,
	"description_short" text NOT NULL,
	"description_long" text,
	"target_url" varchar(2048) NOT NULL,
	"creative_asset_url" varchar(2048),
	"platforms_meta_enabled" boolean DEFAULT false NOT NULL,
	"platforms_x_enabled" boolean DEFAULT false NOT NULL,
	"platforms_google_enabled" boolean DEFAULT false NOT NULL,
	"budget_daily" numeric(10, 2),
	"schedule_start" timestamp NOT NULL,
	"schedule_end" timestamp,
	"status" varchar(20) DEFAULT 'draft' NOT NULL,
	"created_by_user_id" integer,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "social_platform_connections" (
	"id" serial PRIMARY KEY NOT NULL,
	"team_id" integer NOT NULL,
	"platform_name" varchar(50) NOT NULL,
	"platform_user_id" varchar(255),
	"platform_account_id" varchar(255),
	"access_token" text NOT NULL,
	"refresh_token" text,
	"token_expires_at" timestamp,
	"scopes" text,
	"status" varchar(20) DEFAULT 'active' NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "job_ads" ADD CONSTRAINT "job_ads_team_id_teams_id_fk" FOREIGN KEY ("team_id") REFERENCES "public"."teams"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "job_ads" ADD CONSTRAINT "job_ads_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "social_platform_connections" ADD CONSTRAINT "social_platform_connections_team_id_teams_id_fk" FOREIGN KEY ("team_id") REFERENCES "public"."teams"("id") ON DELETE no action ON UPDATE no action;