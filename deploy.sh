#!/usr/bin/env bash
# Automated Deployment Script for Linux & macOS
# ApexBank AI Co-Pilot Deployment to GCP

set -euo pipefail

# ANSI color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}=============================================${NC}"
echo -e "${CYAN}     APEXBANK AI CO-PILOT GCP DEPLOYMENT     ${NC}"
echo -e "${CYAN}=============================================${NC}"

# 1. Check for gcloud CLI installation
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed or not in PATH. Please install Google Cloud SDK and try again.${NC}"
    exit 1
fi

# 2. Gather Configuration
read -rp "Enter your GCP Project ID: " GCP_PROJECT
if [[ -z "$GCP_PROJECT" ]]; then
    echo -e "${RED}Error: Project ID cannot be empty.${NC}"
    exit 1
fi

read -rsp "Enter your Google Gemini API Key: " GEMINI_KEY
echo "" # Linebreak after silent prompt
if [[ -z "$GEMINI_KEY" ]]; then
    echo -e "${RED}Error: API Key cannot be empty.${NC}"
    exit 1
fi

REGION="us-central1"
REPO_NAME="apexbank-repo"
SERVICE_NAME="apexbank-copilot"
SECRET_NAME="gemini-api-key"

echo -e "\n${GREEN}Setting gcloud active project context to: $GCP_PROJECT...${NC}"
gcloud config set project "$GCP_PROJECT"

# 3. Enable Required Google Cloud APIs
echo -e "\n${GREEN}Activating target GCP APIs (this can take a moment)...${NC}"
gcloud services enable \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com

# 4. Create Secret Manager Secret & Store Key
echo -e "\n${GREEN}Configuring Secret Manager...${NC}"
if ! gcloud secrets describe "$SECRET_NAME" &> /dev/null; then
    echo "Creating secret: $SECRET_NAME..."
    gcloud secrets create "$SECRET_NAME" --replication-policy="automatic"
fi

echo "Adding API key secret version..."
echo -n "$GEMINI_KEY" | gcloud secrets versions add "$SECRET_NAME" --data-file=-

# 5. Create Artifact Registry Repository
echo -e "\n${GREEN}Checking Artifact Registry repository...${NC}"
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" &> /dev/null; then
    echo "Creating Docker Artifact Registry: $REPO_NAME in $REGION..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for ApexBank AI Co-Pilot"
fi

# 6. Build and Deploy using Google Cloud Build
echo -e "\n${GREEN}Submitting Cloud Build job (Containerizing & Deploying to Cloud Run)...${NC}"
echo -e "${CYAN}No local Docker installation required. Building on Google Cloud infra...${NC}"

gcloud builds submit --config=gcp/cloudbuild.yaml \
    --substitutions="_LOCATION=$REGION,_REPOSITORY=$REPO_NAME,_SERVICE_NAME=$SERVICE_NAME,_SECRET_NAME=$SECRET_NAME"

echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}  ApexBank AI Co-Pilot Successfully Deployed to GCP!   ${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "${CYAN}You can find your service URL listed in the Cloud Run CLI output above.${NC}"
