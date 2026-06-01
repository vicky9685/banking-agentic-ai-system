# Terraform Output Variables for ApexBank AI Co-Pilot

output "service_url" {
  value       = google_cloud_run_v2_service.copilot_service.uri
  description = "The public URL of the deployed ApexBank AI Co-Pilot Service on Google Cloud Run"
}

output "artifact_registry_repo" {
  value       = google_artifact_registry_repository.copilot_repo.id
  description = "The full resource ID of the Artifact Registry repository created"
}

output "service_account_email" {
  value       = google_service_account.run_identity.email
  description = "The email address of the custom IAM service account utilized by Cloud Run"
}
