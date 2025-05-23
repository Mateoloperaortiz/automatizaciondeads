import {
  pgTable,
  serial,
  varchar,
  text,
  timestamp,
  integer,
  boolean,
  decimal,
  unique,
  jsonb, // Import jsonb for storing array of objects
} from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }),
  email: varchar('email', { length: 255 }).notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  role: varchar('role', { length: 20 }).notNull().default('member'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  deletedAt: timestamp('deleted_at'),
});

export const teams = pgTable('teams', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  stripeCustomerId: text('stripe_customer_id').unique(),
  stripeSubscriptionId: text('stripe_subscription_id').unique(),
  stripeProductId: text('stripe_product_id'),
  planName: varchar('plan_name', { length: 50 }),
  subscriptionStatus: varchar('subscription_status', { length: 20 }),
});

export const teamMembers = pgTable('team_members', {
  id: serial('id').primaryKey(),
  userId: integer('user_id')
    .notNull()
    .references(() => users.id),
  teamId: integer('team_id')
    .notNull()
    .references(() => teams.id),
  role: varchar('role', { length: 50 }).notNull(),
  joinedAt: timestamp('joined_at').notNull().defaultNow(),
});

export const activityLogs = pgTable('activity_logs', {
  id: serial('id').primaryKey(),
  teamId: integer('team_id')
    .notNull()
    .references(() => teams.id),
  userId: integer('user_id').references(() => users.id),
  action: text('action').notNull(),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  ipAddress: varchar('ip_address', { length: 45 }),
});

export const invitations = pgTable('invitations', {
  id: serial('id').primaryKey(),
  teamId: integer('team_id')
    .notNull()
    .references(() => teams.id),
  email: varchar('email', { length: 255 }).notNull(),
  role: varchar('role', { length: 50 }).notNull(),
  invitedBy: integer('invited_by')
    .notNull()
    .references(() => users.id),
  invitedAt: timestamp('invited_at').notNull().defaultNow(),
  status: varchar('status', { length: 20 }).notNull().default('pending'),
});

export const jobAds = pgTable('job_ads', {
  id: serial('id').primaryKey(),
  teamId: integer('team_id')
    .notNull()
    .references(() => teams.id),
  title: varchar('title', { length: 100 }).notNull(),
  companyName: varchar('company_name', { length: 100 }),
  descriptionShort: text('description_short').notNull(),
  descriptionLong: text('description_long'),
  targetUrl: varchar('target_url', { length: 2048 }).notNull(),
  creativeAssetUrl: varchar('creative_asset_url', { length: 2048 }),
  platformsMetaEnabled: boolean('platforms_meta_enabled').default(false).notNull(),
  platformsXEnabled: boolean('platforms_x_enabled').default(false).notNull(),
  platformsGoogleEnabled: boolean('platforms_google_enabled').default(false).notNull(),
  budgetDaily: decimal('budget_daily', { precision: 10, scale: 2 }),
  scheduleStart: timestamp('schedule_start').notNull(),
  scheduleEnd: timestamp('schedule_end'),
  status: varchar('status', { length: 50 }).notNull().default('draft'),
  createdByUserId: integer('created_by_user_id').references(() => users.id),
  metaCampaignId: text('meta_campaign_id'),
  metaAdSetId: text('meta_ad_set_id'),
  metaAdId: text('meta_ad_id'),
  xCampaignId: text('x_campaign_id'),
  xLineItemId: text('x_line_item_id'),
  xPromotedTweetId: text('x_promoted_tweet_id'),
  googleCampaignResourceId: text('google_campaign_resource_name'),
  googleAdGroupResourceId: text('google_ad_group_resource_name'),
  googleAdResourceId: text('google_ad_resource_name'),
  // Fields for storing audience segmentation results
  derivedAudiencePrimitives: jsonb('derived_audience_primitives'), // Stores AudiencePrimitive[]
  audienceClusterId: text('audience_cluster_id'),
  audienceConfidence: decimal('audience_confidence', { precision: 5, scale: 4 }), // e.g., 0.8532
  audienceClusterProfileName: text('audience_cluster_profile_name'), // Human-readable cluster name
  mappedTargeting: jsonb('mapped_targeting'), // Stores PlatformAgnosticTargeting
  segmentationProcessedAt: timestamp('segmentation_processed_at'), // When segmentation was last run
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at')
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
});

export const socialPlatformConnections = pgTable(
  'social_platform_connections',
  {
    id: serial('id').primaryKey(),
    teamId: integer('team_id')
      .notNull()
      .references(() => teams.id),
    platformName: varchar('platform_name', { length: 50 }).notNull(),
    platformUserId: varchar('platform_user_id', { length: 255 }),
    platformAccountId: varchar('platform_account_id', { length: 255 }),
    accessToken: text('access_token').notNull(),
    tokenSecret: text('token_secret'),
    refreshToken: text('refresh_token'),
    tokenExpiresAt: timestamp('token_expires_at'),
    scopes: text('scopes'),
    status: varchar('status', { length: 20 }).notNull().default('active'),
    fundingInstrumentId: varchar('funding_instrument_id', { length: 255 }),
    createdAt: timestamp('created_at').notNull().defaultNow(),
    updatedAt: timestamp('updated_at')
      .notNull()
      .defaultNow()
      .$onUpdate(() => new Date()),
  },
  (table) => {
    return {
      teamPlatformUnique: unique('team_platform_unique_idx').on(table.teamId, table.platformName),
    };
  }
);

export const teamsRelations = relations(teams, ({ many }) => ({
  teamMembers: many(teamMembers),
  activityLogs: many(activityLogs),
  invitations: many(invitations),
  jobAds: many(jobAds),
  socialPlatformConnections: many(socialPlatformConnections),
}));

export const usersRelations = relations(users, ({ many }) => ({
  teamMembers: many(teamMembers),
  invitationsSent: many(invitations),
  jobAdsCreated: many(jobAds, { relationName: 'createdBy' }),
}));

export const invitationsRelations = relations(invitations, ({ one }) => ({
  team: one(teams, {
    fields: [invitations.teamId],
    references: [teams.id],
  }),
  invitedBy: one(users, {
    fields: [invitations.invitedBy],
    references: [users.id],
  }),
}));

export const teamMembersRelations = relations(teamMembers, ({ one }) => ({
  user: one(users, {
    fields: [teamMembers.userId],
    references: [users.id],
  }),
  team: one(teams, {
    fields: [teamMembers.teamId],
    references: [teams.id],
  }),
}));

export const activityLogsRelations = relations(activityLogs, ({ one }) => ({
  team: one(teams, {
    fields: [activityLogs.teamId],
    references: [teams.id],
  }),
  user: one(users, {
    fields: [activityLogs.userId],
    references: [users.id],
  }),
}));

export const jobAdsRelations = relations(jobAds, ({ one, many }) => ({
  team: one(teams, {
    fields: [jobAds.teamId],
    references: [teams.id],
  }),
  createdByUser: one(users, {
    fields: [jobAds.createdByUserId],
    references: [users.id],
    relationName: 'createdBy',
  }),
}));

export const socialPlatformConnectionsRelations = relations(
  socialPlatformConnections,
  ({ one }) => ({
    team: one(teams, {
      fields: [socialPlatformConnections.teamId],
      references: [teams.id],
    }),
  })
);

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Team = typeof teams.$inferSelect;
export type NewTeam = typeof teams.$inferInsert;
export type TeamMember = typeof teamMembers.$inferSelect;
export type NewTeamMember = typeof teamMembers.$inferInsert;
export type ActivityLog = typeof activityLogs.$inferSelect;
export type NewActivityLog = typeof activityLogs.$inferInsert;
export type Invitation = typeof invitations.$inferSelect;
export type NewInvitation = typeof invitations.$inferInsert;
export type TeamDataWithMembers = Team & {
  teamMembers: (TeamMember & {
    user: Pick<User, 'id' | 'name' | 'email'>;
  })[];
};

export type JobAd = typeof jobAds.$inferSelect;
export type NewJobAd = typeof jobAds.$inferInsert;
export type SocialPlatformConnection =
  typeof socialPlatformConnections.$inferSelect;
export type NewSocialPlatformConnection =
  typeof socialPlatformConnections.$inferInsert;

export enum ActivityType {
  SIGN_UP = 'SIGN_UP',
  SIGN_IN = 'SIGN_IN',
  SIGN_OUT = 'SIGN_OUT',
  UPDATE_PASSWORD = 'UPDATE_PASSWORD',
  DELETE_ACCOUNT = 'DELETE_ACCOUNT',
  UPDATE_ACCOUNT = 'UPDATE_ACCOUNT',
  CREATE_TEAM = 'CREATE_TEAM',
  REMOVE_TEAM_MEMBER = 'REMOVE_TEAM_MEMBER',
  INVITE_TEAM_MEMBER = 'INVITE_TEAM_MEMBER',
  ACCEPT_INVITATION = 'ACCEPT_INVITATION',
}
