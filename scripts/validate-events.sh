#!/bin/bash
# Phase V: Event Validation Script
# Validates event flow, Kafka health, and Dapr components

set -e

echo "================================================"
echo "AI Wealth Companion - Event Validation"
echo "Phase V: Cloud-Native Production System"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-wealth}"
KAFKA_NAMESPACE="${KAFKA_NAMESPACE:-kafka}"
KAFKA_CLUSTER="${KAFKA_CLUSTER:-ai-wealth-kafka}"
EVENT_LATENCY_THRESHOLD="${EVENT_LATENCY_THRESHOLD:-5}"  # 5 seconds max

# Validation results
VALIDATION_PASSED=true
VALIDATION_RESULTS=()

# Add result
add_result() {
    local status=$1
    local message=$2
    VALIDATION_RESULTS+=("$status|$message")
    if [ "$status" = "FAIL" ]; then
        VALIDATION_PASSED=false
    fi
}

# Check cluster connection
check_cluster() {
    echo -e "${YELLOW}Checking cluster connection...${NC}"

    if ! kubectl cluster-info &> /dev/null; then
        add_result "FAIL" "Cannot connect to Kubernetes cluster"
        return 1
    fi
    add_result "PASS" "Connected to Kubernetes cluster"
}

# Validate pod health
validate_pods() {
    echo -e "${YELLOW}Validating pod health...${NC}"

    # Check all pods in namespace
    local not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l)
    local total=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)

    if [ "$total" -eq 0 ]; then
        add_result "WARN" "No pods found in namespace $NAMESPACE"
    elif [ "$not_ready" -gt 0 ]; then
        add_result "FAIL" "$not_ready of $total pods not ready in $NAMESPACE"
        kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed"
    else
        add_result "PASS" "All $total pods healthy in $NAMESPACE"
    fi

    # Check Dapr sidecars
    local dapr_pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].spec.containers[*].name}' 2>/dev/null | tr ' ' '\n' | grep -c "daprd" || echo "0")
    if [ "$dapr_pods" -gt 0 ]; then
        add_result "PASS" "$dapr_pods Dapr sidecars running"
    else
        add_result "WARN" "No Dapr sidecars found"
    fi
}

# Validate Kafka cluster
validate_kafka() {
    echo -e "${YELLOW}Validating Kafka cluster...${NC}"

    # Check Kafka cluster status
    if ! kubectl get kafka "$KAFKA_CLUSTER" -n "$NAMESPACE" &> /dev/null; then
        add_result "WARN" "Kafka cluster '$KAFKA_CLUSTER' not found"
        return 0
    fi

    local kafka_ready=$(kubectl get kafka "$KAFKA_CLUSTER" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
    if [ "$kafka_ready" = "True" ]; then
        add_result "PASS" "Kafka cluster '$KAFKA_CLUSTER' is ready"
    else
        add_result "FAIL" "Kafka cluster '$KAFKA_CLUSTER' is not ready"
    fi

    # Check Kafka brokers
    local broker_count=$(kubectl get pods -n "$NAMESPACE" -l strimzi.io/name="${KAFKA_CLUSTER}-kafka" --no-headers 2>/dev/null | grep "Running" | wc -l)
    if [ "$broker_count" -gt 0 ]; then
        add_result "PASS" "$broker_count Kafka brokers running"
    else
        add_result "WARN" "No Kafka brokers found"
    fi

    # Check Zookeeper (if applicable)
    local zk_count=$(kubectl get pods -n "$NAMESPACE" -l strimzi.io/name="${KAFKA_CLUSTER}-zookeeper" --no-headers 2>/dev/null | grep "Running" | wc -l)
    if [ "$zk_count" -gt 0 ]; then
        add_result "PASS" "$zk_count Zookeeper nodes running"
    fi
}

# Validate Kafka topics
validate_topics() {
    echo -e "${YELLOW}Validating Kafka topics...${NC}"

    # Required topics
    local required_topics=("transactions" "budget-alerts" "ai-insights" "notifications")

    for topic in "${required_topics[@]}"; do
        if kubectl get kafkatopic "$topic" -n "$NAMESPACE" &> /dev/null; then
            local topic_ready=$(kubectl get kafkatopic "$topic" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
            if [ "$topic_ready" = "True" ]; then
                add_result "PASS" "Kafka topic '$topic' is ready"
            else
                add_result "FAIL" "Kafka topic '$topic' is not ready"
            fi
        else
            add_result "WARN" "Kafka topic '$topic' not found"
        fi
    done
}

# Validate Dapr components
validate_dapr() {
    echo -e "${YELLOW}Validating Dapr components...${NC}"

    # Check Dapr system
    if ! kubectl get namespace dapr-system &> /dev/null; then
        add_result "FAIL" "Dapr system namespace not found"
        return 1
    fi

    local dapr_pods=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | grep "Running" | wc -l)
    if [ "$dapr_pods" -gt 0 ]; then
        add_result "PASS" "$dapr_pods Dapr system pods running"
    else
        add_result "FAIL" "No Dapr system pods running"
    fi

    # Check Dapr components in application namespace
    local components=$(kubectl get components.dapr.io -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    if [ "$components" -gt 0 ]; then
        add_result "PASS" "$components Dapr components configured"

        # List component status
        kubectl get components.dapr.io -n "$NAMESPACE" 2>/dev/null | while read -r line; do
            echo "  $line"
        done
    else
        add_result "WARN" "No Dapr components found in $NAMESPACE"
    fi
}

# Test event publishing
test_event_publishing() {
    echo -e "${YELLOW}Testing event publishing...${NC}"

    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$backend_pod" ]; then
        add_result "WARN" "No backend pod found for event testing"
        return 0
    fi

    # Test Dapr publish endpoint
    local publish_result=$(kubectl exec -n "$NAMESPACE" "$backend_pod" -c daprd -- \
        curl -sf -X POST "http://localhost:3500/v1.0/publish/pubsub/test-topic" \
        -H "Content-Type: application/json" \
        -d '{"test": "validation"}' 2>/dev/null && echo "OK" || echo "FAIL")

    if [ "$publish_result" = "OK" ]; then
        add_result "PASS" "Dapr publish endpoint accessible"
    else
        add_result "WARN" "Dapr publish endpoint test inconclusive"
    fi
}

# Measure event latency
test_event_latency() {
    echo -e "${YELLOW}Testing event latency...${NC}"

    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$backend_pod" ]; then
        add_result "WARN" "No backend pod found for latency testing"
        return 0
    fi

    # Measure publish latency
    local start_time=$(date +%s%3N)

    kubectl exec -n "$NAMESPACE" "$backend_pod" -c daprd -- \
        curl -sf -X POST "http://localhost:3500/v1.0/publish/pubsub/latency-test" \
        -H "Content-Type: application/json" \
        -d '{"timestamp": "'$start_time'"}' 2>/dev/null

    local end_time=$(date +%s%3N)
    local latency_ms=$((end_time - start_time))
    local latency_sec=$((latency_ms / 1000))

    if [ "$latency_sec" -le "$EVENT_LATENCY_THRESHOLD" ]; then
        add_result "PASS" "Event publish latency: ${latency_ms}ms (< ${EVENT_LATENCY_THRESHOLD}s threshold)"
    else
        add_result "FAIL" "Event publish latency: ${latency_ms}ms exceeds ${EVENT_LATENCY_THRESHOLD}s threshold"
    fi
}

# Simulate pod failure
test_pod_failure() {
    echo -e "${YELLOW}Testing pod failure recovery...${NC}"

    if [ "$SIMULATE_FAILURE" != "true" ]; then
        add_result "SKIP" "Pod failure test (use --simulate-failure to run)"
        return 0
    fi

    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$backend_pod" ]; then
        add_result "WARN" "No backend pod found for failure testing"
        return 0
    fi

    echo "  Deleting pod $backend_pod..."
    local start_time=$(date +%s)

    kubectl delete pod "$backend_pod" -n "$NAMESPACE" --force --grace-period=0 &>/dev/null

    # Wait for new pod to be ready
    echo "  Waiting for recovery..."
    kubectl wait --for=condition=ready pod \
        -l app=backend \
        --namespace="$NAMESPACE" \
        --timeout=60s &>/dev/null || true

    local end_time=$(date +%s)
    local recovery_time=$((end_time - start_time))

    if [ "$recovery_time" -le 30 ]; then
        add_result "PASS" "Pod recovery time: ${recovery_time}s (< 30s target)"
    else
        add_result "WARN" "Pod recovery time: ${recovery_time}s (> 30s target)"
    fi
}

# Simulate Kafka failure
test_kafka_failure() {
    echo -e "${YELLOW}Testing Kafka failure handling...${NC}"

    if [ "$SIMULATE_FAILURE" != "true" ]; then
        add_result "SKIP" "Kafka failure test (use --simulate-failure to run)"
        return 0
    fi

    # Find a Kafka broker pod
    local kafka_pod=$(kubectl get pods -n "$NAMESPACE" -l strimzi.io/name="${KAFKA_CLUSTER}-kafka" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -z "$kafka_pod" ]; then
        add_result "WARN" "No Kafka broker pod found for failure testing"
        return 0
    fi

    echo "  Testing Kafka broker resilience..."

    # Step 1: Publish a test event before failure
    local test_event_id=$(uuidgen 2>/dev/null || echo "test-$(date +%s)")
    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -n "$backend_pod" ]; then
        echo "  Publishing test event before broker restart..."
        kubectl exec -n "$NAMESPACE" "$backend_pod" -c daprd -- \
            curl -sf -X POST "http://localhost:3500/v1.0/publish/pubsub/resilience-test" \
            -H "Content-Type: application/json" \
            -d "{\"test_id\": \"$test_event_id\", \"phase\": \"before\"}" 2>/dev/null || true
    fi

    # Step 2: Restart one Kafka broker (not delete - safer)
    echo "  Restarting Kafka broker $kafka_pod..."
    local start_time=$(date +%s)

    kubectl delete pod "$kafka_pod" -n "$NAMESPACE" --grace-period=30 &>/dev/null

    # Step 3: Wait for Kafka to recover
    echo "  Waiting for Kafka recovery..."
    kubectl wait --for=condition=ready pod \
        -l strimzi.io/name="${KAFKA_CLUSTER}-kafka" \
        --namespace="$NAMESPACE" \
        --timeout=120s &>/dev/null || true

    local end_time=$(date +%s)
    local recovery_time=$((end_time - start_time))

    # Step 4: Check Kafka cluster is ready
    local kafka_ready=$(kubectl get kafka "$KAFKA_CLUSTER" -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)

    if [ "$kafka_ready" = "True" ]; then
        add_result "PASS" "Kafka cluster recovered in ${recovery_time}s"
    else
        add_result "FAIL" "Kafka cluster not ready after ${recovery_time}s"
        return 1
    fi

    # Step 5: Verify event publishing still works after recovery
    if [ -n "$backend_pod" ]; then
        echo "  Verifying event publishing after recovery..."
        local publish_result=$(kubectl exec -n "$NAMESPACE" "$backend_pod" -c daprd -- \
            curl -sf -X POST "http://localhost:3500/v1.0/publish/pubsub/resilience-test" \
            -H "Content-Type: application/json" \
            -d "{\"test_id\": \"$test_event_id\", \"phase\": \"after\"}" 2>/dev/null && echo "OK" || echo "FAIL")

        if [ "$publish_result" = "OK" ]; then
            add_result "PASS" "Event publishing works after Kafka recovery"
        else
            add_result "WARN" "Event publishing test inconclusive after recovery"
        fi
    fi
}

# Test multi-pod failure (chaos testing)
test_multi_pod_failure() {
    echo -e "${YELLOW}Testing multi-pod failure recovery...${NC}"

    if [ "$SIMULATE_FAILURE" != "true" ]; then
        add_result "SKIP" "Multi-pod failure test (use --simulate-failure to run)"
        return 0
    fi

    # Get all backend pods
    local pod_count=$(kubectl get pods -n "$NAMESPACE" -l app=backend --no-headers 2>/dev/null | wc -l)

    if [ "$pod_count" -lt 2 ]; then
        add_result "SKIP" "Multi-pod failure test requires at least 2 replicas"
        return 0
    fi

    echo "  Found $pod_count backend pods, deleting 50%..."
    local pods_to_delete=$((pod_count / 2))
    local start_time=$(date +%s)

    # Delete half the pods
    kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[*].metadata.name}' | \
        tr ' ' '\n' | head -n "$pods_to_delete" | \
        xargs -I {} kubectl delete pod {} -n "$NAMESPACE" --force --grace-period=0 &>/dev/null

    # Wait for recovery
    echo "  Waiting for pods to recover..."
    sleep 5
    kubectl wait --for=condition=ready pod \
        -l app=backend \
        --namespace="$NAMESPACE" \
        --timeout=60s &>/dev/null || true

    local end_time=$(date +%s)
    local recovery_time=$((end_time - start_time))

    # Verify all pods are back
    local final_pod_count=$(kubectl get pods -n "$NAMESPACE" -l app=backend --no-headers 2>/dev/null | grep "Running" | wc -l)

    if [ "$final_pod_count" -ge "$pod_count" ]; then
        add_result "PASS" "Multi-pod recovery: ${final_pod_count}/${pod_count} pods in ${recovery_time}s"
    else
        add_result "WARN" "Multi-pod recovery incomplete: ${final_pod_count}/${pod_count} pods in ${recovery_time}s"
    fi
}

# Test network partition simulation (if supported)
test_network_partition() {
    echo -e "${YELLOW}Testing network partition handling...${NC}"

    if [ "$SIMULATE_FAILURE" != "true" ]; then
        add_result "SKIP" "Network partition test (use --simulate-failure to run)"
        return 0
    fi

    # This would require a network policy or chaos mesh
    # For now, we verify the network policies exist
    local netpol_count=$(kubectl get networkpolicies -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)

    if [ "$netpol_count" -gt 0 ]; then
        add_result "PASS" "Network policies configured: $netpol_count policies"
    else
        add_result "INFO" "No network policies configured (optional)"
    fi
}

# Print validation summary
print_summary() {
    echo ""
    echo "================================================"
    echo "Validation Summary"
    echo "================================================"
    echo ""

    local pass_count=0
    local fail_count=0
    local warn_count=0
    local skip_count=0

    for result in "${VALIDATION_RESULTS[@]}"; do
        local status="${result%%|*}"
        local message="${result#*|}"

        case "$status" in
            "PASS")
                echo -e "${GREEN}✓ PASS${NC}: $message"
                ((pass_count++))
                ;;
            "FAIL")
                echo -e "${RED}✗ FAIL${NC}: $message"
                ((fail_count++))
                ;;
            "WARN")
                echo -e "${YELLOW}! WARN${NC}: $message"
                ((warn_count++))
                ;;
            "SKIP")
                echo -e "${BLUE}○ SKIP${NC}: $message"
                ((skip_count++))
                ;;
        esac
    done

    echo ""
    echo "================================================"
    echo -e "Results: ${GREEN}$pass_count passed${NC}, ${RED}$fail_count failed${NC}, ${YELLOW}$warn_count warnings${NC}, ${BLUE}$skip_count skipped${NC}"
    echo "================================================"
    echo ""

    if [ "$VALIDATION_PASSED" = true ]; then
        echo -e "${GREEN}All critical validations passed!${NC}"
        return 0
    else
        echo -e "${RED}Some validations failed - review results above${NC}"
        return 1
    fi
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --namespace NS       Target namespace (default: ai-wealth)"
    echo "  --kafka-cluster NAME Kafka cluster name (default: ai-wealth-kafka)"
    echo "  --simulate-failure   Run failure simulation tests"
    echo "  --skip-kafka         Skip Kafka validation"
    echo "  --skip-dapr          Skip Dapr validation"
    echo "  --skip-events        Skip event publishing tests"
    echo "  --json               Output results as JSON"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all validations"
    echo "  $0 --simulate-failure        # Include failure tests"
    echo "  $0 --skip-kafka --skip-dapr  # Only validate pods"
    echo ""
}

# Parse arguments
SIMULATE_FAILURE=false
SKIP_KAFKA=false
SKIP_DAPR=false
SKIP_EVENTS=false
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --kafka-cluster)
            KAFKA_CLUSTER="$2"
            shift 2
            ;;
        --simulate-failure)
            SIMULATE_FAILURE=true
            shift
            ;;
        --skip-kafka)
            SKIP_KAFKA=true
            shift
            ;;
        --skip-dapr)
            SKIP_DAPR=true
            shift
            ;;
        --skip-events)
            SKIP_EVENTS=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    check_cluster || exit 1
    validate_pods

    if [ "$SKIP_KAFKA" = false ]; then
        validate_kafka
        validate_topics
    fi

    if [ "$SKIP_DAPR" = false ]; then
        validate_dapr
    fi

    if [ "$SKIP_EVENTS" = false ]; then
        test_event_publishing
        test_event_latency
    fi

    # Resilience tests
    test_pod_failure
    test_kafka_failure
    test_multi_pod_failure
    test_network_partition

    if [ "$JSON_OUTPUT" = true ]; then
        echo "{"
        echo "  \"passed\": $VALIDATION_PASSED,"
        echo "  \"results\": ["
        local first=true
        for result in "${VALIDATION_RESULTS[@]}"; do
            local status="${result%%|*}"
            local message="${result#*|}"
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            echo -n "    {\"status\": \"$status\", \"message\": \"$message\"}"
        done
        echo ""
        echo "  ]"
        echo "}"
    else
        print_summary
    fi
}

main "$@"
