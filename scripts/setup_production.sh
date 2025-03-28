#!/bin/bash
# Setup script for production deployment of MagnetoCursor
# This script sets up the secure credential management system in a production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}MagnetoCursor Production Setup${NC}"
echo "This script will set up the secure credential management system for production."
echo

# Check if Google Cloud SDK is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: Google Cloud SDK (gcloud) not found.${NC}"
    echo "Please install the Google Cloud SDK first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
echo -e "${YELLOW}Checking Google Cloud authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}You need to log in to Google Cloud first.${NC}"
    gcloud auth login
fi

# Get or select Google Cloud project
echo -e "${YELLOW}Checking Google Cloud project...${NC}"
current_project=$(gcloud config get-value project 2>/dev/null)
if [ -z "$current_project" ]; then
    echo -e "${YELLOW}No project selected. Listing available projects:${NC}"
    gcloud projects list
    echo
    echo -e "${YELLOW}Please enter the project ID to use:${NC}"
    read -r project_id
    gcloud config set project "$project_id"
    current_project="$project_id"
else
    echo -e "${GREEN}Using project: $current_project${NC}"
    read -p "Continue with this project? (Y/n): " confirm
    if [[ $confirm == [nN] ]]; then
        echo -e "${YELLOW}Please enter the project ID to use:${NC}"
        read -r project_id
        gcloud config set project "$project_id"
        current_project="$project_id"
    fi
fi

# Create a .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env-example...${NC}"
    if [ -f .env-example ]; then
        cp .env-example .env
        echo -e "${GREEN}Created .env file from .env-example.${NC}"
        echo -e "${YELLOW}Please edit the .env file to add your credentials.${NC}"
        echo "Press Enter to continue when ready..."
        read
    else
        echo -e "${RED}ERROR: .env-example file not found.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env file found.${NC}"
fi

# Enable Secret Manager API
echo -e "${YELLOW}Enabling Secret Manager API...${NC}"
gcloud services enable secretmanager.googleapis.com

# Update GCP_PROJECT_ID in .env
echo -e "${YELLOW}Updating GCP_PROJECT_ID in .env...${NC}"
sed -i.bak -e "s/^GCP_PROJECT_ID=.*/GCP_PROJECT_ID=$current_project/" .env
sed -i.bak -e "s/^USE_GOOGLE_SECRET_MANAGER=.*/USE_GOOGLE_SECRET_MANAGER=True/" .env
rm -f .env.bak

# Install required Python packages
echo -e "${YELLOW}Installing required Python packages...${NC}"
pip install -r requirements.txt

# Import secrets to Secret Manager
echo -e "${YELLOW}Importing secrets to Secret Manager...${NC}"
python scripts/manage_secrets.py import .env

# Test Secret Manager
echo -e "${YELLOW}Testing Secret Manager configuration...${NC}"
echo "Listing secrets in Secret Manager:"
python scripts/manage_secrets.py list

# Set up service account for the application
echo -e "${YELLOW}Creating service account for the application...${NC}"
service_account_name="magnetocursor-app"
service_account_email="$service_account_name@$current_project.iam.gserviceaccount.com"

# Check if service account already exists
if gcloud iam service-accounts describe "$service_account_email" &> /dev/null; then
    echo -e "${GREEN}Service account $service_account_email already exists.${NC}"
else
    gcloud iam service-accounts create "$service_account_name" \
        --display-name="MagnetoCursor Application Service Account"
    echo -e "${GREEN}Created service account: $service_account_email${NC}"
fi

# Grant Secret Manager access to service account
echo -e "${YELLOW}Granting Secret Manager access to service account...${NC}"
gcloud projects add-iam-policy-binding "$current_project" \
    --member="serviceAccount:$service_account_email" \
    --role="roles/secretmanager.secretAccessor"

# Create a key for the service account
echo -e "${YELLOW}Creating a key for the service account...${NC}"
key_file="service-account-key.json"
if [ -f "$key_file" ]; then
    echo -e "${YELLOW}Key file already exists. Creating a new key will invalidate the old one.${NC}"
    read -p "Create a new key? (y/N): " create_key
    if [[ $create_key != [yY] ]]; then
        echo -e "${GREEN}Keeping existing key.${NC}"
    else
        gcloud iam service-accounts keys create "$key_file" \
            --iam-account="$service_account_email"
        echo -e "${GREEN}Created new service account key: $key_file${NC}"
    fi
else
    gcloud iam service-accounts keys create "$key_file" \
        --iam-account="$service_account_email"
    echo -e "${GREEN}Created service account key: $key_file${NC}"
fi

# Create app.yaml for App Engine deployment
echo -e "${YELLOW}Creating app.yaml for App Engine deployment...${NC}"
cat > app.yaml << EOF
runtime: python311
entrypoint: gunicorn -b :8080 app:app

env_variables:
  FLASK_ENV: production
  GCP_PROJECT_ID: $current_project
  USE_GOOGLE_SECRET_MANAGER: 'True'

handlers:
- url: /static
  static_dir: app/static

- url: /.*
  script: auto
EOF

echo -e "${GREEN}Created app.yaml for App Engine deployment.${NC}"

# Create a README.md with deployment instructions
echo -e "${YELLOW}Creating deployment instructions...${NC}"
cat > DEPLOYMENT.md << EOF
# MagnetoCursor Production Deployment Guide

## Prerequisites

- Google Cloud SDK installed and configured
- Python 3.11 or higher
- Service account with Secret Manager access

## Deployment Steps

1. **Set environment variables:**

   \`\`\`bash
   export GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
   \`\`\`

2. **Deploy to App Engine:**

   \`\`\`bash
   gcloud app deploy app.yaml
   \`\`\`

3. **Set up scheduler for credential rotation (optional):**

   \`\`\`bash
   gcloud scheduler jobs create http rotate-meta-token \\
     --schedule="0 0 1 * *" \\
     --uri="https://YOUR_APP_URL/api/credentials/rotate" \\
     --http-method=POST \\
     --headers="X-API-Key=YOUR_API_ADMIN_KEY" \\
     --message-body='{"platform":"META","credential_key":"META_ACCESS_TOKEN"}' \\
     --time-zone="America/New_York"
   \`\`\`

## Managing Secrets

Use the secret management utility to manage secrets:

- **List secrets:**
  \`\`\`bash
  python scripts/manage_secrets.py list
  \`\`\`

- **Import secrets from .env:**
  \`\`\`bash
  python scripts/manage_secrets.py import .env
  \`\`\`

- **Export secrets to .env:**
  \`\`\`bash
  python scripts/manage_secrets.py export .env.prod
  \`\`\`

## Security Best Practices

1. Rotate API keys regularly
2. Use separate service accounts for different environments
3. Set up IP restrictions for API access
4. Enable Google Cloud Audit Logging
5. Implement proper IAM roles and permissions
EOF

echo -e "${GREEN}Created DEPLOYMENT.md with deployment instructions.${NC}"

echo -e "${GREEN}Production setup completed successfully!${NC}"
echo
echo "Next steps:"
echo "1. Review the DEPLOYMENT.md file for deployment instructions"
echo "2. Make sure all credentials in Secret Manager are correct"
echo "3. Deploy the application to Google App Engine"
echo
echo -e "${YELLOW}Note: To authenticate in your deployed application, set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file.${NC}"
echo