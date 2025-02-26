// ATS Client for importing vacancies
// This is a mock implementation for the POC

import { z } from 'zod'

// Define schemas for ATS data
const ATSVacancySchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  location: z.string(),
  department: z.string(),
  status: z.string(),
  posted_date: z.string(),
  closing_date: z.string().optional(),
  salary_range: z.object({
    min: z.number().optional(),
    max: z.number().optional(),
    currency: z.string().optional(),
  }).optional(),
  required_skills: z.array(z.string()).optional(),
  employment_type: z.string().optional(),
})

export type ATSVacancy = z.infer<typeof ATSVacancySchema>

// Mock data for ATS vacancies
const mockATSVacancies: ATSVacancy[] = [
  {
    id: 'v001',
    title: 'Senior Frontend Developer',
    description: 'We are looking for a Senior Frontend Developer with experience in React, TypeScript, and modern web development practices.',
    location: 'San Francisco, CA',
    department: 'Engineering',
    status: 'OPEN',
    posted_date: '2025-02-10',
    employment_type: 'FULL_TIME',
    required_skills: ['React', 'TypeScript', 'HTML', 'CSS'],
  },
  {
    id: 'v002',
    title: 'UX Designer',
    description: 'Join our design team to create user-centered designs for our products.',
    location: 'New York, NY',
    department: 'Design',
    status: 'OPEN',
    posted_date: '2025-02-12',
    employment_type: 'FULL_TIME',
    required_skills: ['Figma', 'User Research', 'Prototyping'],
  },
  {
    id: 'v003',
    title: 'Product Manager',
    description: 'Lead the development of our products from conception to launch.',
    location: 'Remote',
    department: 'Product',
    status: 'OPEN',
    posted_date: '2025-02-15',
    employment_type: 'FULL_TIME',
    required_skills: ['Product Strategy', 'Agile', 'User Stories'],
  },
  {
    id: 'v004',
    title: 'DevOps Engineer',
    description: 'Manage our cloud infrastructure and CI/CD pipelines.',
    location: 'Austin, TX',
    department: 'Engineering',
    status: 'OPEN',
    posted_date: '2025-02-18',
    employment_type: 'FULL_TIME',
    required_skills: ['AWS', 'Docker', 'Kubernetes', 'CI/CD'],
  },
  {
    id: 'v005',
    title: 'Marketing Specialist',
    description: 'Create and execute marketing campaigns for our products.',
    location: 'Chicago, IL',
    department: 'Marketing',
    status: 'OPEN',
    posted_date: '2025-02-20',
    employment_type: 'FULL_TIME',
    required_skills: ['Social Media Marketing', 'Content Creation', 'Analytics'],
  },
]

export class ATSClient {
  private apiUrl: string
  private apiKey: string
  
  constructor(apiUrl: string, apiKey: string) {
    this.apiUrl = apiUrl
    this.apiKey = apiKey
  }
  
  // Get all vacancies from ATS
  async getVacancies(): Promise<ATSVacancy[]> {
    // In a real implementation, this would make an API call to the ATS
    // For the POC, we'll return the mock data
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    return mockATSVacancies
  }
  
  // Get a single vacancy by ID
  async getVacancy(id: string): Promise<ATSVacancy | null> {
    // In a real implementation, this would make an API call to the ATS
    // For the POC, we'll return the mock data
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const vacancy = mockATSVacancies.find(v => v.id === id)
    return vacancy || null
  }
  
  // Transform ATS vacancy to our database format
  transformVacancyForImport(atsVacancy: ATSVacancy, userId: string) {
    return {
      atsId: atsVacancy.id,
      title: atsVacancy.title,
      description: atsVacancy.description,
      location: atsVacancy.location,
      department: atsVacancy.department,
      status: 'DRAFT', // Default status for imported vacancies
      importedBy: userId,
    }
  }
}
