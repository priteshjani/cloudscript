output "project_id" {
  value       = var.project_id
  description = "The Google Cloud Project ID."
}

output "artifact_registry_repository" {
  value       = google_artifact_registry_repository.cloudscript_repo.name
  description = "Artifact Registry Docker Repository name."
}

output "spanner_instance" {
  value       = google_spanner_instance.spanner_inst.name
  description = "Spanner Instance name."
}

output "cloudsql_connection_name" {
  value       = google_sql_database_instance.cloudsql_inst.connection_name
  description = "Cloud SQL Instance connection name (useful for proxy and Cloud Run)."
}

output "alloydb_cluster" {
  value       = google_alloydb_cluster.alloydb_cluster.name
  description = "AlloyDB Cluster name."
}
