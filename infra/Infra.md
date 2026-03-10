# Infrastructure Overview

Cloud-native Kubernetes deployment on Google Cloud Platform.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Google Cloud Platform               │
│  ┌───────────────────────────────────────────────┐  │
│  │           GKE Cluster: todo-cluster           │  │
│  │                                               │  │
│  │  ┌─────────────┐    ┌─────────────┐           │  │
│  │  │  e2-medium  │    │  e2-medium  │           │  │
│  │  │   Node 1    │    │   Node 2    │           │  │
│  │  └──────┬──────┘    └──────┬──────┘           │  │
│  │         └────────┬─────────┘                  │  │
│  │                  ▼                            │  │
│  │  ┌───────────────────────────────────────┐    │  │
│  │  │  Service: todo-app (ClusterIP:80)     │    │  │
│  │  │              │                        │    │  │
│  │  │              ▼                        │    │  │
│  │  │  Deployment: todo-app (:8080)         │    │  │
│  │  └───────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Structure

```
infra/
├── terraform/           Provisions GKE cluster on GCP
│   ├── main.tf          Cluster and node pool definitions
│   └── variables.tfvars.example
│
└── helm/todo-app/       Deploys application to Kubernetes
    ├── Chart.yaml       Chart metadata (v0.1.0)
    ├── values.yaml      Configuration defaults
    └── templates/
        ├── deployment.yaml
        └── service.yaml
```

## Components

### Terraform Layer
Provisions the GKE cluster `todo-cluster` with a node pool `todo-nodes` containing 2 e2-medium instances in us-central1.

### Helm Layer
Deploys the `todo-app` container as a single-replica Deployment exposed via an internal ClusterIP Service on port 80.

## Key Points

- **Provider:** GCP (Google Kubernetes Engine)
- **Access:** Internal only (ClusterIP, no public ingress)
- **Scale:** Minimal footprint for dev/staging use
- **IaC:** Terraform for infra, Helm for app deployment
