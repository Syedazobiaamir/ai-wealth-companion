#!/bin/bash
# Phase IV: Kubernetes Deployment Script
# Deploys AI Wealth Companion to local Kubernetes cluster

set -e

echo "================================================"
echo "AI Wealth Companion - Kubernetes Deployment"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-wealth}"
RELEASE_NAME="${RELEASE_NAME:-ai-wealth}"
CHART_PATH="${CHART_PATH:-./helm/ai-wealth-companion}"
VALUES_FILE="${VALUES_FILE:-}"

# Check if Minikube is running
check_cluster() {
    echo -e "${YELLOW}Checking cluster status...${NC}"

    if ! minikube status | grep -q "Running"; then
        echo -e "${RED}Error: Minikube is not running${NC}"
        echo "Run: ./scripts/k8s-setup.sh"
        exit 1
    fi
    echo -e "${GREEN}✓ Minikube is running${NC}"
}

# Build Docker images in Minikube's Docker daemon
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"

    # Point to Minikube's Docker daemon
    eval $(minikube docker-env)

    # Build backend
    echo "Building backend image..."
    docker build -t ai-wealth-companion/backend:dev ./backend
    echo -e "${GREEN}✓ Backend image built${NC}"

    # Build frontend
    echo "Building frontend image..."
    docker build -t ai-wealth-companion/frontend:dev ./frontend
    echo -e "${GREEN}✓ Frontend image built${NC}"
}

# Build and push Docker images to Docker Hub
build_and_push_dockerhub() {
    echo -e "${YELLOW}Building and pushing Docker images to Docker Hub...${NC}"

    if [ -z "$DOCKER_USERNAME" ]; then
        echo -e "${RED}Error: DOCKER_USERNAME environment variable not set${NC}"
        echo "Usage: DOCKER_USERNAME=yourusername $0 --dockerhub"
        exit 1
    fi

    # Login to Docker Hub
    echo "Logging into Docker Hub..."
    docker login || {
        echo -e "${RED}Docker login failed${NC}"
        exit 1
    }

    IMAGE_TAG="${IMAGE_TAG:-latest}"

    # Build and push backend
    echo "Building and pushing backend image..."
    docker build -t $DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG ./backend
    docker push $DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG
    echo -e "${GREEN}✓ Backend image pushed to $DOCKER_USERNAME/ai-wealth-backend:$IMAGE_TAG${NC}"

    # Build and push frontend
    echo "Building and pushing frontend image..."
    docker build -t $DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG ./frontend
    docker push $DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG
    echo -e "${GREEN}✓ Frontend image pushed to $DOCKER_USERNAME/ai-wealth-frontend:$IMAGE_TAG${NC}"

    echo ""
    echo -e "${GREEN}Images pushed to Docker Hub!${NC}"
    echo "Update your values.yaml with:"
    echo "  backend.image.repository: $DOCKER_USERNAME/ai-wealth-backend"
    echo "  frontend.image.repository: $DOCKER_USERNAME/ai-wealth-frontend"
    echo "  backend.image.tag: $IMAGE_TAG"
    echo "  frontend.image.tag: $IMAGE_TAG"
}

# Check if secrets exist
check_secrets() {
    echo -e "${YELLOW}Checking secrets...${NC}"

    local missing_secrets=()

    for secret in db-credentials jwt-secret ai-credentials; do
        if ! kubectl get secret $secret -n $NAMESPACE &> /dev/null; then
            missing_secrets+=($secret)
        fi
    done

    if [ ${#missing_secrets[@]} -gt 0 ]; then
        echo -e "${YELLOW}Warning: Some secrets are missing: ${missing_secrets[*]}${NC}"
        echo "Run: ./scripts/k8s-secrets.sh to create secrets"
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
deploy() {
    echo -e "${YELLOW}Deploying with Helm...${NC}"

    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE 2>/dev/null || true

    # Build Helm command
    HELM_CMD="helm upgrade --install $RELEASE_NAME $CHART_PATH --namespace $NAMESPACE --create-namespace"

    # Add values file if specified
    if [ -n "$VALUES_FILE" ]; then
        HELM_CMD="$HELM_CMD -f $VALUES_FILE"
    fi

    # Add development values by default
    if [ -f "$CHART_PATH/values-dev.yaml" ]; then
        HELM_CMD="$HELM_CMD -f $CHART_PATH/values-dev.yaml"
    fi

    # Execute deployment
    echo "Running: $HELM_CMD"
    eval $HELM_CMD

    echo -e "${GREEN}✓ Helm deployment complete${NC}"
}

# Wait for pods to be ready
wait_for_pods() {
    echo -e "${YELLOW}Waiting for pods to be ready...${NC}"

    kubectl wait --for=condition=ready pod \
        --all \
        --namespace=$NAMESPACE \
        --timeout=300s || {
        echo -e "${RED}Timeout waiting for pods${NC}"
        kubectl get pods -n $NAMESPACE
        exit 1
    }

    echo -e "${GREEN}✓ All pods are ready${NC}"
}

# Print deployment status
print_status() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo "================================================"
    echo ""

    echo "Pods:"
    kubectl get pods -n $NAMESPACE
    echo ""

    echo "Services:"
    kubectl get svc -n $NAMESPACE
    echo ""

    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE
    echo ""

    local MINIKUBE_IP=$(minikube ip)
    echo "Access the application:"
    echo "  1. Add to /etc/hosts: $MINIKUBE_IP ai-wealth.local"
    echo "  2. Open: http://ai-wealth.local"
    echo ""
    echo "Or use port-forward:"
    echo "  kubectl port-forward svc/frontend 3000:3000 -n $NAMESPACE"
    echo "  kubectl port-forward svc/backend 8000:8000 -n $NAMESPACE"
    echo ""
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --build           Build Docker images in Minikube before deploying"
    echo "  --dockerhub       Build and push images to Docker Hub (requires DOCKER_USERNAME env var)"
    echo "  --values FILE     Use custom values file"
    echo "  --namespace NS    Deploy to custom namespace (default: ai-wealth)"
    echo "  --tag TAG         Image tag for Docker Hub push (default: latest)"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --build                           # Build locally in Minikube"
    echo "  DOCKER_USERNAME=myuser $0 --dockerhub  # Push to Docker Hub"
}

# Parse arguments
BUILD_IMAGES=false
PUSH_DOCKERHUB=false
IMAGE_TAG="${IMAGE_TAG:-latest}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_IMAGES=true
            shift
            ;;
        --dockerhub)
            PUSH_DOCKERHUB=true
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

    if [ "$PUSH_DOCKERHUB" = true ]; then
        build_and_push_dockerhub
        echo ""
        echo -e "${YELLOW}Note: Update your values.yaml with Docker Hub image names before deploying${NC}"
        read -p "Continue with deployment? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    elif [ "$BUILD_IMAGES" = true ]; then
        build_images
    fi

    check_secrets
    deploy
    wait_for_pods
    print_status
}

main
