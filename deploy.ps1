# Automated Deployment Script for Windows PowerShell
# ApexBank AI Co-Pilot Deployment to GCP

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "     APEXBANK AI CO-PILOT GCP DEPLOYMENT     " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Check for gcloud CLI installation
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud CLI is not installed or not in PATH. Please install Google Cloud SDK and try again."
    exit 1
}

# 2. Gather Configuration
$GCP_PROJECT = Read-Host -Prompt "Enter your GCP Project ID"
if ([string]::IsNullOrWhiteSpace($GCP_PROJECT)) {
    Write-Error "Project ID cannot be empty."
    exit 1
}

$GEMINI_KEY = Read-Host -Prompt "Enter your Google Gemini API Key"
if ([string]::IsNullOrWhiteSpace($GEMINI_KEY)) {
    Write-Error "API Key cannot be empty."
    exit 1
}

$REGION = "us-central1"
$REPO_NAME = "apexbank-repo"
$SERVICE_NAME = "apexbank-copilot"
$SECRET_NAME = "gemini-api-key"

Write-Host "`nSetting gcloud active project context to: $GCP_PROJECT..." -ForegroundColor Green
gcloud config set project $GCP_PROJECT

# 3. Enable Required Google Cloud APIs
Write-Host "`nActivating target GCP APIs (this can take a moment)..." -ForegroundColor Green
gcloud services enable `
    artifactregistry.googleapis.com `
    secretmanager.googleapis.com `
    run.googleapis.com `
    cloudbuild.googleapis.com

# 4. Create Secret Manager Secret & Store Key
Write-Host "`nConfiguring Secret Manager..." -ForegroundColor Green
$secretExists = gcloud secrets list --filter="name:$SECRET_NAME" --format="value(name)"

if (!$secretExists) {
    Write-Host "Creating secret: $SECRET_NAME..."
    gcloud secrets create $SECRET_NAME --replication-policy="automatic"
}

Write-Host "Adding API key secret version..."
$SecretBytes = [System.Text.Encoding]::UTF8.GetBytes($GEMINI_KEY)
$TempFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllBytes($TempFile, $SecretBytes)
try {
    gcloud secrets versions add $SECRET_NAME --data-file=$TempFile
} finally {
    Remove-Item $TempFile -Force
}

# 5. Create Artifact Registry Repository
Write-Host "`nChecking Artifact Registry repository..." -ForegroundColor Green
$repoExists = gcloud artifacts repositories list --location=$REGION --filter="name:$REPO_NAME" --format="value(name)"

if (!$repoExists) {
    Write-Host "Creating Docker Artifact Registry: $REPO_NAME in $REGION..."
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="Docker repository for ApexBank AI Co-Pilot"
}

# 6. Build and Deploy using Google Cloud Build
Write-Host "`nSubmitting Cloud Build job (Containerizing & Deploying to Cloud Run)..." -ForegroundColor Green
Write-Host "No local Docker installation required. Building on Google Cloud infra..." -ForegroundColor Cyan

gcloud builds submit --config=gcp/cloudbuild.yaml `
    --substitutions="_LOCATION=$REGION,_REPOSITORY=$REPO_NAME,_SERVICE_NAME=$SERVICE_NAME,_SECRET_NAME=$SECRET_NAME"

Write-Host "`n=======================================================" -ForegroundColor Green
Write-Host "  ApexBank AI Co-Pilot Successfully Deployed to GCP!   " -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "You can find your service URL listed in the Cloud Run CLI output above." -ForegroundColor Cyan
