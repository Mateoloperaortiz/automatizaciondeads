# InspireAI: Automatización Inteligente de Anuncios de Empleo

InspireAI es una plataforma avanzada que automatiza la publicación de anuncios de empleo en múltiples redes sociales (Meta, Google Ads y X), utilizando inteligencia artificial para segmentar y optimizar la audiencia de cada campaña. Nuestra solución ahorra tiempo, reduce costos y maximiza el alcance de tus vacantes, permitiéndote encontrar el mejor talento de manera eficiente y moderna.

---

## 🚀 ¿Qué hace InspireAI?

- **Automatiza** la creación, segmentación y publicación de anuncios de empleo en Meta (Facebook/Instagram), Google Ads y X (Twitter) desde un solo lugar.
- **Segmenta audiencias** automáticamente usando IA y machine learning, analizando la descripción del puesto para identificar el público ideal.
- **Gestiona campañas**: programa, pausa, reactiva y archiva anuncios fácilmente desde un dashboard intuitivo.
- **Conexión Multi-Plataforma**: vincula tus cuentas de anuncios de Meta, Google y X una sola vez y publica en todas simultáneamente.
- **Gestión de equipos y roles**: organiza usuarios y equipos, con control de acceso y roles personalizados.
- **Suscripciones y pagos**: integra Stripe para la gestión de planes y pagos recurrentes.

---

## 🧠 Segmentación de Audiencia con IA

Cada vez que creas o programas un anuncio, InspireAI analiza el texto y utiliza un microservicio Python con modelos de machine learning (Sentence-BERT, UMAP, K-Means) para:
- Extraer las características clave del puesto (industria, habilidades, seniority, palabras clave).
- Asignar el anuncio a un perfil de audiencia óptimo, con un nivel de confianza visualizable en el dashboard.
- Mapear la segmentación a los parámetros específicos de cada plataforma publicitaria.
- Adaptar la estrategia automáticamente si la confianza es baja, garantizando siempre la entrega del anuncio.

---

## 🏗️ Arquitectura y Tecnologías

- **Frontend & Backend:** Next.js (App Router), TypeScript, TailwindCSS, shadcn/ui.
- **Base de datos:** PostgreSQL gestionado con Drizzle ORM.
- **Pagos:** Stripe para suscripciones y portal de clientes.
- **Microservicio de IA:** Python (FastAPI, Sentence-BERT, UMAP, K-Means) para segmentación avanzada de audiencias.
- **Automatización:** Orquestación de campañas, programación y logging de resultados.
- **Seguridad:** Tokens y credenciales cifrados, autenticación robusta y control de acceso por roles.

---

## ✨ Características Destacadas

- **Dashboard centralizado** para gestión de anuncios, equipos y conexiones.
- **CRUD completo** de anuncios de empleo y conexiones de plataformas.
- **Visualización de segmentación**: confianza, perfil asignado y parámetros de targeting.
- **Pruebas de segmentación en tiempo real** antes de publicar.
- **Automatización de campañas**: desde la creación hasta el monitoreo de resultados.
- **Soporte para múltiples equipos y usuarios.**

---

## 🚦 Comenzando

```bash
git clone https://github.com/nextjs/saas-starter
cd saas-starter
pnpm install
```

## 🖥️ Ejecución Local

[Instala](https://docs.stripe.com/stripe-cli) y accede a tu cuenta de Stripe:

```bash
stripe login
```

Ejecuta las migraciones de base de datos y siembra los datos iniciales (usuario y equipo de prueba):

```bash
pnpm db:migrate
pnpm db:seed
```

Esto creará el siguiente usuario y equipo de prueba:

- Usuario: `test@test.com`
- Contraseña: `admin123`

También puedes crear nuevos usuarios desde la ruta `/sign-up`.

Por último, inicia el servidor de desarrollo de Next.js:

```bash
pnpm dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador para ver la aplicación en acción.

You can listen for Stripe webhooks locally through their CLI to handle subscription change events:

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```

## Going to Production

When you're ready to deploy your SaaS application to production, follow these steps:

### Set up a production Stripe webhook

1. Go to the Stripe Dashboard and create a new webhook for your production environment.
2. Set the endpoint URL to your production API route (e.g., `https://yourdomain.com/api/stripe/webhook`).
3. Select the events you want to listen for (e.g., `checkout.session.completed`, `customer.subscription.updated`).

### Deploy to Vercel

1. Push your code to a GitHub repository.
2. Connect your repository to [Vercel](https://vercel.com/) and deploy it.
3. Follow the Vercel deployment process, which will guide you through setting up your project.

### Add environment variables

In your Vercel project settings (or during deployment), add all the necessary environment variables. Make sure to update the values for the production environment, including:

1. `BASE_URL`: Set this to your production domain.
2. `STRIPE_WEBHOOK_SECRET`: Use the webhook secret from the production webhook you created in step 1.
3. `POSTGRES_URL`: Set this to your production database URL.
4. `AUTH_SECRET`: Set this to a random string. `openssl rand -base64 32` will generate one.

## Other Templates

While this template is intentionally minimal and to be used as a learning resource, there are other paid versions in the community which are more full-featured:

- https://achromatic.dev
- https://shipfa.st
- https://makerkit.dev
- https://zerotoshipped.com 