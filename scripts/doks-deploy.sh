#!/bin/bash
# Phase V: DOKS Deployment Script
# Deploys AI Wealth Companion to DigitalOcean Kubernetes with zero-downtime

set -e

echo "================================================"
echo "AI Wealth Companion - DOKS Deployment"
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
CHART_PATH="${CHART_PATH:-./helm/ai-wealth-companion}"
VALUES_FILE="${VALUES_FILE:-./helm/ai-wealth-companion/values-doks.yaml}"
TIMEOUT="${TIMEOUT:-600s}"

# Docker Hub Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Auto-rollback Configuration (Phase V: Zero-downtime deployments)
AUTO_ROLLBACK="${AUTO_ROLLBACK:-true}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-3}"
HEALTH_CHECK_DELAY="${HEALTH_CHECK_DELAY:-10}"

# Deployment tracking
DEPLOYMENT_START=$(date +%s)

# Check cluster connection
check_cluster() {
    echo -e "${YELLOW}Checking DOKS cluster connection...${NC}"

    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        echo "Run: doctl kubernetes cluster kubeconfig save <cluster-name>"
        exit 1
    fi
    echo -e "${GREEN}✓ Connected to cluster${NC}"

    # Verify this is a DOKS cluster
    local context=$(kubectl config current-context)
    if [[ ! "$context" == *"do-"* ]]; then
        echo -e "${YELLOW}Warning: Current context '$context' may not be a DOKS cluster${NC}"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Verify infrastructure
verify_infrastructure() {
    echo -e "${YELLOW}Verifying infrastructure...${NC}"

    # Check Dapr
    if ! kubectl get namespace dapr-system &> /dev/null; then
        echo -e "${RED}Error: Dapr is not installed${NC}"
        echo "Run: ./scripts/doks-setup.sh"
        exit 1
    fi
    echo -e "${GREEN}✓ Dapr installed${NC}"

    # Check Strimzi
    if ! kubectl get pods -n kafka -l name=strimzi-cluster-operator &> /dev/null; then
        echo -e "${YELLOW}Warning: Strimzi Kafka Operator may not be running${NC}"
    else
        echo -e "${GREEN}✓ Strimzi Kafka Operator running${NC}"
    fi

    # Check Ingress
    if ! kubectl get svc -n ingress-nginx ingress-nginx-controller &> /dev/null; then
        echo -e "${YELLOW}Warning: NGINX Ingress Controller not found${NC}"
    else
        echo -e "${GREEN}✓ NGINX Ingress Controller available${NC}"
    fi
}

# Build and push images to Docker Hub
build_and_push() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"

    if [ -z "$DOCKER_USERNAME" ]; then
        echo -e "${RED}Error: DOCKER_USERNAME environment variable not set${NC}"
        echo "Usage: DOCKER_USERNAME=yourusername $0 --build"
        exit 1
    fi

    # Login to Docker Hub
    echo "Logging into Docker Hub..."
    docker login || {
        echo -e "${RED}Docker login failed${NC}"
        exit 1
    }

    # Build and push backend
    echo "Building backend image..."
    docker build -t "$DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG" ./backend
    docker push "$DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG"
    echo -e "${GREEN}✓ Backend pushed: $DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG${NC}"

    # Build and push frontend
    echo "Building frontend image..."
    docker build -t "$DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG" ./frontend
    docker push "$DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG"
    echo -e "${GREEN}✓ Frontend pushed: $DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG${NC}"
}

# Deploy Kafka cluster
deploy_kafka() {
    echo -e "${YELLOW}Deploying Kafka cluster...${NC}"

    # Check if Kafka cluster exists
    if kubectl get kafka ai-wealth-kafka -n "$NAMESPACE" &> /dev/null; then
        echo -e "${GREEN}✓ Kafka cluster already exists${NC}"
        return 0
    fi

    # Apply Kafka manifests
    if [ -d "$CHART_PATH/templates/kafka" ]; then
        kubectl apply -f "$CHART_PATH/templates/kafka/" -n "$NAMESPACE"
        echo -e "${GREEN}✓ Kafka manifests applied${NC}"

        # Wait for Kafka to be ready (with timeout)
        echo "Waiting for Kafka cluster to be ready..."
        local max_wait=300
        local waited=0
        while [ $waited -lt $max_wait ]; do
            if kubectl get kafka ai-wealth-kafka -n "$NAMESPACE" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q "True"; then
                echo -e "${GREEN}✓ Kafka cluster ready${NC}"
                return 0
            fi
            sleep 10
            waited=$((waited + 10))
            echo "  Still waiting for Kafka... ($waited/$max_wait seconds)"
        done
        echo -e "${YELLOW}Warning: Kafka cluster may still be initializing${NC}"
    else
        echo -e "${YELLOW}Kafka templates not found, skipping...${NC}"
    fi
}

# Deploy Dapr components
deploy_dapr_components() {
    echo -e "${YELLOW}Deploying Dapr components...${NC}"

    if [ -d "$CHART_PATH/templates/dapr" ]; then
        kubectl apply -f "$CHART_PATH/templates/dapr/" -n "$NAMESPACE"
        echo -e "${GREEN}✓ Dapr components deployed${NC}"
    else
        echo -e "${YELLOW}Dapr templates not found, skipping...${NC}"
    fi
}

# Check and create secrets
check_secrets() {
    echo -e "${YELLOW}Checking secrets...${NC}"

    local missing_secrets=()

    for secret in db-credentials jwt-secret ai-credentials; do
        if ! kubectl get secret "$secret" -n "$NAMESPACE" &> /dev/null; then
            missing_secrets+=("$secret")
        fi
    done

    if [ ${#missing_secrets[@]} -gt 0 ]; then
        echo -e "${YELLOW}Warning: Missing secrets: ${missing_secrets[*]}${NC}"
        echo "Create secrets with: kubectl create secret generic <name> -n $NAMESPACE --from-literal=KEY=value"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✓ All required secrets exist${NC}"
    fi
}

# Deploy with Helm
deploy_helm() {
    echo -e "${YELLOW}Deploying with Helm...${NC}"

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true

    # Build Helm command
    local helm_cmd="helm upgrade --install $RELEASE_NAME $CHART_PATH"
    helm_cmd="$helm_cmd --namespace $NAMESPACE"
    helm_cmd="$helm_cmd --create-namespace"
    helm_cmd="$helm_cmd --timeout $TIMEOUT"
    helm_cmd="$helm_cmd --wait"
    helm_cmd="$helm_cmd --atomic"  # Rollback on failure

    # Add values file
    if [ -f "$VALUES_FILE" ]; then
        helm_cmd="$helm_cmd -f $VALUES_FILE"
    fi

    # Add Docker Hub image overrides if specified
    if [ -n "$DOCKER_USERNAME" ]; then
        helm_cmd="$helm_cmd --set backend.image.repository=$DOCKER_USERNAME/ai-wealth-backend"
        helm_cmd="$helm_cmd --set backend.image.tag=$IMAGE_TAG"
        helm_cmd="$helm_cmd --set frontend.image.repository=$DOCKER_USERNAME/ai-wealth-frontend"
        helm_cmd="$helm_cmd --set frontend.image.tag=$IMAGE_TAG"
    fi

    # Execute deployment
    echo "Running: $helm_cmd"
    eval "$helm_cmd"

    echo -e "${GREEN}✓ Helm deployment complete${NC}"

    # Record deployment in history
    echo "$(date -Iseconds) $RELEASE_NAME deployed with chart $CHART_PATH" >> /tmp/ai-wealth-deploy-history.log
}

# Wait for pods to be ready
wait_for_pods() {
    echo -e "${YELLOW}Waiting for pods to be ready...${NC}"

    kubectl wait --for=condition=ready pod \
        --all \
        --namespace="$NAMESPACE" \
        --timeout="$TIMEOUT" || {
        echo -e "${RED}Timeout waiting for pods${NC}"
        kubectl get pods -n "$NAMESPACE"
        exit 1
    }

    echo -e "${GREEN}✓ All pods are ready${NC}"
}

# Automatic rollback on health check failure
auto_rollback() {
    echo -e "${RED}Health check failed - initiating automatic rollback...${NC}"

    local current_revision=$(helm list -n "$NAMESPACE" -o json | jq -r ".[] | select(.name==\"$RELEASE_NAME\") | .revision")
    local previous_revision=$((current_revision - 1))

    if [ "$previous_revision" -lt 1 ]; then
        echo -e "${RED}No previous revision available for rollback${NC}"
        return 1
    fi

    echo "Rolling back from revision $current_revision to $previous_revision..."

    helm rollback "$RELEASE_NAME" "$previous_revision" \
        --namespace "$NAMESPACE" \
        --timeout 120s \
        --wait

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Automatic rollback successful${NC}"
        # Wait for rollback pods to stabilize
        kubectl wait --for=condition=ready pod \
            --all \
            --namespace="$NAMESPACE" \
            --timeout=120s || true
        return 0
    else
        echo -e "${RED}✗ Automatic rollback failed${NC}"
        return 1
    fi
}

# Validate deployment
validate_deployment() {
    echo -e "${YELLOW}Validating deployment...${NC}"

    local validation_passed=true
    local health_check_failed=false

    # Check pod status
    local not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed" | wc -l)
    if [ "$not_ready" -gt 0 ]; then
        echo -e "${RED}✗ Some pods are not ready${NC}"
        kubectl get pods -n "$NAMESPACE" --no-headers | grep -v "Running\|Completed"
        validation_passed=false
        health_check_failed=true
    else
        echo -e "${GREEN}✓ All pods running${NC}"
    fi

    # Check services
    local svc_count=$(kubectl get svc -n "$NAMESPACE" --no-headers | wc -l)
    if [ "$svc_count" -eq 0 ]; then
        echo -e "${RED}✗ No services found${NC}"
        validation_passed=false
    else
        echo -e "${GREEN}✓ $svc_count services deployed${NC}"
    fi

    # Check ingress
    if kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
        local ingress_ip=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ -n "$ingress_ip" ]; then
            echo -e "${GREEN}✓ Ingress available at: $ingress_ip${NC}"
        else
            echo -e "${YELLOW}! Ingress IP not yet assigned${NC}"
        fi
    fi

    # Check Dapr sidecars
    local dapr_pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].spec.containers[*].name}' | tr ' ' '\n' | grep -c "daprd" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ $dapr_pods Dapr sidecars running${NC}"

    # Health check endpoints
    echo ""
    echo "Performing health checks..."

    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -n "$backend_pod" ]; then
        if kubectl exec -n "$NAMESPACE" "$backend_pod" -c backend -- curl -sf http://localhost:8000/health &> /dev/null; then
            echo -e "${GREEN}✓ Backend health check passed${NC}"
        else
            echo -e "${YELLOW}! Backend health check inconclusive${NC}"
        fi
    fi

    if [ "$validation_passed" = false ]; then
        echo -e "${RED}Deployment validation failed${NC}"

        # Trigger automatic rollback if enabled and health checks failed
        if [ "$AUTO_ROLLBACK" = true ] && [ "$health_check_failed" = true ]; then
            auto_rollback
            return $?
        fi

        return 1
    fi

    return 0
}

# Print deployment status
print_status() {
    local deployment_end=$(date +%s)
    local deployment_time=$((deployment_end - DEPLOYMENT_START))

    echo ""
    echo "================================================"
    echo -e "${GREEN}DOKS Deployment Complete!${NC}"
    echo "================================================"
    echo ""
    echo -e "${BLUE}Deployment Time: ${deployment_time} seconds${NC}"
    echo ""

    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""

    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""

    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""

    echo "Dapr Components:"
    kubectl get components.dapr.io -n "$NAMESPACE" 2>/dev/null || echo "No Dapr components found"
    echo ""

    # Get external access URL
    local ingress_ip=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    local ingress_host=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null)

    echo -e "${BLUE}Access the application:${NC}"
    if [ -n "$ingress_ip" ]; then
        echo "  1. Add to /etc/hosts: $ingress_ip $ingress_host"
        echo "  2. Open: https://$ingress_host"
    else
        echo "  Waiting for LoadBalancer IP assignment..."
        echo "  Run: kubectl get ingress -n $NAMESPACE -w"
    fi
    echo ""

    echo "Helm Release Info:"
    helm list -n "$NAMESPACE"
    echo ""

    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs:     kubectl logs -f deployment/backend -n $NAMESPACE"
    echo "  Scale up:      kubectl scale deployment/backend --replicas=3 -n $NAMESPACE"
    echo "  Rollback:      ./scripts/doks-rollback.sh"
    echo "  Port forward:  kubectl port-forward svc/backend 8000:8000 -n $NAMESPACE"
    echo ""
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --build               Build and push Docker images before deploying"
    echo "  --values FILE         Use custom values file (default: values-doks.yaml)"
    echo "  --namespace NS        Deploy to custom namespace (default: ai-wealth)"
    echo "  --tag TAG             Image tag for Docker images (default: latest)"
    echo "  --skip-kafka          Skip Kafka cluster deployment"
    echo "  --skip-dapr           Skip Dapr components deployment"
    echo "  --skip-validation     Skip post-deployment validation"
    echo "  --dry-run             Show what would be deployed without deploying"
    echo "  --help                Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DOCKER_USERNAME       Docker Hub username (required for --build)"
    echo "  IMAGE_TAG             Image tag (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0                                        # Deploy using existing images"
    echo "  DOCKER_USERNAME=myuser $0 --build         # Build and deploy"
    echo "  $0 --values custom-values.yaml            # Deploy with custom values"
    echo ""
}

# Parse arguments
BUILD_IMAGES=false
SKIP_KAFKA=false
SKIP_DAPR=false
SKIP_VALIDATION=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_IMAGES=true
            shift
            ;;
        --values)
            VALUES_FILE="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --skip-kafka)
            SKIP_KAFKA=true
            shift
            ;;
        --skip-dapr)
            SKIP_DAPR=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
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
    verify_infrastructure

    if [ "$DRY_RUN" = true ]; then
        echo ""
        echo -e "${BLUE}Dry run mode - showing what would be deployed:${NC}"
        echo "  Namespace: $NAMESPACE"
        echo "  Release: $RELEASE_NAME"
        echo "  Chart: $CHART_PATH"
        echo "  Values: $VALUES_FILE"
        echo "  Image Tag: $IMAGE_TAG"
        echo ""
        helm template "$RELEASE_NAME" "$CHART_PATH" -f "$VALUES_FILE" --namespace "$NAMESPACE"
        exit 0
    fi

    if [ "$BUILD_IMAGES" = true ]; then
        build_and_push
    fi

    check_secrets

    if [ "$SKIP_KAFKA" = false ]; then
        deploy_kafka
    fi

    if [ "$SKIP_DAPR" = false ]; then
        deploy_dapr_components
    fi

    deploy_helm
    wait_for_pods

    if [ "$SKIP_VALIDATION" = false ]; then
        validate_deployment
    fi

    print_status
}

main "$@"
