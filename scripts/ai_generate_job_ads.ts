// scripts/ai_generate_job_ads.ts
// Run with: npx ts-node scripts/ai_generate_job_ads.ts --team 1 --user 1 --count 3 --platforms meta,x,google
// This script calls OpenAI Chat Completion API to generate realistic job advertisements and stores them in the database.

import { Command } from 'commander';
import * as dotenv from 'dotenv';
import { OpenAI } from 'openai';
import { db } from '@/lib/db/drizzle';
import { jobAds, NewJobAd } from '@/lib/db/schema';
import { sql } from 'drizzle-orm';

// Load .env so OPENAI_API_KEY & DATABASE_URL are available when running standalone
dotenv.config();

const program = new Command();
program
  .option('-t, --team <teamId>', 'Team ID that should own the ads', parseInt)
  .option('-u, --user <userId>', 'User ID recorded as creator', parseInt)
  .option('-c, --count <n>', 'Number of job ads to generate', (v) => parseInt(v, 10), 1)
  .option('-p, --platforms <list>', 'Comma-separated list of enabled platforms (meta,x,google)', 'meta,x,google');

program.parse();
const opts = program.opts();

if (!opts.team || !opts.user) {
  console.error('Both --team and --user are required.');
  process.exit(1);
}

if (!process.env.OPENAI_API_KEY) {
  console.error('OPENAI_API_KEY not set in environment.');
  process.exit(1);
}

const openaiClient = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });

async function generateSingleAd(): Promise<NewJobAd> {
  const systemPrompt = `You are an expert HR recruiter and copywriter. You create concise, engaging job advertisements suitable for social media and search ads. Output MUST be valid JSON with these keys and no extra text:\n- title (max 100 chars)\n- companyName (max 100 chars)\n- descriptionShort (max 280 chars)\n- descriptionLong (max 600 chars)\n- targetUrl (must start with https)\n- suggestedSkills (array of 1-4 short keywords)\nIf you cannot comply, output exactly {"error": "fail"}.`;

  const response = await openaiClient.chat.completions.create({
    model: 'gpt-4o-mini',
    temperature: 0.8,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: 'Create a software-engineering-focused job ad.' },
    ],
    response_format: { type: 'json_object' },
  });

  const raw = response.choices[0].message.content ?? '{}';
  const json = JSON.parse(raw);
  if (json.error) throw new Error('OpenAI generation failed');

  const now = new Date();
  const start = new Date(now.getTime() + 60 * 60 * 1000); // +1h

  const ad: NewJobAd = {
    title: json.title,
    companyName: json.companyName,
    descriptionShort: json.descriptionShort,
    descriptionLong: json.descriptionLong,
    targetUrl: json.targetUrl,
    creativeAssetUrl: null,
    budgetDaily: '10.00',
    scheduleStart: start,
    scheduleEnd: null,
    platformsMetaEnabled: opts.platforms.includes('meta'),
    platformsXEnabled: opts.platforms.includes('x'),
    platformsGoogleEnabled: opts.platforms.includes('google'),
    status: 'scheduled',
    teamId: opts.team,
    createdByUserId: opts.user,
  } as NewJobAd;

  return ad;
}

(async () => {
  try {
    const ads: NewJobAd[] = [];
    for (let i = 0; i < opts.count; i++) {
      process.stdout.write(`Generating ad ${i + 1}/${opts.count}...\n`);
      const ad = await generateSingleAd();
      ads.push(ad);
    }

    const inserted = await db
      .insert(jobAds)
      .values(ads as any)
      .returning({ id: jobAds.id });

    console.log('Inserted job ads with IDs:', inserted.map((r) => r.id).join(', '));
    process.exit(0);
  } catch (err: any) {
    console.error('Error generating ads:', err.message);
    process.exit(1);
  }
})(); 