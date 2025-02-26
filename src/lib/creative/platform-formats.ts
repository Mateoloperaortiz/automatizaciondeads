import { PrismaClient, Platform } from '@prisma/client';

const prisma = new PrismaClient();

// Format requirements for each platform
// These are based on current specifications, but would need regular updates
const platformFormats = [
  // Meta (Facebook & Instagram) Formats
  {
    platform: Platform.META,
    formatName: 'Feed Image',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    maxFileSize: 30720, // 30MB
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 125,
  },
  {
    platform: Platform.META,
    formatName: 'Feed Landscape',
    width: 1200,
    height: 628,
    aspectRatio: '1.91:1',
    maxFileSize: 30720,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 125,
  },
  {
    platform: Platform.META,
    formatName: 'Story',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 30720,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 125,
  },
  
  // Google Ads Formats
  {
    platform: Platform.GOOGLE,
    formatName: 'Display Square',
    width: 250,
    height: 250,
    aspectRatio: '1:1',
    maxFileSize: 150, // 150KB
    supportedTypes: ['jpg', 'png', 'gif'],
    textMaxLength: 90,
  },
  {
    platform: Platform.GOOGLE,
    formatName: 'Display Leaderboard',
    width: 728,
    height: 90,
    aspectRatio: '8.09:1',
    maxFileSize: 150,
    supportedTypes: ['jpg', 'png', 'gif'],
    textMaxLength: 90,
  },
  {
    platform: Platform.GOOGLE,
    formatName: 'Display Large Rectangle',
    width: 336,
    height: 280,
    aspectRatio: '1.2:1',
    maxFileSize: 150,
    supportedTypes: ['jpg', 'png', 'gif'],
    textMaxLength: 90,
  },
  
  // Twitter (X) Formats
  {
    platform: Platform.TWITTER,
    formatName: 'Single Image',
    width: 1600,
    height: 900,
    aspectRatio: '16:9',
    maxFileSize: 5120, // 5MB
    supportedTypes: ['jpg', 'png', 'webp'],
    textMaxLength: 280,
  },
  {
    platform: Platform.TWITTER,
    formatName: 'Card Image',
    width: 800,
    height: 418,
    aspectRatio: '1.91:1',
    maxFileSize: 5120,
    supportedTypes: ['jpg', 'png', 'webp'],
    textMaxLength: 280,
  },
  
  // TikTok Formats
  {
    platform: Platform.TIKTOK,
    formatName: 'Feed Video',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 512000, // 500MB
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 100,
  },
  {
    platform: Platform.TIKTOK,
    formatName: 'Feed Image',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 10240, // 10MB
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 100,
  },
  
  // Snapchat Formats
  {
    platform: Platform.SNAPCHAT,
    formatName: 'Snap Ad',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 5120, // 5MB
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 150,
  },
  {
    platform: Platform.SNAPCHAT,
    formatName: 'Story Ad',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    maxFileSize: 5120,
    supportedTypes: ['jpg', 'png'],
    textMaxLength: 150,
  },
];

/**
 * Initialize platform format requirements in the database
 * This should be run during application setup or as a migration
 */
export async function initializePlatformFormats() {
  console.log('Initializing platform format requirements...');
  
  for (const format of platformFormats) {
    await prisma.platformFormat.upsert({
      where: {
        platform_formatName: {
          platform: format.platform,
          formatName: format.formatName,
        },
      },
      update: format,
      create: format,
    });
  }
  
  console.log('Platform format requirements initialized successfully.');
}

// If this file is run directly
if (require.main === module) {
  initializePlatformFormats()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Error initializing platform formats:', error);
      process.exit(1);
    });
}
