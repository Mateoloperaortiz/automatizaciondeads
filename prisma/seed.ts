import { PrismaClient, UserRole } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  // Check if the test user already exists
  const existingUser = await prisma.user.findUnique({
    where: { email: 'test@example.com' },
  })

  if (!existingUser) {
    // Create test user
    const hashedPassword = await bcrypt.hash('password123', 10)
    
    const testUser = await prisma.user.create({
      data: {
        name: 'Test User',
        email: 'test@example.com',
        password: hashedPassword,
        role: UserRole.MANAGER,
      },
    })
    
    console.log(`Created test user: ${testUser.email}`)
  } else {
    console.log('Test user already exists')
  }

  // Create platform formats for creative adaptation if they don't exist
  const existingFormats = await prisma.platformFormat.findMany()
  
  if (existingFormats.length === 0) {
    await prisma.platformFormat.createMany({
      data: [
        {
          platform: 'META',
          formatName: 'Feed Image',
          width: 1080,
          height: 1080,
          aspectRatio: '1:1',
          maxFileSize: 4000,
          supportedTypes: ['jpg', 'png'],
          textMaxLength: 125,
        },
        {
          platform: 'GOOGLE',
          formatName: 'Display Ad',
          width: 336,
          height: 280,
          aspectRatio: '6:5',
          maxFileSize: 2000,
          supportedTypes: ['jpg', 'png', 'gif'],
          textMaxLength: 90,
        },
        {
          platform: 'TIKTOK',
          formatName: 'Feed Video',
          width: 1080,
          height: 1920,
          aspectRatio: '9:16',
          maxFileSize: 10000,
          supportedTypes: ['mp4', 'mov'],
          textMaxLength: 100,
        },
      ],
    })
    
    console.log('Created platform format specifications')
  }
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
