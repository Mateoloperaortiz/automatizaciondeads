import { getServerSession } from 'next-auth/next'
import { redirect } from 'next/navigation'
import Link from 'next/link'

// Mock data for imported vacancies with Colombian context
const mockVacancies = [
  {
    id: 'v001',
    title: 'Desarrollador Frontend Senior',
    location: 'Bogotá, Colombia',
    department: 'Ingeniería',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v002',
    title: 'Diseñador UX/UI',
    location: 'Medellín, Colombia',
    department: 'Diseño',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v003',
    title: 'Gerente de Producto',
    location: 'Remoto (Colombia)',
    department: 'Producto',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v004',
    title: 'Ingeniero DevOps',
    location: 'Cali, Colombia',
    department: 'Operaciones',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v005',
    title: 'Especialista en Marketing Digital',
    location: 'Barranquilla, Colombia',
    department: 'Marketing',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v006',
    title: 'Analista de Recursos Humanos',
    location: 'Cartagena, Colombia',
    department: 'Recursos Humanos',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
  {
    id: 'v007',
    title: 'Especialista en Comercio Electrónico',
    location: 'Bogotá, Colombia',
    department: 'Comercial',
    status: 'DRAFT',
    imported: '2025-02-25',
  },
]

export default async function VacanciesPage() {
  const session = await getServerSession()
  
  if (!session) {
    redirect('/auth/login')
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Vacancies</h1>
        <Link href="/vacancies/import" className="btn-primary">
          Import from ATS
        </Link>
      </div>
      
      <div className="card">
        <div className="border border-gray-200 rounded-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Imported
                </th>
                <th scope="col" className="relative px-4 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockVacancies.map((vacancy) => (
                <tr key={vacancy.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{vacancy.title}</div>
                    <div className="text-sm text-gray-500">ID: {vacancy.id}</div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {vacancy.location}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {vacancy.department}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      {vacancy.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(vacancy.imported).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link href={`/campaigns/create?vacancyId=${vacancy.id}`} className="text-primary-600 hover:text-primary-900 mr-4">
                      Create Campaign
                    </Link>
                    <Link href={`/vacancies/${vacancy.id}`} className="text-gray-600 hover:text-gray-900">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
