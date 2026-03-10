terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_container_cluster" "primary" {
  name     = "todo-cluster"
  location = var.region

  initial_node_count       = 1
  remove_default_node_pool = true
}

resource "google_container_node_pool" "nodes" {
  name       = "todo-nodes"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 50
  }
}

output "cluster_endpoint" {
  value = google_container_cluster.primary.endpoint
}
