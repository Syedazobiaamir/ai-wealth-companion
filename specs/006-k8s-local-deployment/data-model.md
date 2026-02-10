# Phase IV Data Model: Kubernetes Entities

**Feature**: 006-k8s-local-deployment
**Date**: 2026-02-09

## Overview

This document defines the Kubernetes entities and their relationships for Phase IV Local Kubernetes Deployment.

---

## 1. Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-wealth
  labels:
    app.kubernetes.io/name: ai-wealth-companion
    app.kubernetes.io/part-of: ai-wealth-companion
    environment: development
```

**Purpose**: Isolate all AI Wealth Companion resources.

---

## 2. Services

### 2.1 Backend Service

| Field | Value |
|-------|-------|
| Name | `backend` |
| Type | ClusterIP |
| Port | 8000 |
| Target Port | 8000 |
| Selector | `app: backend` |

### 2.2 Frontend Service

| Field | Value |
|-------|-------|
| Name | `frontend` |
| Type | ClusterIP |
| Port | 3000 |
| Target Port | 3000 |
| Selector | `app: frontend` |

### 2.3 MCP Server Service

| Field | Value |
|-------|-------|
| Name | `mcp-server` |
| Type | ClusterIP |
| Port | 8080 |
| Target Port | 8080 |
| Selector | `app: mcp-server` |

---

## 3. Deployments

### 3.1 Backend Deployment

```yaml
metadata:
  name: backend
  labels:
    app: backend
    app.kubernetes.io/component: api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
        - name: backend
          image: ai-wealth-companion/backend:dev
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: db-credentials
            - secretRef:
                name: jwt-secret
            - secretRef:
                name: ai-credentials
            - configMapRef:
                name: app-config
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### 3.2 Frontend Deployment

```yaml
metadata:
  name: frontend
  labels:
    app: frontend
    app.kubernetes.io/component: ui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    spec:
      containers:
        - name: frontend
          image: ai-wealth-companion/frontend:dev
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: API_URL
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 300m
              memory: 256Mi
          livenessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### 3.3 MCP Server Deployment

```yaml
metadata:
  name: mcp-server
  labels:
    app: mcp-server
    app.kubernetes.io/component: mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-server
  template:
    spec:
      containers:
        - name: mcp-server
          image: ai-wealth-companion/mcp-server:dev
          ports:
            - containerPort: 8080
          envFrom:
            - secretRef:
                name: db-credentials
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
```

---

## 4. ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ai-wealth
data:
  APP_NAME: "AI Wealth & Spending Companion"
  APP_VERSION: "4.0.0"
  DEBUG: "false"
  API_URL: "http://backend:8000"
  CORS_ORIGINS: "http://frontend:3000,http://localhost:3000"
```

---

## 5. Secrets

### 5.1 Database Credentials

| Key | Description |
|-----|-------------|
| DATABASE_URL | PostgreSQL connection string to Neon DB |

### 5.2 JWT Secret

| Key | Description |
|-----|-------------|
| JWT_SECRET_KEY | Secret key for JWT token signing |

### 5.3 AI Credentials

| Key | Description |
|-----|-------------|
| GEMINI_API_KEY | Google Gemini API key |
| OPENAI_API_KEY | OpenAI API key (optional) |

### 5.4 OAuth Credentials

| Key | Description |
|-----|-------------|
| GOOGLE_CLIENT_ID | Google OAuth client ID |
| GOOGLE_CLIENT_SECRET | Google OAuth client secret |
| GITHUB_CLIENT_ID | GitHub OAuth client ID |
| GITHUB_CLIENT_SECRET | GitHub OAuth client secret |

---

## 6. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-wealth-ingress
  namespace: ai-wealth
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  ingressClassName: nginx
  rules:
    - host: ai-wealth.local
      http:
        paths:
          - path: /api/(.*)
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
          - path: /(.*)
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
```

---

## 7. HorizontalPodAutoscaler (AI Agents)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agents-hpa
  namespace: ai-wealth
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 1
  maxReplicas: 3
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 8. Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                       Namespace: ai-wealth                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐                                             │
│  │   Ingress   │                                             │
│  │ (ai-wealth- │                                             │
│  │   ingress)  │                                             │
│  └──────┬──────┘                                             │
│         │ routes to                                          │
│         ▼                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Service    │  │   Service    │  │   Service    │       │
│  │  (frontend)  │  │  (backend)   │  │ (mcp-server) │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │               │
│         ▼                 ▼                  ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Deployment  │  │  Deployment  │  │  Deployment  │       │
│  │  (frontend)  │  │  (backend)   │  │ (mcp-server) │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                           │                                  │
│                           │ uses                             │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │   Secrets & ConfigMap   │                     │
│              │  - db-credentials       │                     │
│              │  - jwt-secret           │                     │
│              │  - ai-credentials       │                     │
│              │  - app-config           │                     │
│              └────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Labels Convention

All resources follow Kubernetes recommended labels:

| Label | Purpose | Example |
|-------|---------|---------|
| `app.kubernetes.io/name` | Application name | `ai-wealth-companion` |
| `app.kubernetes.io/component` | Component type | `api`, `ui`, `mcp` |
| `app.kubernetes.io/version` | Version | `4.0.0` |
| `app.kubernetes.io/part-of` | Parent application | `ai-wealth-companion` |
| `app.kubernetes.io/managed-by` | Tool managing resource | `helm` |
| `environment` | Deployment environment | `development`, `production` |
