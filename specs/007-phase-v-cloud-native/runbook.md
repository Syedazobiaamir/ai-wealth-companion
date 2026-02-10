# AI Wealth Companion - Production Runbook

## Phase V: Cloud-Native Production System

**Version:** 5.0.0
**Last Updated:** 2026-02-10
**Environment:** DigitalOcean Kubernetes (DOKS)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Incident Response](#incident-response)
6. [Failure Scenarios](#failure-scenarios)
7. [Recovery Procedures](#recovery-procedures)
8. [Scaling Operations](#scaling-operations)
9. [Maintenance Windows](#maintenance-windows)
10. [Contact Information](#contact-information)

---

## Overview

### System Components

| Component | Technology | Replicas | Purpose |
|-----------|------------|----------|---------|
| Backend | FastAPI + Dapr | 2-10 (HPA) | API server, event publishing |
| Frontend | Next.js + Dapr | 2-5 (HPA) | Web UI |
| MCP Server | Python + Dapr | 2-5 (HPA) | AI tool integration |
| Kafka | Strimzi 3-node | 3 | Event streaming |
| Redis | Single node | 1 | State store, caching |
| Prometheus | Single node | 1 | Metrics collection |
| Grafana | Single node | 1 | Dashboards |
| Jaeger | All-in-one | 1 | Distributed tracing |
| Loki | Single node | 1 | Log aggregation |

### SLOs (Service Level Objectives)

| Metric | Target | Critical |
|--------|--------|----------|
| Availability | 99.9% | < 99% |
| API p95 Latency | < 200ms | > 500ms |
| Event Latency | < 5s | > 10s |
| Error Rate | < 0.1% | > 1% |
| Pod Recovery | < 30s | > 60s |
| Rollback Time | < 2min | > 5min |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  NGINX Ingress    │
                    │  + TLS (cert-mgr) │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Frontend │        │ Backend  │        │   MCP    │
   │ (Next.js)│        │(FastAPI) │        │ Server   │
   └────┬─────┘        └────┬─────┘        └────┬─────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                   ┌────────▼────────┐
                   │   Dapr Sidecar  │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │  Kafka   │  │  Redis   │  │ Postgres │
        │(Strimzi) │  │(State)   │  │ (Neon)   │
        └──────────┘  └──────────┘  └──────────┘
```

---

## Deployment Procedures

### Standard Deployment

```bash
# 1. Verify cluster access
kubectl cluster-info

# 2. Run deployment
./scripts/doks-deploy.sh

# 3. Validate
./scripts/validate-events.sh
```

### Blue-Green Deployment

```bash
# 1. Deploy to staging namespace
NAMESPACE=ai-wealth-staging ./scripts/doks-deploy.sh

# 2. Run smoke tests
./scripts/validate-events.sh --namespace ai-wealth-staging

# 3. Switch traffic (update ingress)
kubectl patch ingress ai-wealth-companion -n ai-wealth \
  --patch '{"spec":{"rules":[{"host":"ai-wealth.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"backend-staging","port":{"number":8000}}}}]}}]}}'

# 4. Monitor for 15 minutes

# 5. If successful, promote staging to production
```

### Rollback Procedure

```bash
# Quick rollback (< 2 minutes)
./scripts/doks-rollback.sh

# Rollback to specific revision
./scripts/doks-rollback.sh --revision 3

# List available revisions
./scripts/doks-rollback.sh --list

# Emergency rollback (force restart all pods)
./scripts/doks-rollback.sh --emergency
```

---

## Monitoring & Alerting

### Grafana Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| AI Wealth Companion | `/grafana/d/ai-wealth-companion` | Main overview |
| Kafka Metrics | `/grafana/d/kafka` | Event streaming |
| Pod Resources | `/grafana/d/kubernetes-pods` | Resource usage |

### Key Metrics

```promql
# Request rate
sum(rate(http_requests_total{namespace="ai-wealth"}[5m]))

# Error rate
sum(rate(http_request_errors_total{namespace="ai-wealth"}[5m])) / sum(rate(http_requests_total{namespace="ai-wealth"}[5m]))

# P95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{namespace="ai-wealth"}[5m])) by (le))

# Event publish rate
sum(rate(events_published_total{namespace="ai-wealth"}[5m]))

# Pod memory usage
sum(container_memory_working_set_bytes{namespace="ai-wealth"}) by (pod)
```

### Alert Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| HighErrorRate | error_rate > 1% for 5m | Critical | Page on-call |
| HighLatency | p95 > 500ms for 10m | Warning | Investigate |
| PodCrashLooping | restarts > 5 in 10m | Critical | Check logs |
| KafkaDown | kafka_ready != True | Critical | Page on-call |
| DiskPressure | disk_usage > 85% | Warning | Scale storage |

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV1 | Complete outage | 15 minutes | All pods down, data loss |
| SEV2 | Major degradation | 30 minutes | High error rate, slow responses |
| SEV3 | Minor issue | 4 hours | Single pod failures, non-critical |
| SEV4 | Cosmetic | Next business day | UI glitches |

### Incident Workflow

1. **Detect**: Alert fires or user reports issue
2. **Triage**: Determine severity and impact
3. **Communicate**: Update status page, notify stakeholders
4. **Investigate**: Check logs, metrics, traces
5. **Mitigate**: Apply temporary fix or rollback
6. **Resolve**: Implement permanent fix
7. **Postmortem**: Document and learn

### Useful Commands

```bash
# Check pod status
kubectl get pods -n ai-wealth -o wide

# View pod logs
kubectl logs -f deployment/backend -n ai-wealth --tail=100

# Check events
kubectl get events -n ai-wealth --sort-by='.lastTimestamp'

# Describe failing pod
kubectl describe pod <pod-name> -n ai-wealth

# Check Dapr sidecar logs
kubectl logs <pod-name> -n ai-wealth -c daprd

# Port forward for local debugging
kubectl port-forward svc/backend 8000:8000 -n ai-wealth
```

---

## Failure Scenarios

### Scenario 1: Backend Pod Crash

**Symptoms:**
- 5xx errors on API calls
- Pod in CrashLoopBackOff state

**Recovery Time:** < 30 seconds (auto-recovery via HPA)

**Manual Recovery:**
```bash
# Check pod status
kubectl get pods -n ai-wealth -l app=backend

# View crash logs
kubectl logs <pod-name> -n ai-wealth --previous

# Force restart
kubectl rollout restart deployment/backend -n ai-wealth
```

### Scenario 2: Kafka Broker Failure

**Symptoms:**
- Event publishing failures
- Increased event latency

**Recovery Time:** 2-5 minutes (auto-recovery via Strimzi)

**Manual Recovery:**
```bash
# Check Kafka cluster status
kubectl get kafka ai-wealth-kafka -n ai-wealth -o yaml

# View broker logs
kubectl logs ai-wealth-kafka-kafka-0 -n ai-wealth

# Force broker restart
kubectl delete pod ai-wealth-kafka-kafka-0 -n ai-wealth
```

### Scenario 3: Database Connection Issues

**Symptoms:**
- Timeout errors
- Transaction failures

**Recovery Time:** Varies (depends on Neon)

**Manual Recovery:**
```bash
# Check database secret
kubectl get secret db-credentials -n ai-wealth -o yaml

# Verify connection from pod
kubectl exec -it deployment/backend -n ai-wealth -- \
  python -c "from src.db.session import get_db; print('Connected')"
```

### Scenario 4: Dapr Sidecar Issues

**Symptoms:**
- Event publishing failures
- State store errors

**Recovery Time:** < 30 seconds (sidecar restart)

**Manual Recovery:**
```bash
# Check Dapr status
dapr status -k

# View sidecar logs
kubectl logs <pod-name> -n ai-wealth -c daprd

# Restart pod to get fresh sidecar
kubectl delete pod <pod-name> -n ai-wealth
```

### Scenario 5: Full Namespace Failure

**Symptoms:**
- All services unavailable
- Complete outage

**Recovery Time:** 5-10 minutes

**Manual Recovery:**
```bash
# Delete and recreate namespace
kubectl delete namespace ai-wealth

# Redeploy
./scripts/doks-setup.sh --skip-cluster
./scripts/doks-deploy.sh
```

---

## Recovery Procedures

### Database Recovery

```bash
# Neon handles automatic backups
# To restore from backup:
# 1. Go to Neon dashboard
# 2. Select project
# 3. Choose "Branches" > "Create from backup"
# 4. Update DATABASE_URL secret with new connection string

kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="<new-connection-string>" \
  -n ai-wealth --dry-run=client -o yaml | kubectl apply -f -

# Restart backend to pick up new connection
kubectl rollout restart deployment/backend -n ai-wealth
```

### Event Recovery (Kafka)

```bash
# Events are retained for 7 days in Kafka
# To replay events from specific offset:

# 1. Check current consumer offsets
kubectl exec -it ai-wealth-kafka-kafka-0 -n ai-wealth -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group ai-wealth-consumers --describe

# 2. Reset offset to beginning (use with caution)
kubectl exec -it ai-wealth-kafka-kafka-0 -n ai-wealth -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group ai-wealth-consumers --reset-offsets --to-earliest \
  --topic transactions --execute
```

### Full Cluster Recovery

```bash
# If cluster is completely lost:

# 1. Recreate cluster
./scripts/doks-setup.sh

# 2. Restore secrets
kubectl apply -f backups/secrets.yaml

# 3. Deploy application
./scripts/doks-deploy.sh

# 4. Restore database (from Neon backup)
# 5. Validate
./scripts/validate-events.sh
```

---

## Scaling Operations

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment/backend --replicas=5 -n ai-wealth

# Scale frontend
kubectl scale deployment/frontend --replicas=3 -n ai-wealth
```

### HPA Configuration

```bash
# View current HPA status
kubectl get hpa -n ai-wealth

# Edit HPA limits
kubectl edit hpa backend-hpa -n ai-wealth
```

### Node Pool Scaling

```bash
# Scale DOKS node pool
doctl kubernetes cluster node-pool update ai-wealth-doks default \
  --count 5

# Enable autoscaling
doctl kubernetes cluster node-pool update ai-wealth-doks default \
  --auto-scale --min-nodes 2 --max-nodes 10
```

---

## Maintenance Windows

### Standard Maintenance

- **When:** Sundays 02:00-06:00 UTC
- **Duration:** 4 hours max
- **Notification:** 48 hours in advance

### Emergency Maintenance

- **When:** As needed
- **Duration:** Minimum required
- **Notification:** Immediate via status page

### Maintenance Checklist

- [ ] Notify users via status page
- [ ] Disable alerting for expected downtime
- [ ] Take database backup
- [ ] Export Grafana dashboards
- [ ] Perform maintenance
- [ ] Run validation tests
- [ ] Re-enable alerting
- [ ] Update status page

---

## Contact Information

### On-Call Rotation

| Role | Primary | Secondary |
|------|---------|-----------|
| Platform Engineer | TBD | TBD |
| Backend Developer | TBD | TBD |
| SRE | TBD | TBD |

### Escalation Path

1. On-call engineer (PagerDuty)
2. Team lead
3. Engineering manager
4. CTO

### External Contacts

| Service | Support | SLA |
|---------|---------|-----|
| DigitalOcean | support@digitalocean.com | 4 hours |
| Neon | support@neon.tech | 24 hours |
| Strimzi | GitHub Issues | Community |

---

## Appendix

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |

### Secrets Management

```bash
# Create secrets from .env file
kubectl create secret generic ai-credentials \
  --from-literal=GEMINI_API_KEY="<key>" \
  --from-literal=OPENAI_API_KEY="<key>" \
  -n ai-wealth

# Rotate secrets
kubectl create secret generic ai-credentials \
  --from-literal=GEMINI_API_KEY="<new-key>" \
  --from-literal=OPENAI_API_KEY="<new-key>" \
  -n ai-wealth --dry-run=client -o yaml | kubectl apply -f -

# Restart to pick up new secrets
kubectl rollout restart deployment/backend -n ai-wealth
```

### Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias k="kubectl"
alias kaw="kubectl -n ai-wealth"
alias kpods="kubectl get pods -n ai-wealth"
alias klogs="kubectl logs -f -n ai-wealth"
alias kexec="kubectl exec -it -n ai-wealth"
```
