#!/bin/bash
# Phase IV: Kubernetes Teardown Script
# Removes AI Wealth Companion from local Kubernetes cluster

set -e

echo "================================================"
echo "AI Wealth Companion - Kubernetes Teardown"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-wealth}"
RELEASE_NAME="${RELEASE_NAME:-ai-wealth}"

# Uninstall Helm release
uninstall_release() {
    echo -e "${YELLOW}Uninstalling Helm release...${NC}"

    if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
        helm uninstall $RELEASE_NAME -n $NAMESPACE
        echo -e "${GREEN}✓ Helm release uninstalled${NC}"
    else
        echo -e "${YELLOW}No Helm release found${NC}"
    fi
}

# Delete secrets
delete_secrets() {
    echo -e "${YELLOW}Deleting secrets...${NC}"

    for secret in db-credentials jwt-secret ai-credentials oauth-credentials; do
        if kubectl get secret $secret -n $NAMESPACE &> /dev/null; then
            kubectl delete secret $secret -n $NAMESPACE
            echo -e "${GREEN}✓ Deleted secret: $secret${NC}"
        fi
    done
}

# Delete namespace
delete_namespace() {
    echo -e "${YELLOW}Deleting namespace...${NC}"

    if kubectl get namespace $NAMESPACE &> /dev/null; then
        kubectl delete namespace $NAMESPACE
        echo -e "${GREEN}✓ Namespace deleted${NC}"
    else
        echo -e "${YELLOW}Namespace does not exist${NC}"
    fi
}

# Clean up Docker images
cleanup_images() {
    echo -e "${YELLOW}Cleaning up Docker images...${NC}"

    # Point to Minikube's Docker daemon
    eval $(minikube docker-env)

    # Remove development images
    docker rmi ai-wealth-companion/backend:dev 2>/dev/null || true
    docker rmi ai-wealth-companion/frontend:dev 2>/dev/null || true

    echo -e "${GREEN}✓ Docker images cleaned${NC}"
}

# Stop Minikube
stop_minikube() {
    echo -e "${YELLOW}Stopping Minikube...${NC}"

    if minikube status | grep -q "Running"; then
        minikube stop
        echo -e "${GREEN}✓ Minikube stopped${NC}"
    else
        echo -e "${YELLOW}Minikube is not running${NC}"
    fi
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all           Remove everything including Minikube"
    echo "  --keep-secrets  Keep secrets when uninstalling"
    echo "  --keep-images   Keep Docker images"
    echo "  --namespace NS  Use custom namespace (default: ai-wealth)"
    echo "  --help          Show this help message"
}

# Parse arguments
REMOVE_ALL=false
KEEP_SECRETS=false
KEEP_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            REMOVE_ALL=true
            shift
            ;;
        --keep-secrets)
            KEEP_SECRETS=true
            shift
            ;;
        --keep-images)
            KEEP_IMAGES=true
            shift
            ;;
        --namespace)
            NAMESPACE="$2"
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
    uninstall_release

    if [ "$KEEP_SECRETS" = false ]; then
        delete_secrets
    fi

    delete_namespace

    if [ "$KEEP_IMAGES" = false ]; then
        cleanup_images
    fi

    if [ "$REMOVE_ALL" = true ]; then
        stop_minikube
    fi

    echo ""
    echo -e "${GREEN}Teardown complete!${NC}"
}

main
