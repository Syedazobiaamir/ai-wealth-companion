#!/bin/bash
# Phase V: DOKS Rollback Script
# Rolls back AI Wealth Companion deployment with validation

set -e

echo "================================================"
echo "AI Wealth Companion - DOKS Rollback"
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
RELEASE_NAME="${RELEASE_NAME:-ai-wealth}"
ROLLBACK_TIMEOUT="${ROLLBACK_TIMEOUT:-120}"  # 2 minutes target

# Rollback tracking
ROLLBACK_START=$(date +%s)

# Check cluster connection
check_cluster() {
    echo -e "${YELLOW}Checking DOKS cluster connection...${NC}"

    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Connected to cluster${NC}"
}

# List available revisions
list_revisions() {
    echo -e "${YELLOW}Available Helm revisions:${NC}"
    helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 10
    echo ""
}

# Get current revision
get_current_revision() {
    helm list -n "$NAMESPACE" -o json | jq -r ".[] | select(.name==\"$RELEASE_NAME\") | .revision"
}

# Rollback to previous revision
rollback_previous() {
    local current_revision=$(get_current_revision)
    local target_revision=$((current_revision - 1))

    if [ "$target_revision" -lt 1 ]; then
        echo -e "${RED}Error: No previous revision to rollback to${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Rolling back from revision $current_revision to $target_revision...${NC}"
    rollback_to_revision "$target_revision"
}

# Rollback to specific revision
rollback_to_revision() {
    local revision=$1

    echo -e "${YELLOW}Rolling back to revision $revision...${NC}"

    # Perform rollback with timeout
    helm rollback "$RELEASE_NAME" "$revision" \
        --namespace "$NAMESPACE" \
        --timeout "${ROLLBACK_TIMEOUT}s" \
        --wait

    echo -e "${GREEN}✓ Helm rollback complete${NC}"
}

# Wait for pods to stabilize
wait_for_pods() {
    echo -e "${YELLOW}Waiting for pods to stabilize...${NC}"

    kubectl wait --for=condition=ready pod \
        --all \
        --namespace="$NAMESPACE" \
        --timeout="${ROLLBACK_TIMEOUT}s" || {
        echo -e "${RED}Warning: Some pods may not be ready${NC}"
        kubectl get pods -n "$NAMESPACE"
    }

    echo -e "${GREEN}✓ Pods stabilized${NC}"
}

# Validate rollback
validate_rollback() {
    echo -e "${YELLOW}Validating rollback...${NC}"

    local validation_passed=true

    # Check pod status
    local not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed" | wc -l)
    if [ "$not_ready" -gt 0 ]; then
        echo -e "${RED}✗ Some pods are not ready${NC}"
        kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed"
        validation_passed=false
    else
        echo -e "${GREEN}✓ All pods running${NC}"
    fi

    # Health check backend
    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$backend_pod" ]; then
        if kubectl exec -n "$NAMESPACE" "$backend_pod" -c backend -- curl -sf http://localhost:8000/health &> /dev/null; then
            echo -e "${GREEN}✓ Backend health check passed${NC}"
        else
            echo -e "${YELLOW}! Backend health check inconclusive${NC}"
        fi
    fi

    # Calculate rollback time
    local rollback_end=$(date +%s)
    local rollback_time=$((rollback_end - ROLLBACK_START))

    echo ""
    echo -e "${BLUE}Rollback Time: ${rollback_time} seconds${NC}"

    if [ "$rollback_time" -le "$ROLLBACK_TIMEOUT" ]; then
        echo -e "${GREEN}✓ Rollback completed within ${ROLLBACK_TIMEOUT}s target${NC}"
    else
        echo -e "${YELLOW}! Rollback exceeded ${ROLLBACK_TIMEOUT}s target${NC}"
    fi

    if [ "$validation_passed" = false ]; then
        echo -e "${RED}Rollback validation failed${NC}"
        return 1
    fi

    return 0
}

# Print rollback status
print_status() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}DOKS Rollback Complete!${NC}"
    echo "================================================"
    echo ""

    echo "Current Release:"
    helm list -n "$NAMESPACE"
    echo ""

    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""

    echo "Revision History:"
    helm history "$RELEASE_NAME" -n "$NAMESPACE" --max 5
    echo ""
}

# Emergency rollback - force delete and redeploy
emergency_rollback() {
    echo -e "${RED}EMERGENCY ROLLBACK - Force delete and redeploy${NC}"
    echo ""
    read -p "This will delete all pods and redeploy. Continue? (yes/no) " -r
    echo
    if [[ ! $REPLY =~ ^yes$ ]]; then
        exit 1
    fi

    echo "Deleting all pods in namespace..."
    kubectl delete pods --all -n "$NAMESPACE" --force --grace-period=0

    echo "Waiting for pods to restart..."
    sleep 10
    wait_for_pods

    echo -e "${GREEN}Emergency rollback complete${NC}"
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --revision N      Rollback to specific revision"
    echo "  --list            List available revisions"
    echo "  --namespace NS    Target namespace (default: ai-wealth)"
    echo "  --timeout SEC     Rollback timeout in seconds (default: 120)"
    echo "  --emergency       Force delete all pods and restart"
    echo "  --skip-validation Skip post-rollback validation"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Rollback to previous revision"
    echo "  $0 --revision 3       # Rollback to revision 3"
    echo "  $0 --list             # List available revisions"
    echo "  $0 --emergency        # Force restart all pods"
    echo ""
}

# Parse arguments
REVISION=""
LIST_ONLY=false
EMERGENCY=false
SKIP_VALIDATION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --revision)
            REVISION="$2"
            shift 2
            ;;
        --list)
            LIST_ONLY=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --timeout)
            ROLLBACK_TIMEOUT="$2"
            shift 2
            ;;
        --emergency)
            EMERGENCY=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
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
    check_cluster

    if [ "$LIST_ONLY" = true ]; then
        list_revisions
        exit 0
    fi

    if [ "$EMERGENCY" = true ]; then
        emergency_rollback
        exit 0
    fi

    list_revisions

    if [ -n "$REVISION" ]; then
        rollback_to_revision "$REVISION"
    else
        rollback_previous
    fi

    wait_for_pods

    if [ "$SKIP_VALIDATION" = false ]; then
        validate_rollback
    fi

    print_status
}

main "$@"
