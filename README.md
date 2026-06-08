# SRE-BootCamp

A production-grade Python REST API (Students API) deployed on a local Kubernetes cluster using Minikube, with full SRE infrastructure:

- **HashiCorp Vault** — secret management
- **External Secrets Operator (ESO)** — syncs Vault secrets into Kubernetes
- **ArgoCD** — GitOps-based continuous deployment
- **Prometheus + Grafana** — observability and monitoring

---

## Prerequisites

Install the following before you start:

| Tool | Purpose | Install |
|---|---|---|
| [Minikube](https://minikube.sigs.k8s.io/docs/start/) | Local Kubernetes cluster | `brew install minikube` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Kubernetes CLI | `brew install kubectl` |
| [Helm](https://helm.sh/docs/intro/install/) | Package manager for K8s | `brew install helm` |
| [Docker](https://docs.docker.com/get-docker/) | Container runtime | Download from docker.com |

---

## Setup Order

> **Follow this exact order** — each phase depends on the previous one.

```
Phase 1 → Minikube cluster + node labeling
Phase 2 → HashiCorp Vault
Phase 3 → External Secrets Operator (ESO)
Phase 4 → Monitoring (Prometheus + Grafana)
Phase 5 → ArgoCD
Phase 6 → App Deployment (Helm)
```

---

## Phase 1 — Minikube Cluster Setup

Start a 3-node Minikube cluster and label each node to control workload placement.

```bash
# Start cluster with 3 nodes
minikube start --nodes 3
```

Verify all nodes are up:

```bash
kubectl get nodes
```

You should see:
```
NAME           STATUS   ROLES           AGE
minikube       Ready    control-plane   ...
minikube-m02   Ready    <none>          ...
minikube-m03   Ready    <none>          ...
```

Label each node for workload assignment:

```bash
# Node 1 → Application workloads (Flask API)
kubectl label nodes minikube role=app

# Node 2 → Database workloads (PostgreSQL)
kubectl label nodes minikube-m02 role=database

# Node 3 → Monitoring workloads (Prometheus + Grafana)
kubectl label nodes minikube-m03 app=monitoring
```

Create all required namespaces upfront:

```bash
kubectl create namespace student-api-ns
kubectl create namespace eso
kubectl create namespace vault
kubectl create namespace monitoring
kubectl create namespace argocd
```

---

## Phase 2 — HashiCorp Vault

Vault stores all secrets (DB credentials etc.). The app fetches `DB_PASSWORD` from Vault at startup, so Vault **must be running before the app**.

All Helm charts in this repo use **Helm dependencies** — no manual `helm repo add` or `helm repo update` needed. Just run `helm dependency build` inside the chart directory and install.

### 2.1 Build Chart Dependencies

```bash
cd vault-stack
helm dependency build
```

### 2.2 Install Vault

```bash
helm install vault . -f values.yaml -n vault
```

> **Note**: Dev mode runs Vault unsealed with a fixed root token (`root`). Vault will not be pinned to a specific node in dev mode — this is expected behaviour for a local setup.

### 2.3 Verify Vault is Running

```bash
kubectl get pods -n vault
```

Wait until `vault-0` shows `Running`.

### 2.4 Port-forward Vault

```bash
kubectl port-forward -n vault svc/vault 8200:8200
```

### 2.5 Add Secrets to Vault

Add secrets in vault via UI
1. DB password
2. git PAT token

---

## Phase 3 — External Secrets Operator (ESO)

ESO watches Vault and automatically creates Kubernetes `Secret` objects for your workloads. It is installed in the `vault` namespace so it can communicate directly with Vault.

### 3.1 Build Chart Dependencies

```bash
cd eso-stack
helm dependency build
```

### 3.2 Install ESO

```bash
helm install external-secrets . -f values.yaml -n vault
```

### 3.3 Verify ESO is Running

```bash
kubectl get pods -n vault
```

You should see both `vault-0` and the `external-secrets` pods running.

---

## Phase 4 — Monitoring Stack (Prometheus + Grafana)

### 4.1 Build Chart Dependencies

```bash
cd monitoring-stack
helm dependency build
```

### 4.2 Install Monitoring Stack

```bash
helm install monitoring . -f values.yaml -n monitoring
```

### 4.3 Verify Monitoring Stack

```bash
kubectl get pods -n monitoring
```

### 4.4 Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Open [http://localhost:3000](http://localhost:3000)

Default credentials: `admin` / `admin`

---

## Phase 5 — ArgoCD Setup (GitOps)

ArgoCD watches the `app-stack/` folder in this repo and automatically syncs any changes to the cluster. Set this up before deploying the app so ArgoCD owns the app lifecycle from the start.

### 5.1 Build Chart Dependencies

```bash
cd argocd-deployment
helm dependency build
```

### 5.2 Install ArgoCD

```bash
helm install argocd . -f values.yaml -n argocd --wait
```

### 5.3 Wait for ArgoCD to be Ready

```bash
kubectl get pods -n argocd
```

Wait until all pods are `Running`.

### 5.4 Get Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

### 5.5 Access ArgoCD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open [https://localhost:8080](https://localhost:8080)

Login with:
- **Username**: `admin`
- **Password**: output from the command above

### 5.6 Register the Application in ArgoCD

In the ArgoCD UI, create a new app pointing to:

| Field | Value |
|---|---|
| Repository URL | `https://github.com/atharva-kulkarni123/SRE-BootCamp` |
| Path | `app-stack` |
| Cluster | `https://kubernetes.default.svc` |
| Namespace | `application` |

From this point, any push to `app-stack/` on `main` will be automatically synced to your cluster by ArgoCD.

---

## Phase 6 — App Deployment (Helm)

> If you set up ArgoCD in Phase 5 and registered the app, ArgoCD will deploy this automatically. Use the manual steps below only if you want to deploy without ArgoCD.

### 6.1 Build Chart Dependencies

```bash
cd app-stack
helm dependency build
```

### 6.2 Install the App

```bash
helm install web-app . -f values.yaml -n application
```

### 6.3 Verify the App is Running

```bash
kubectl get pods -n application
kubectl get pods -n database
```

### 6.4 Access the App

```bash
# Using minikube service (opens in browser automatically)
minikube service web-application-service -n application
```

Or port-forward manually:

```bash
kubectl port-forward svc/web-api 5000:5000 -n application
```

Then open [http://localhost:5000](http://localhost:5000).

### 6.5 Verify Metrics

```bash
curl localhost:5000/metrics
```
