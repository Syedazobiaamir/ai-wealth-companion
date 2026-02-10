# Research: Phase V Cloud-Native Production System

**Branch**: `007-phase-v-cloud-native`
**Date**: 2026-02-10
**Purpose**: Resolve technical decisions and document best practices for Phase V implementation

## Research Topics

### 1. DOKS Cluster Configuration

**Decision**: Use DigitalOcean Kubernetes (DOKS) with 3 standard nodes (s-4vcpu-8gb)

**Rationale**:
- DOKS provides managed Kubernetes with automatic control plane updates
- 3 nodes ensure high availability across failure domains
- s-4vcpu-8gb provides sufficient resources for Kafka, Dapr, and application workloads
- DigitalOcean's pricing is competitive for development/staging workloads

**Alternatives Considered**:
- **AWS EKS**: More features but higher cost and complexity
- **GKE**: Excellent Kubernetes support but vendor lock-in concerns
- **Self-managed K8s**: Maximum control but high operational burden

**Best Practices**:
- Enable node auto-upgrade for security patches
- Use node pools for different workload types
- Configure VPC for network isolation
- Enable cluster autoscaler for cost optimization

---

### 2. Kafka Deployment Strategy

**Decision**: Deploy Kafka via Strimzi Operator with 3 brokers in ephemeral mode

**Rationale**:
- Strimzi is the CNCF standard for Kubernetes-native Kafka
- 3 brokers provide fault tolerance (can lose 1 broker)
- Ephemeral mode reduces storage costs for development
- Strimzi handles rolling upgrades and configuration changes

**Alternatives Considered**:
- **Confluent Cloud**: Fully managed but higher cost and less control
- **Amazon MSK**: Managed but requires AWS ecosystem
- **Redpanda**: Kafka-compatible with lower resource usage but less mature

**Best Practices**:
- Use 3 Zookeeper nodes (or KRaft mode if using Kafka 3.3+)
- Configure topic retention based on use case (7 days default)
- Set replication factor to 3 for production topics
- Use separate topic per event type for isolation

**Configuration**:
```yaml
replicas: 3
resources:
  requests:
    memory: 2Gi
    cpu: 500m
  limits:
    memory: 4Gi
    cpu: 2000m
retention.ms: 604800000  # 7 days
replication.factor: 3
min.insync.replicas: 2
```

---

### 3. Dapr Integration Pattern

**Decision**: Use Dapr pub/sub and state store building blocks only

**Rationale**:
- Pub/sub abstracts Kafka implementation details
- State store provides consistent caching across replicas
- Minimizes Dapr learning curve by focusing on two patterns
- Dapr sidecars handle retries, dead letter queues automatically

**Alternatives Considered**:
- **Direct Kafka SDK**: More control but couples code to Kafka
- **CloudEvents SDK**: Standard format but more implementation work
- **NATS**: Simpler but less mature ecosystem

**Best Practices**:
- Use CloudEvents format for all messages (Dapr does this by default)
- Configure dead letter topics for failed messages
- Set reasonable timeouts (30s default for processing)
- Use content-based routing for complex event flows

**Dapr Component Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-cluster-kafka-bootstrap:9092"
    - name: consumerGroup
      value: "ai-wealth-companion"
    - name: authRequired
      value: "false"
```

---

### 4. Event Schema Design

**Decision**: Use CloudEvents 1.0 specification with JSON payload

**Rationale**:
- CloudEvents is the CNCF standard for event format
- Dapr automatically wraps messages in CloudEvents format
- JSON payload enables easy debugging and compatibility
- Schema includes correlation ID for distributed tracing

**Event Schema Structure**:
```json
{
  "specversion": "1.0",
  "type": "finance.transaction.created",
  "source": "backend",
  "id": "uuid-v4",
  "time": "2026-02-10T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "transactionId": "string",
    "userId": "string",
    "amount": "number",
    "category": "string",
    "timestamp": "string"
  },
  "correlationid": "uuid-v4",
  "traceparent": "00-trace-span-flags"
}
```

---

### 5. Idempotency Implementation

**Decision**: Use event ID deduplication with Redis-based state store

**Rationale**:
- Redis provides fast lookup for processed event IDs
- Dapr state store API handles serialization/TTL
- Event IDs are UUIDs, ensuring global uniqueness
- TTL prevents unbounded growth of processed IDs

**Implementation Pattern**:
```python
async def handle_event(event: CloudEvent):
    event_id = event.id

    # Check if already processed
    if await state_store.get(f"processed:{event_id}"):
        logger.info(f"Duplicate event {event_id}, skipping")
        return

    # Process event
    await process_business_logic(event.data)

    # Mark as processed with 7-day TTL
    await state_store.set(f"processed:{event_id}", "1", ttl=604800)
```

---

### 6. Blue/Green Deployment Strategy

**Decision**: Use Kubernetes Deployment rolling updates with Helm

**Rationale**:
- Native Kubernetes rolling updates are sufficient for this use case
- Helm rollback provides quick recovery (< 2 minutes)
- No need for complex service mesh traffic splitting
- Readiness probes ensure traffic only goes to healthy pods

**Alternatives Considered**:
- **Argo Rollouts**: More sophisticated but adds complexity
- **Istio traffic splitting**: Overkill for current scale
- **Manual blue/green**: Error-prone, harder to automate

**Deployment Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

---

### 7. Observability Stack

**Decision**: Use Prometheus + Grafana + Loki + Jaeger (PLG+J stack)

**Rationale**:
- All components are CNCF projects with strong community support
- Prometheus is the de-facto standard for Kubernetes metrics
- Grafana provides unified dashboards for all data sources
- Loki is lightweight compared to Elasticsearch
- Jaeger integrates with Dapr for distributed tracing

**Best Practices**:
- Use Prometheus Operator for easy management
- Configure retention based on storage budget (15 days default)
- Create pre-built dashboards for key metrics
- Enable Dapr tracing with Jaeger backend

---

### 8. Secret Management

**Decision**: Use Kubernetes Secrets with Dapr Secret Store component

**Rationale**:
- DOKS Secrets are encrypted at rest
- Dapr abstracts secret access from application code
- External secret operators can be added later if needed
- Helm manages secret creation during deployment

**Secrets Required**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `GEMINI_API_KEY`: AI provider API key
- `JWT_SECRET_KEY`: Authentication secret
- `REDIS_URL`: Redis connection string

---

## Summary

All technical decisions have been made based on:
1. Alignment with Phase V constitution (Dapr, Kafka, DOKS)
2. Operational simplicity for current team size
3. Cost-effectiveness for development/staging
4. Clear upgrade path to production scale

No NEEDS CLARIFICATION items remain - all decisions documented above.
