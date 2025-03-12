import Image from 'next/image';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4">
          AdsMaster - Automatización de anuncios
        </p>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-white via-white lg:static lg:h-auto lg:w-auto lg:bg-none">
          <a
            className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0"
            href="https://www.magneto365.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            Powered by Magneto365
          </a>
        </div>
      </div>

      <div className="relative flex place-items-center">
        <h1 className="text-5xl font-bold text-magneto-purple">
          AdsMaster <span className="text-magneto-orange">Platform</span>
        </h1>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 lg:text-left">
        <Link
          href="/dashboard"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className={`mb-3 text-2xl font-semibold text-magneto-purple`}>
            Dashboard{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              →
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Visualiza y gestiona tus campañas de anuncios.
          </p>
        </Link>

        <Link
          href="/create"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className={`mb-3 text-2xl font-semibold text-magneto-purple`}>
            Crear Anuncio{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              →
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Crea y automatiza anuncios de empleo para múltiples plataformas.
          </p>
        </Link>

        <Link
          href="/analytics"
          className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100"
        >
          <h2 className={`mb-3 text-2xl font-semibold text-magneto-purple`}>
            Analíticas{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              →
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Analiza el rendimiento de tus campañas y optimiza tus resultados.
          </p>
        </Link>
      </div>

      <div className="mt-10 p-6 bg-magneto-purple text-white rounded-lg w-full max-w-2xl">
        <h3 className="text-xl font-bold mb-2">Sobre AdsMaster</h3>
        <p className="text-sm">
          La plataforma AdsMaster automatiza la creación y publicación de anuncios de vacantes 
          laborales en múltiples canales de redes sociales. Nuestro objetivo es minimizar los 
          procesos manuales, agilizar los flujos de trabajo de reclutamiento y proporcionar 
          análisis unificados para mejorar los resultados de reclutamiento.
        </p>
        <div className="mt-4 p-3 bg-magneto-orange rounded-md">
          <p className="text-xs font-bold">
            Nuestro objetivo: Reducir el tiempo dedicado a la creación de anuncios en un 70% y 
            disminuir las métricas de costo por aplicación en un 25%.
          </p>
        </div>
      </div>
    </main>
  );
}
