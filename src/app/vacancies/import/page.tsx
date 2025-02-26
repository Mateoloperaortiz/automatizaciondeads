'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

// Mock data for vacancies from ATS
const mockVacancies = [
  {
    id: 'v001',
    title: 'Senior Frontend Developer',
    location: 'San Francisco, CA',
    department: 'Engineering',
    status: 'Open',
    posted: '2025-02-10',
  },
  {
    id: 'v002',
    title: 'UX Designer',
    location: 'New York, NY',
    department: 'Design',
    status: 'Open',
    posted: '2025-02-12',
  },
  {
    id: 'v003',
    title: 'Product Manager',
    location: 'Remote',
    department: 'Product',
    status: 'Open',
    posted: '2025-02-15',
  },
  {
    id: 'v004',
    title: 'DevOps Engineer',
    location: 'Austin, TX',
    department: 'Engineering',
    status: 'Open',
    posted: '2025-02-18',
  },
  {
    id: 'v005',
    title: 'Marketing Specialist',
    location: 'Chicago, IL',
    department: 'Marketing',
    status: 'Open',
    posted: '2025-02-20',
  },
]

export default function ImportVacanciesPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDepartment, setSelectedDepartment] = useState('')
  const [selectedVacancies, setSelectedVacancies] = useState<string[]>([])
  const [isImporting, setIsImporting] = useState(false)
  const [importSuccess, setImportSuccess] = useState(false)
  
  // Filter vacancies based on search term and department
  const filteredVacancies = mockVacancies.filter(vacancy => {
    const matchesSearch = vacancy.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          vacancy.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDepartment = selectedDepartment === '' || vacancy.department === selectedDepartment
    return matchesSearch && matchesDepartment
  })
  
  // Get unique departments for filter
  const departments = Array.from(new Set(mockVacancies.map(v => v.department)))
  
  // Toggle vacancy selection
  const toggleVacancySelection = (id: string) => {
    setSelectedVacancies(prev => 
      prev.includes(id) 
        ? prev.filter(v => v !== id)
        : [...prev, id]
    )
  }
  
  // Select all visible vacancies
  const selectAllVacancies = () => {
    if (selectedVacancies.length === filteredVacancies.length) {
      // If all are selected, deselect all
      setSelectedVacancies([])
    } else {
      // Otherwise, select all filtered vacancies
      setSelectedVacancies(filteredVacancies.map(v => v.id))
    }
  }
  
  // Handle import button click
  const handleImport = async () => {
    if (selectedVacancies.length === 0) return
    
    setIsImporting(true)
    
    // Simulate API call to import vacancies
    try {
      // In a real app, this would be an API call to import the selected vacancies
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setImportSuccess(true)
      
      // Redirect to vacancies list after 1.5 seconds
      setTimeout(() => {
        router.push('/vacancies')
      }, 1500)
    } catch (error) {
      console.error('Error importing vacancies:', error)
    } finally {
      setIsImporting(false)
    }
  }
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Import Vacancies from ATS</h1>
        <Link href="/vacancies" className="btn-outline text-sm">
          Cancel
        </Link>
      </div>
      
      {/* Success message */}
      {importSuccess && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-800 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="font-medium">Vacancies imported successfully!</p>
              <p className="text-sm">Redirecting to vacancies list...</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="card mb-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Search and Filter</h2>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="search" className="sr-only">
                Search
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                </div>
                <input
                  id="search"
                  type="text"
                  placeholder="Search by title or location"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-64">
              <label htmlFor="department" className="sr-only">
                Department
              </label>
              <select
                id="department"
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="input"
              >
                <option value="">All Departments</option>
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
        
        <div>
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-semibold">Available Vacancies</h2>
            <button
              onClick={selectAllVacancies}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              {selectedVacancies.length === filteredVacancies.length
                ? 'Deselect All'
                : 'Select All'}
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-md overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="w-12 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedVacancies.length === filteredVacancies.length && filteredVacancies.length > 0}
                      onChange={selectAllVacancies}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                  </th>
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
                    Posted
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredVacancies.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-4 text-center text-gray-500">
                      No vacancies found matching your criteria
                    </td>
                  </tr>
                ) : (
                  filteredVacancies.map((vacancy) => (
                    <tr 
                      key={vacancy.id} 
                      className={selectedVacancies.includes(vacancy.id) ? 'bg-primary-50' : 'hover:bg-gray-50'}
                      onClick={() => toggleVacancySelection(vacancy.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td className="px-4 py-4 whitespace-nowrap">
                        <input
                          type="checkbox"
                          checked={selectedVacancies.includes(vacancy.id)}
                          onChange={() => toggleVacancySelection(vacancy.id)}
                          onClick={(e) => e.stopPropagation()}
                          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                        />
                      </td>
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
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(vacancy.posted).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div className="flex justify-between">
        <div>
          <span className="text-sm text-gray-600">
            {selectedVacancies.length} vacancies selected
          </span>
        </div>
        <div className="flex gap-3">
          <Link href="/vacancies" className="btn-outline">
            Cancel
          </Link>
          <button
            onClick={handleImport}
            disabled={selectedVacancies.length === 0 || isImporting}
            className={`btn-primary ${(selectedVacancies.length === 0 || isImporting) ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isImporting ? 'Importing...' : `Import ${selectedVacancies.length} Vacancies`}
          </button>
        </div>
      </div>
    </div>
  )
}
