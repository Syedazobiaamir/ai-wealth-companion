#!/bin/bash
# Phase IV: Kubernetes Setup Script
# Sets up Minikube cluster with required addons for AI Wealth Companion

set -e

echo "================================================"
echo "AI Wealth Companion - Kubernetes Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker installed${NC}"

    # Check Minikube
    if ! command -v minikube &> /dev/null; then
        echo -e "${RED}Error: Minikube is not installed${NC}"
        echo "Install: https://minikube.sigs.k8s.io/docs/start/"
        exit 1
    fi
    echo -e "${GREEN}✓ Minikube installed${NC}"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}Error: kubectl is not installed${NC}"
        echo "Install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    echo -e "${GREEN}✓ kubectl installed${NC}"

    # Check Helm
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}Error: Helm is not installed${NC}"
        echo "Install: https://helm.sh/docs/intro/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Helm installed${NC}"
}

# Start Minikube cluster
start_minikube() {
    echo -e "${YELLOW}Starting Minikube cluster...${NC}"

    # Check if Minikube is already running
    if minikube status | grep -q "Running"; then
        echo -e "${GREEN}✓ Minikube is already running${NC}"
    else
        # Start with recommended resources
        minikube start \
            --driver=docker \
            --cpus=2 \
            --memory=4096 \
            --disk-size=20g \
            --kubernetes-version=stable
        echo -e "${GREEN}✓ Minikube started${NC}"
    fi
}

# Enable required addons
enable_addons() {
    echo -e "${YELLOW}Enabling Minikube addons...${NC}"

    # Enable Ingress
    minikube addons enable ingress
    echo -e "${GREEN}✓ Ingress addon enabled${NC}"

    # Enable metrics-server for HPA
    minikube addons enable metrics-server
    echo -e "${GREEN}✓ Metrics server addon enabled${NC}"

    # Enable dashboard (optional)
    minikube addons enable dashboard
    echo -e "${GREEN}✓ Dashboard addon enabled${NC}"
}

# Setup kubectl-ai (if available)
setup_kubectl_ai() {
    echo -e "${YELLOW}Setting up kubectl-ai...${NC}"

    # Check if krew is installed
    if kubectl krew version &> /dev/null; then
        # Install kubectl-ai via krew
        if kubectl krew list | grep -q "ai"; then
            echo -e "${GREEN}✓ kubectl-ai already installed${NC}"
        else
            kubectl krew install ai 2>/dev/null || echo -e "${YELLOW}kubectl-ai not available in krew, skipping...${NC}"
        fi
    else
        echo -e "${YELLOW}krew not installed. kubectl-ai installation skipped.${NC}"
        echo "To install krew: https://krew.sigs.k8s.io/docs/user-guide/setup/install/"
    fi
}

# Setup kagent (if available)
setup_kagent() {
    echo -e "${YELLOW}Setting up kagent...${NC}"

    # kagent is typically a CRD-based tool
    # For now, we document it and let the Helm chart handle CRD installation
    echo -e "${YELLOW}kagent will be configured via Helm chart${NC}"
    echo -e "${GREEN}✓ kagent setup delegated to Helm deployment${NC}"
}

# Configure Docker environment for Minikube
configure_docker_env() {
    echo -e "${YELLOW}Configuring Docker environment...${NC}"
    echo ""
    echo "To build images directly in Minikube's Docker daemon, run:"
    echo -e "${GREEN}eval \$(minikube docker-env)${NC}"
    echo ""
}

# Print cluster info
print_cluster_info() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}Kubernetes Cluster Ready!${NC}"
    echo "================================================"
    echo ""
    kubectl cluster-info
    echo ""
    echo "Minikube IP: $(minikube ip)"
    echo ""
    echo "Next steps:"
    echo "  1. Build Docker images: eval \$(minikube docker-env) && docker build ..."
    echo "  2. Create secrets: ./scripts/k8s-secrets.sh"
    echo "  3. Deploy: ./scripts/k8s-deploy.sh"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    start_minikube
    enable_addons
    setup_kubectl_ai
    setup_kagent
    configure_docker_env
    print_cluster_info
}

main "$@"
