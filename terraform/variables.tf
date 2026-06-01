# Terraform Input Variables for ApexBank AI Co-Pilot

variable "gcp_project_id" {
  type        = string
  description = "The target Google Cloud Platform (GCP) Project ID"
}

variable "gcp_region" {
  type        = string
  default     = "us-central1"
  description = "The target GCP region for regional resources"
}

variable "service_name" {
  type        = string
  default     = "apexbank-copilot"
  description = "Name of the Google Cloud Run serverless service"
}

variable "repository_name" {
  type        = string
  default     = "apexbank-repo"
  description = "Name of the Google Artifact Registry repository"
}

variable "secret_name" {
  type        = string
  default     = "gemini-api-key"
  description = "Name of the GCP Secret Manager entry for the Gemini API Key"
}
