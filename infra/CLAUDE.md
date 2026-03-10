# CLAUDE.md

Infrastructure for todo-app. GKE on GCP provisioned with Terraform, deployed via Helm.

See **Infra.md** for architecture diagrams and component relationships.

## Commands

```bash
# Cluster context
kubectl config use-context todo-app-context

# View cluster state
kubectl get nodes
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=todo-app
kubectl logs -l app=todo-app --tail=100 -f

# Describe resources
kubectl describe deployment todo-app
kubectl describe service todo-app

# GCP cluster info
gcloud container clusters list
gcloud container clusters describe todo-cluster --region us-central1

# GCP logs
gcloud logging read "resource.type=k8s_container" --limit=50
```

## Structure

- **terraform/main.tf** — GKE cluster `todo-cluster` and node pool `todo-nodes` (2x e2-medium).
- **terraform/variables.tfvars.example** — Template for GCP project config.
- **helm/todo-app/Chart.yaml** — Helm chart metadata (v0.1.0).
- **helm/todo-app/values.yaml** — Deployment config: replicas, image, resources, service type.
- **helm/todo-app/templates/** — K8s manifests (deployment.yaml, service.yaml).

## Boundaries

- Never commit secrets, credentials, or service account keys.
- Do not modify production cluster state without review.
- Keep Terraform and Helm changes in version control.
- Use variables.tfvars.example as template, never commit actual tfvars.
