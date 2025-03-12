import Link from 'next/link';
import Image from 'next/image';
import { Button } from './button';

export function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-2.5 fixed w-full top-0 left-0 z-50">
      <div className="flex flex-wrap justify-between items-center">
        <div className="flex items-center">
          <Link href="/" className="flex items-center">
            <span className="self-center text-2xl font-semibold text-magneto-purple whitespace-nowrap">
              Ads<span className="text-magneto-orange">Master</span>
            </span>
          </Link>
        </div>
        
        <div className="flex items-center lg:order-2">
          <Button variant="default" size="sm" className="mr-2">
            Iniciar Sesión
          </Button>
          <Button variant="secondary" size="sm">
            Registrarse
          </Button>
          <button 
            type="button" 
            className="inline-flex items-center p-2 ml-1 text-sm text-gray-500 rounded-lg lg:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
          >
            <span className="sr-only">Abrir menú</span>
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"></path>
            </svg>
            <svg className="hidden w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"></path>
            </svg>
          </button>
        </div>
        
        <div className="hidden justify-between items-center w-full lg:flex lg:w-auto lg:order-1">
          <ul className="flex flex-col mt-4 font-medium lg:flex-row lg:space-x-8 lg:mt-0">
            <li>
              <Link href="/" className="block py-2 pr-4 pl-3 text-white rounded bg-magneto-purple lg:bg-transparent lg:text-magneto-purple lg:p-0">
                Inicio
              </Link>
            </li>
            <li>
              <Link href="/dashboard" className="block py-2 pr-4 pl-3 text-gray-700 border-b border-gray-100 hover:bg-gray-50 lg:hover:bg-transparent lg:border-0 lg:hover:text-magneto-orange lg:p-0">
                Dashboard
              </Link>
            </li>
            <li>
              <Link href="/create" className="block py-2 pr-4 pl-3 text-gray-700 border-b border-gray-100 hover:bg-gray-50 lg:hover:bg-transparent lg:border-0 lg:hover:text-magneto-orange lg:p-0">
                Crear Anuncio
              </Link>
            </li>
            <li>
              <Link href="/analytics" className="block py-2 pr-4 pl-3 text-gray-700 border-b border-gray-100 hover:bg-gray-50 lg:hover:bg-transparent lg:border-0 lg:hover:text-magneto-orange lg:p-0">
                Analíticas
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
