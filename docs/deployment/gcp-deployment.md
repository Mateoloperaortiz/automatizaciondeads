# Deploying AdFlux on Google Cloud Platform

This guide provides step-by-step instructions for deploying AdFlux on Google Cloud Platform (GCP).

## Overview

AdFlux can be deployed on GCP using the following services:

- **App Engine**: Hosts the Flask application
- **Cloud SQL**: Provides managed PostgreSQL database
- **Cloud Storage**: Stores static files and uploads
- **Cloud Run**: Runs Celery workers
- **Memorystore**: Provides Redis for Celery broker
- **Cloud Logging**: Centralizes application logs
- **Cloud Monitoring**: Tracks application performance

## Prerequisites

Before you begin, ensure you have:

1. A Google Cloud Platform account
2. Google Cloud SDK installed and configured
3. Access to the AdFlux codebase
4. Necessary API credentials for Meta and Google Ads

## Step 1: Create a GCP Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project"
3. Enter a project name (e.g., "adflux-production")
4. Select an organization and billing account
5. Click "Create"

## Step 2: Enable Required APIs

Enable the following APIs for your project:

```bash
gcloud services enable appengine.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

## Step 3: Set Up Cloud SQL

1. Create a PostgreSQL instance:

```bash
gcloud sql instances create adflux-db \
  --database-version=POSTGRES_13 \
  --tier=db-g1-small \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=10GB \
  --availability-type=ZONAL \
  --backup-start-time=04:00 \
  --enable-bin-log
```

2. Create a database:

```bash
gcloud sql databases create adflux \
  --instance=adflux-db
```

3. Create a user:

```bash
gcloud sql users create adflux-user \
  --instance=adflux-db \
  --password=YOUR_SECURE_PASSWORD
```

Note: Replace `YOUR_SECURE_PASSWORD` with a secure password.

## Step 4: Set Up Cloud Storage

1. Create a bucket for static files:

```bash
gsutil mb -l us-central1 gs://adflux-static
```

2. Make the bucket publicly readable:

```bash
gsutil iam ch allUsers:objectViewer gs://adflux-static
```

3. Create a bucket for uploads:

```bash
gsutil mb -l us-central1 gs://adflux-uploads
```

## Step 5: Set Up Memorystore (Redis)

1. Create a Redis instance:

```bash
gcloud redis instances create adflux-redis \
  --size=1 \
  --region=us-central1 \
  --zone=us-central1-a \
  --redis-version=redis_6_x \
  --tier=basic
```

2. Note the Redis instance IP address:

```bash
gcloud redis instances describe adflux-redis \
  --region=us-central1 \
  --format='value(host)'
```

## Step 6: Configure App Engine

1. Create an `app.yaml` file in the root of your project:

```yaml
runtime: python39
entrypoint: gunicorn -b :$PORT run:app

env_variables:
  DATABASE_URL: postgresql+pg8000://adflux-user:YOUR_SECURE_PASSWORD@/adflux?unix_sock=/cloudsql/YOUR_PROJECT_ID:us-central1:adflux-db/.s.PGSQL.5432
  SECRET_KEY: YOUR_SECRET_KEY
  STATIC_URL: https://storage.googleapis.com/adflux-static/
  UPLOAD_BUCKET: adflux-uploads
  CELERY_BROKER_URL: redis://REDIS_IP:6379/0
  CELERY_RESULT_BACKEND: redis://REDIS_IP:6379/0
  META_APP_ID: YOUR_META_APP_ID
  META_APP_SECRET: YOUR_META_APP_SECRET
  META_ACCESS_TOKEN: YOUR_META_ACCESS_TOKEN
  META_AD_ACCOUNT_ID: YOUR_META_AD_ACCOUNT_ID
  META_PAGE_ID: YOUR_META_PAGE_ID
  GOOGLE_ADS_DEVELOPER_TOKEN: YOUR_GOOGLE_ADS_DEVELOPER_TOKEN
  GOOGLE_ADS_CLIENT_ID: YOUR_GOOGLE_ADS_CLIENT_ID
  GOOGLE_ADS_CLIENT_SECRET: YOUR_GOOGLE_ADS_CLIENT_SECRET
  GOOGLE_ADS_REFRESH_TOKEN: YOUR_GOOGLE_ADS_REFRESH_TOKEN
  GOOGLE_ADS_LOGIN_CUSTOMER_ID: YOUR_GOOGLE_ADS_LOGIN_CUSTOMER_ID
  GOOGLE_ADS_TARGET_CUSTOMER_ID: YOUR_GOOGLE_ADS_TARGET_CUSTOMER_ID
  GOOGLE_ADS_USE_PROTO_PLUS: "True"
  GEMINI_API_KEY: YOUR_GEMINI_API_KEY
  GEMINI_MODEL: models/gemini-2.5-pro-exp-03-25

beta_settings:
  cloud_sql_instances: YOUR_PROJECT_ID:us-central1:adflux-db
```

Replace the following placeholders:
- `YOUR_SECURE_PASSWORD`: The password for the database user
- `YOUR_PROJECT_ID`: Your GCP project ID
- `YOUR_SECRET_KEY`: A secure random string for Flask's secret key
- `REDIS_IP`: The IP address of your Redis instance
- All API credentials with your actual credentials

## Step 7: Deploy the Application

1. Deploy static files to Cloud Storage:

```bash
gsutil -m cp -r adflux/static/* gs://adflux-static/
```

2. Deploy the application to App Engine:

```bash
gcloud app deploy app.yaml
```

## Step 8: Set Up Cloud Run for Celery Workers

1. Create a `Dockerfile` for the Celery worker:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "adflux.extensions.celery", "worker", "--loglevel=info"]
```

2. Build and push the Docker image:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/adflux-worker
```

3. Deploy the Celery worker to Cloud Run:

```bash
gcloud run deploy adflux-worker \
  --image gcr.io/YOUR_PROJECT_ID/adflux-worker \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars="DATABASE_URL=postgresql+pg8000://adflux-user:YOUR_SECURE_PASSWORD@/adflux?unix_sock=/cloudsql/YOUR_PROJECT_ID:us-central1:adflux-db/.s.PGSQL.5432,CELERY_BROKER_URL=redis://REDIS_IP:6379/0,CELERY_RESULT_BACKEND=redis://REDIS_IP:6379/0,META_APP_ID=YOUR_META_APP_ID,META_APP_SECRET=YOUR_META_APP_SECRET,META_ACCESS_TOKEN=YOUR_META_ACCESS_TOKEN,META_AD_ACCOUNT_ID=YOUR_META_AD_ACCOUNT_ID,META_PAGE_ID=YOUR_META_PAGE_ID,GOOGLE_ADS_DEVELOPER_TOKEN=YOUR_GOOGLE_ADS_DEVELOPER_TOKEN,GOOGLE_ADS_CLIENT_ID=YOUR_GOOGLE_ADS_CLIENT_ID,GOOGLE_ADS_CLIENT_SECRET=YOUR_GOOGLE_ADS_CLIENT_SECRET,GOOGLE_ADS_REFRESH_TOKEN=YOUR_GOOGLE_ADS_REFRESH_TOKEN,GOOGLE_ADS_LOGIN_CUSTOMER_ID=YOUR_GOOGLE_ADS_LOGIN_CUSTOMER_ID,GOOGLE_ADS_TARGET_CUSTOMER_ID=YOUR_GOOGLE_ADS_TARGET_CUSTOMER_ID,GOOGLE_ADS_USE_PROTO_PLUS=True,GEMINI_API_KEY=YOUR_GEMINI_API_KEY,GEMINI_MODEL=models/gemini-2.5-pro-exp-03-25" \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:adflux-db \
  --no-allow-unauthenticated
```

4. Deploy the Celery beat scheduler to Cloud Run:

```bash
gcloud run deploy adflux-beat \
  --image gcr.io/YOUR_PROJECT_ID/adflux-worker \
  --platform managed \
  --region us-central1 \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 1 \
  --command celery \
  --args "-A,adflux.extensions.celery,beat,--loglevel=info" \
  --set-env-vars="DATABASE_URL=postgresql+pg8000://adflux-user:YOUR_SECURE_PASSWORD@/adflux?unix_sock=/cloudsql/YOUR_PROJECT_ID:us-central1:adflux-db/.s.PGSQL.5432,CELERY_BROKER_URL=redis://REDIS_IP:6379/0,CELERY_RESULT_BACKEND=redis://REDIS_IP:6379/0,META_APP_ID=YOUR_META_APP_ID,META_APP_SECRET=YOUR_META_APP_SECRET,META_ACCESS_TOKEN=YOUR_META_ACCESS_TOKEN,META_AD_ACCOUNT_ID=YOUR_META_AD_ACCOUNT_ID,META_PAGE_ID=YOUR_META_PAGE_ID,GOOGLE_ADS_DEVELOPER_TOKEN=YOUR_GOOGLE_ADS_DEVELOPER_TOKEN,GOOGLE_ADS_CLIENT_ID=YOUR_GOOGLE_ADS_CLIENT_ID,GOOGLE_ADS_CLIENT_SECRET=YOUR_GOOGLE_ADS_CLIENT_SECRET,GOOGLE_ADS_REFRESH_TOKEN=YOUR_GOOGLE_ADS_REFRESH_TOKEN,GOOGLE_ADS_LOGIN_CUSTOMER_ID=YOUR_GOOGLE_ADS_LOGIN_CUSTOMER_ID,GOOGLE_ADS_TARGET_CUSTOMER_ID=YOUR_GOOGLE_ADS_TARGET_CUSTOMER_ID,GOOGLE_ADS_USE_PROTO_PLUS=True,GEMINI_API_KEY=YOUR_GEMINI_API_KEY,GEMINI_MODEL=models/gemini-2.5-pro-exp-03-25" \
  --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:adflux-db \
  --no-allow-unauthenticated
```

## Step 9: Run Database Migrations

1. Create a `migrate.yaml` file for a one-time migration job:

```yaml
runtime: python39
service: migrate
entrypoint: flask db upgrade

env_variables:
  DATABASE_URL: postgresql+pg8000://adflux-user:YOUR_SECURE_PASSWORD@/adflux?unix_sock=/cloudsql/YOUR_PROJECT_ID:us-central1:adflux-db/.s.PGSQL.5432
  FLASK_APP: run.py

beta_settings:
  cloud_sql_instances: YOUR_PROJECT_ID:us-central1:adflux-db

manual_scaling:
  instances: 1

inbound_services:
- warmup
```

2. Deploy the migration job:

```bash
gcloud app deploy migrate.yaml
```

3. After the migration is complete, you can delete the service:

```bash
gcloud app services delete migrate
```

## Step 10: Set Up Monitoring and Logging

1. Create a custom dashboard in Cloud Monitoring:

```bash
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard.json
```

2. Set up log-based metrics:

```bash
gcloud logging metrics create adflux-errors \
  --description="Count of error logs from AdFlux" \
  --log-filter="resource.type=gae_app AND severity>=ERROR"
```

3. Create alerts:

```bash
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/alerts.json
```

## Step 11: Set Up Scheduled Backups

1. Create a Cloud Scheduler job for database backups:

```bash
gcloud scheduler jobs create http adflux-db-backup \
  --schedule="0 2 * * *" \
  --uri="https://sqladmin.googleapis.com/v1/projects/YOUR_PROJECT_ID/instances/adflux-db/backupRuns" \
  --http-method=POST \
  --oauth-service-account-email=YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --oauth-token-scope=https://www.googleapis.com/auth/cloud-platform
```

## Step 12: Verify Deployment

1. Access your application:

```bash
gcloud app browse
```

2. Check the logs:

```bash
gcloud app logs tail
```

3. Monitor Celery workers:

```bash
gcloud run services describe adflux-worker
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Verify the Cloud SQL instance is running:

```bash
gcloud sql instances describe adflux-db
```

2. Check the connection string in `app.yaml`
3. Ensure the service account has the necessary permissions

### Celery Worker Issues

If Celery workers are not processing tasks:

1. Check the Redis connection:

```bash
gcloud redis instances describe adflux-redis --region=us-central1
```

2. Verify the Celery worker logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=adflux-worker"
```

3. Ensure the environment variables are correctly set

### Static Files Not Loading

If static files are not loading:

1. Check the Cloud Storage bucket:

```bash
gsutil ls gs://adflux-static/
```

2. Verify the `STATIC_URL` environment variable
3. Ensure the bucket is publicly readable

## Security Considerations

1. **API Credentials**: Store sensitive API credentials in Secret Manager instead of environment variables
2. **Database Access**: Restrict access to the Cloud SQL instance
3. **Cloud Run Services**: Use service accounts with minimal permissions
4. **Network Security**: Configure VPC Service Controls for additional security

## Performance Optimization

1. **App Engine Scaling**: Configure automatic scaling based on load
2. **Cloud SQL**: Monitor and optimize database performance
3. **Redis**: Monitor Redis memory usage and consider scaling if needed
4. **Cloud CDN**: Enable Cloud CDN for static assets

## Cost Optimization

1. **App Engine**: Use automatic scaling to reduce costs during low-traffic periods
2. **Cloud SQL**: Choose an appropriate instance size
3. **Cloud Run**: Configure concurrency and maximum instances
4. **Monitoring**: Set up budget alerts to avoid unexpected costs

## Next Steps

1. [Set up custom domain](https://cloud.google.com/appengine/docs/standard/python3/mapping-custom-domains)
2. [Configure SSL/TLS](https://cloud.google.com/appengine/docs/standard/python3/securing-custom-domains-with-ssl)
3. [Implement CI/CD pipeline](https://cloud.google.com/source-repositories/docs/quickstart-triggering-builds-with-source-repositories)
4. [Set up disaster recovery](https://cloud.google.com/architecture/dr-scenarios-planning-guide)
