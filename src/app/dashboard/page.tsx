import { Button } from '@/components/ui/button';

export default function Dashboard() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-primary mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-primary mb-2">Anuncios Activos</h2>
          <p className="text-4xl font-bold">12</p>
          <p className="text-sm text-gray-500">+3 desde el mes pasado</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-primary mb-2">Aplicaciones</h2>
          <p className="text-4xl font-bold">248</p>
          <p className="text-sm text-gray-500">+24% desde el mes pasado</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-primary mb-2">Costo por Aplicación</h2>
          <p className="text-4xl font-bold">$12.40</p>
          <p className="text-sm text-gray-500">-18% desde el mes pasado</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-primary">Anuncios Recientes</h2>
          <Button variant="secondary" size="sm">Ver Todos</Button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th className="px-6 py-3">Título</th>
                <th className="px-6 py-3">Plataforma</th>
                <th className="px-6 py-3">Estado</th>
                <th className="px-6 py-3">Aplicaciones</th>
                <th className="px-6 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr className="bg-white border-b">
                <td className="px-6 py-4 font-medium">Desarrollador Frontend</td>
                <td className="px-6 py-4">LinkedIn, Facebook</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Activo</span>
                </td>
                <td className="px-6 py-4">45</td>
                <td className="px-6 py-4">
                  <Button variant="link" size="sm">Editar</Button>
                </td>
              </tr>
              <tr className="bg-white border-b">
                <td className="px-6 py-4 font-medium">Diseñador UX/UI</td>
                <td className="px-6 py-4">Instagram, LinkedIn</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Activo</span>
                </td>
                <td className="px-6 py-4">32</td>
                <td className="px-6 py-4">
                  <Button variant="link" size="sm">Editar</Button>
                </td>
              </tr>
              <tr className="bg-white">
                <td className="px-6 py-4 font-medium">Desarrollador Backend</td>
                <td className="px-6 py-4">LinkedIn</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Pendiente</span>
                </td>
                <td className="px-6 py-4">0</td>
                <td className="px-6 py-4">
                  <Button variant="link" size="sm">Editar</Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-primary">Rendimiento por Plataforma</h2>
          <div>
            <select className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg p-2.5">
              <option>Últimos 30 días</option>
              <option>Últimos 60 días</option>
              <option>Últimos 90 días</option>
            </select>
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">LinkedIn</span>
              <span className="text-sm font-medium">78%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-secondary h-2.5 rounded-full" style={{ width: '78%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Facebook</span>
              <span className="text-sm font-medium">62%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-primary h-2.5 rounded-full" style={{ width: '62%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Instagram</span>
              <span className="text-sm font-medium">45%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: '45%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium">Twitter</span>
              <span className="text-sm font-medium">32%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '32%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
