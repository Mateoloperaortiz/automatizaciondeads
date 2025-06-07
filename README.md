# Adflux: Automatización Inteligente de Anuncios de Empleo

Adflux es una plataforma avanzada que automatiza la publicación de anuncios de empleo en múltiples redes sociales (Meta, Google Ads y X), utilizando inteligencia artificial para segmentar y optimizar la audiencia de cada campaña. Nuestra solución ahorra tiempo, reduce costos y maximiza el alcance de tus vacantes, permitiéndote encontrar el mejor talento de manera eficiente y moderna.

---

## 🚀 ¿Qué hace Adflux?

- **Automatiza** la creación, segmentación y publicación de anuncios de empleo en Meta (Facebook/Instagram), Google Ads y X (Twitter) desde un solo lugar.
- **Segmenta audiencias** automáticamente usando IA y machine learning, analizando la descripción del puesto para identificar el público ideal.
- **Gestiona campañas**: programa, pausa, reactiva y archiva anuncios fácilmente desde un dashboard intuitivo.
- **Conexión Multi-Plataforma**: vincula tus cuentas de anuncios de Meta, Google y X una sola vez y publica en todas simultáneamente.
- **Gestión de equipos y roles**: organiza usuarios y equipos, con control de acceso y roles personalizados.
- **Suscripciones y pagos**: integra Stripe para la gestión de planes y pagos recurrentes.

---

## 🧠 Segmentación de Audiencia con IA

Cada vez que creas o programas un anuncio, Adflux analiza el texto y utiliza un microservicio Python con modelos de machine learning (Sentence-BERT, UMAP, K-Means) para:
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

### Add environment variables

In your Vercel project settings (or during deployment), add all the necessary environment variables. Make sure to update the values for the production environment, including:

1. `BASE_URL`: Set this to your production domain.
2. `STRIPE_WEBHOOK_SECRET`: Use the webhook secret from the production webhook you created in step 1.
3. `POSTGRES_URL`: Set this to your production database URL.
4. `AUTH_SECRET`: Set this to a random string. `openssl rand -base64 32` will generate one.

---

## Variables de entorno requeridas (`.env`)

Copia y personaliza estas variables en tu archivo `.env` en la raíz del proyecto:

```env
# Base de la aplicación
BASE_URL=http://localhost:3000
NEXT_PUBLIC_BASE_URL=http://localhost:3000

# Base de datos
POSTGRES_URL=postgres://usuario:contraseña@host:puerto/base_de_datos

# Autenticación
AUTH_SECRET=pon_aqui_un_string_secreto

# Stripe (pagos)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Cifrado
ENCRYPTION_KEY=pon_aqui_una_cadena_hexadecimal_de_64_caracteres

# Meta (Facebook/Instagram)
META_APP_ID=tu_app_id_de_meta
META_APP_SECRET=tu_app_secret_de_meta
META_DEFAULT_PAGE_ID=tu_page_id_de_facebook

# Google Ads
GOOGLE_CLIENT_ID=tu_google_client_id
GOOGLE_CLIENT_SECRET=tu_google_client_secret
GOOGLE_DEVELOPER_TOKEN=tu_google_developer_token
GOOGLE_LOGIN_CUSTOMER_ID=opcional_mcc_id
GOOGLE_ADS_CUSTOMER_ID_FOR_APP=tu_google_ads_customer_id

# X (Twitter)
X_CONSUMER_KEY=tu_consumer_key
X_CONSUMER_SECRET=tu_consumer_secret
X_ADS_ACCOUNT_ID=tu_ads_account_id
X_USER_ACCESS_TOKEN=tu_user_access_token
X_USER_ACCESS_TOKEN_SECRET=tu_user_access_token_secret

# OpenAI (opcional, para generación de anuncios con IA)
OPENAI_API_KEY=tu_openai_api_key

# Microservicio de segmentación (Python)
PYTHON_SEGMENTATION_SERVICE_URL=http://localhost:8000/segment

# Seguridad y automatización
CRON_JOB_SECRET=un_secreto_para_tus_cron_jobs
```