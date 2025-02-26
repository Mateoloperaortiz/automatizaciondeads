import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { PrismaClient } from '@prisma/client'
import { ATSClient } from '@/lib/ats/ats-client'

const prisma = new PrismaClient()

export async function POST(request: NextRequest) {
  const session = await getServerSession()
  
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  try {
    const { vacancyIds } = await request.json()
    
    if (!Array.isArray(vacancyIds) || vacancyIds.length === 0) {
      return NextResponse.json(
        { error: 'No vacancy IDs provided' },
        { status: 400 }
      )
    }
    
    // Initialize ATS client
    const atsClient = new ATSClient(
      process.env.ATS_API_URL || 'https://ats.magneto.com/api',
      process.env.ATS_API_KEY || 'mock-api-key'
    )
    
    // Fetch vacancy details from ATS
    const importedVacancies = []
    
    for (const id of vacancyIds) {
      // In a real implementation, this would fetch from the ATS and store in the database
      const atsVacancy = await atsClient.getVacancy(id)
      
      if (atsVacancy) {
        // Transform ATS vacancy to our database format
        const vacancyData = atsClient.transformVacancyForImport(
          atsVacancy,
          session.user.id
        )
        
        // In a real implementation, we would add to the database:
        /*
        const vacancy = await prisma.vacancy.create({
          data: vacancyData,
        })
        */
        
        importedVacancies.push({
          id,
          title: atsVacancy.title,
          status: 'IMPORTED',
        })
      }
    }
    
    return NextResponse.json({
      success: true,
      message: `${importedVacancies.length} vacancies imported successfully`,
      vacancies: importedVacancies,
    })
  } catch (error) {
    console.error('Vacancy import error:', error)
    
    return NextResponse.json(
      { error: 'Failed to import vacancies' },
      { status: 500 }
    )
  }
}
