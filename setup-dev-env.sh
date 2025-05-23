#!/bin/bash

# Fully automated setup script for local development environment

# Colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print messages
info() { echo -e "\033[0;36m[INFO] ${1}\033[0m"; }
success() { echo -e "\033[0;32m[SUCCESS] ${1}\033[0m"; }
warn() { echo -e "\033[0;33m[WARNING] ${1}\033[0m"; }
error() { echo -e "\033[0;31m[ERROR] ${1}\033[0m"; }

# --- Check Prerequisites --- #
info "Checking prerequisites..."
if ! command -v pnpm &> /dev/null; then error "pnpm not found. Please install."; exit 1; fi
success "pnpm found."
if ! command -v python3 &> /dev/null || ! python3 -c 'import sys; assert sys.version_info >= (3,8)' &> /dev/null; then error "Python 3.8+ not found."; exit 1; fi
success "Python 3.8+ found."

# --- Setup .env file --- #
info "Setting up .env file..."
if [ -f ".env" ]; then
    warn ".env file already exists. Assuming it is correctly populated."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        success ".env file created from .env.example."
        warn "IMPORTANT: .env created. For database operations to succeed now or later, ensure POSTGRES_URL is correctly set in .env"
    else
        error ".env.example not found. Cannot create .env. Please create .env.example or .env manually."
        # Decide if we should exit or continue without .env for other steps
        # For a fully automated script, it might be better to exit if .env is critical for next steps.
        # However, pnpm install and python venv setup can proceed without .env content.
        warn "Proceeding without .env creation. Database operations will likely fail."
    fi
fi

# --- Setup Python Microservice --- #
SERVICE_DIR="./services/audience_segmentation_service"
PYTHON_VENV_NAME=".venv_py_service" # Name of venv in project root
PROJECT_ROOT_VENV_PATH="./${PYTHON_VENV_NAME}" # Path from project root

if [ -d "${SERVICE_DIR}" ]; then
    info "Setting up Python microservice in ${SERVICE_DIR}..."
    
    if [ -d "${PROJECT_ROOT_VENV_PATH}" ]; then
        warn "Python virtual environment ${PYTHON_VENV_NAME} already exists in project root. Re-installing dependencies."
    else
        info "Creating Python virtual environment ${PYTHON_VENV_NAME} in project root..."
        python3 -m venv "${PYTHON_VENV_NAME}"
        if [ $? -eq 0 ]; then
            success "Python virtual environment ${PYTHON_VENV_NAME} created."
        else
            error "Failed to create Python virtual environment. Exiting."
            exit 1
        fi
    fi

    info "Activating Python virtual environment and installing/updating dependencies..."
    source "${PYTHON_VENV_NAME}/bin/activate" # Activate from project root
    pip install -r "${SERVICE_DIR}/requirements.txt"
    if [ $? -eq 0 ]; then
        success "Python dependencies installed for ${SERVICE_DIR}."
    else
        error "Failed to install Python dependencies for ${SERVICE_DIR}."
    fi
    deactivate
else
    warn "Directory ${SERVICE_DIR} not found. Skipping Python microservice setup."
fi

# --- Setup Next.js Project Dependencies --- #
info "Installing/updating Next.js project dependencies using pnpm..."
pnpm install
if [ $? -eq 0 ]; then
    success "Next.js dependencies installed/updated successfully."
else
    error "Failed to install Next.js dependencies. Exiting."
    exit 1
fi

# --- Database Migrations (Attempt if .env exists) --- #
info "Attempting Database Migrations..."
if [ -f ".env" ]; then
    info "Found .env file. Assuming POSTGRES_URL might be configured. Attempting migrations."
    info "Running 'pnpm db:generate'..."
    pnpm db:generate
    if [ $? -ne 0 ]; then
        warn "'pnpm db:generate' failed. This might be okay if there are no schema changes or if .env is not yet fully configured."
        warn "Please check Drizzle setup, schema, and .env (POSTGRES_URL)."
    else
        success "'pnpm db:generate' completed."
        info "Running 'pnpm db:migrate'..."
        pnpm db:migrate
        if [ $? -eq 0 ]; then
            success "Database migrations attempted successfully. Check output for details."
        else
            warn "'pnpm db:migrate' failed. This might be due to an unconfigured/incorrect POSTGRES_URL in .env or other DB issues."
            warn "Please ensure your database is accessible and .env is correct, then run migrations manually if needed."
        fi
    fi
else
    warn ".env file not found. Skipping database migrations."
    info "To run migrations later: populate .env (especially POSTGRES_URL) and then run 'pnpm db:generate && pnpm db:migrate'"
fi

# --- Final Instructions --- #
success "Automated development environment setup steps complete!"
info "Next steps for a fully functional environment:"
info "1. CRITICAL: If a new .env file was created, open it NOW and fill in ALL your actual secrets and configuration values."
info "2. If database migrations were skipped or failed, ensure POSTGRES_URL in .env is correct and run them manually: 'pnpm db:generate && pnpm db:migrate'"
info "3. To start the Python microservice (from project root):"
info "   source .venv_py_service/bin/activate && cd services/audience_segmentation_service && honcho start"
info "4. To start the Next.js application (from project root, in a new terminal):"
info "   pnpm dev"

echo -e "${YELLOW}Review script output above for any warnings or errors and address them accordingly.${NC}" 