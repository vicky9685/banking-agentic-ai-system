# Production-Grade Terraform Infrastructure for ApexBank AI Co-Pilot

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# 1. Google Artifact Registry Repository
resource "google_artifact_registry_repository" "copilot_repo" {
  location      = var.gcp_region
  repository_id = var.repository_name
  description   = "Docker Artifact Registry for ApexBank AI Co-Pilot images"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }
}

# 2. Google Secret Manager Secret for Gemini API Key
resource "google_secret_manager_secret" "api_key_secret" {
  secret_id = var.secret_name

  replication {
    auto {}
  }
}

# 3. Custom IAM Service Account for Cloud Run Execution
resource "google_service_account" "run_identity" {
  account_id   = "apexbank-copilot-run-sa"
  display_name = "ApexBank Co-Pilot Cloud Run Service Account"
}

# 4. IAM Role Binding: Let Cloud Run read the Gemini Secret
resource "google_secret_manager_secret_iam_member" "secret_accessor" {
  secret_id = google_secret_manager_secret.api_key_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.run_identity.email}"
}

# 5. Google Cloud Run v2 Service Deployment
resource "google_cloud_run_v2_service" "copilot_service" {
  name     = var.service_name
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.run_identity.email

    scaling {
      max_instance_count = 5 # Prevent run-away budget costs
      min_instance_count = 0 # Scale down to 0 when idle to reduce costs
    }

    containers {
      image = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.copilot_repo.name}/${var.service_name}:latest"
      
      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }

      # Hook environment variable to Secret Manager
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.api_key_secret.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_LATEST"
    percent = 100
  }

  # Ensure registry is built and secrets are permissioned before creating the service
  depends_on = [
    google_artifact_registry_repository.copilot_repo,
    google_secret_manager_secret_iam_member.secret_accessor
  ]
}

# 6. IAM Policy: Allow Public (Unauthenticated) Access to the Web Dashboard
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.copilot_service.name
  location = google_cloud_run_v2_service.copilot_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
