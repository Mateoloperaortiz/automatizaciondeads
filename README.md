# AdsMaster - Plataforma de Automatización de Anuncios

AdsMaster es una plataforma diseñada para automatizar la creación y publicación de anuncios de vacantes laborales en múltiples canales de redes sociales para Magneto365. La plataforma busca minimizar los procesos manuales, agilizar los flujos de trabajo de reclutamiento y proporcionar análisis unificados para mejorar los resultados de reclutamiento.

## Objetivos

- Reducir el tiempo dedicado a la creación de anuncios en un 70%
- Disminuir las métricas de costo por aplicación en un 25%

## Tecnologías Utilizadas

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript
- **Estilos**: Tailwind CSS, Shadcn UI
- **Despliegue**: Vercel (recomendado)

## Estructura del Proyecto

- `src/app`: Contiene las páginas principales de la aplicación utilizando el paradigma App Router de Next.js 14
- `src/components`: Componentes UI reutilizables
- `src/lib`: Utilidades y funciones auxiliares

## Paleta de Colores de Magneto365

La aplicación utiliza los colores corporativos de Magneto365:

- **Púrpura (#5D3B90)**: Color principal de la marca, utilizado en logos y elementos principales de la UI
- **Naranja (#FF6B00)**: Color de acento secundario, utilizado para CTAs y destacados
- **Blanco (#FFFFFF)**: Utilizado para fondos y texto sobre fondos oscuros
- **Gris Oscuro (#333333)**: Utilizado para texto y elementos secundarios de la UI

## Instalación

1. Clona este repositorio:
```bash
git clone <url-del-repositorio>
cd automatizaciondeads
```

2. Instala las dependencias:
```bash
npm install
```

3. Ejecuta el servidor de desarrollo:
```bash
npm run dev
```

4. Abre [http://localhost:3000](http://localhost:3000) en tu navegador para ver la aplicación.

## Funcionalidades Principales

- **Dashboard**: Visualización de métricas clave y rendimiento de anuncios
- **Creación de Anuncios**: Formulario intuitivo para crear y automatizar anuncios de empleo
- **Analíticas**: Análisis detallado del rendimiento de las campañas y demografía de los aplicantes

## Despliegue

Para desplegar la aplicación en producción:

```bash
npm run build
npm start
```

Para un despliegue más sencillo, se recomienda utilizar Vercel, que se integra perfectamente con Next.js.

## Licencia

Este proyecto es propiedad de Magneto365 y está destinado únicamente para uso interno.
