#!/bin/bash
# =============================================================================
# AI Wealth Companion - Complete Installation & Deployment Script
# =============================================================================
# This script automatically:
# 1. Installs Minikube & Helm (if not present)
# 2. Starts Kubernetes cluster
# 3. Builds Docker images
# 4. Creates secrets
# 5. Deploys the application
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=============================================="
echo "  AI Wealth Companion - Auto Install & Deploy"
echo "=============================================="
echo -e "${NC}"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version 2>/dev/null; then
            OS="wsl"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    echo -e "${YELLOW}Detected OS: $OS${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Minikube
install_minikube() {
    if command_exists minikube; then
        echo -e "${GREEN}✓ Minikube already installed: $(minikube version --short)${NC}"
        return 0
    fi

    echo -e "${YELLOW}Installing Minikube...${NC}"

    case $OS in
        linux|wsl)
            curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
            sudo install minikube-linux-amd64 /usr/local/bin/minikube
            rm minikube-linux-amd64
            ;;
        macos)
            if command_exists brew; then
                brew install minikube
            else
                curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
                sudo install minikube-darwin-amd64 /usr/local/bin/minikube
                rm minikube-darwin-amd64
            fi
            ;;
        *)
            echo -e "${RED}Please install Minikube manually: https://minikube.sigs.k8s.io/docs/start/${NC}"
            exit 1
            ;;
    esac

    echo -e "${GREEN}✓ Minikube installed${NC}"
}

# Install Helm
install_helm() {
    if command_exists helm; then
        echo -e "${GREEN}✓ Helm already installed: $(helm version --short)${NC}"
        return 0
    fi

    echo -e "${YELLOW}Installing Helm...${NC}"

    case $OS in
        linux|wsl)
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
            ;;
        macos)
            if command_exists brew; then
                brew install helm
            else
                curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
            fi
            ;;
        *)
            echo -e "${RED}Please install Helm manually: https://helm.sh/docs/intro/install/${NC}"
            exit 1
            ;;
    esac

    echo -e "${GREEN}✓ Helm installed${NC}"
}

# Install kubectl
install_kubectl() {
    if command_exists kubectl; then
        echo -e "${GREEN}✓ kubectl already installed${NC}"
        return 0
    fi

    echo -e "${YELLOW}Installing kubectl...${NC}"

    case $OS in
        linux|wsl)
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
            sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
            rm kubectl
            ;;
        macos)
            if command_exists brew; then
                brew install kubectl
            else
                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
                chmod +x kubectl
                sudo mv kubectl /usr/local/bin/kubectl
            fi
            ;;
    esac

    echo -e "${GREEN}✓ kubectl installed${NC}"
}

# Check Docker
check_docker() {
    if ! command_exists docker; then
        echo -e "${RED}Docker is not installed!${NC}"
        echo "Please install Docker Desktop from: https://docker.com/products/docker-desktop"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker is not running!${NC}"
        echo "Please start Docker Desktop and try again."
        exit 1
    fi

    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Start Minikube
start_minikube() {
    echo -e "${YELLOW}Starting Minikube cluster...${NC}"

    if minikube status | grep -q "Running" 2>/dev/null; then
        echo -e "${GREEN}✓ Minikube already running${NC}"
    else
        minikube start --cpus=2 --memory=3072 --driver=docker
        echo -e "${GREEN}✓ Minikube started${NC}"
    fi

    # Enable addons
    echo -e "${YELLOW}Enabling addons...${NC}"
    minikube addons enable ingress
    minikube addons enable metrics-server
    echo -e "${GREEN}✓ Addons enabled${NC}"
}

# Build Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images in Minikube...${NC}"

    # Point to Minikube's Docker daemon
    eval $(minikube docker-env)

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

    # Build backend
    echo "Building backend..."
    docker build -t ai-wealth-companion/backend:dev "$PROJECT_DIR/backend"
    echo -e "${GREEN}✓ Backend image built${NC}"

    # Build frontend
    echo "Building frontend..."
    docker build -t ai-wealth-companion/frontend:dev "$PROJECT_DIR/frontend"
    echo -e "${GREEN}✓ Frontend image built${NC}"
}

# Create secrets
create_secrets() {
    echo -e "${YELLOW}Creating Kubernetes secrets...${NC}"

    # Create namespace
    kubectl create namespace ai-wealth 2>/dev/null || true

    # Check if secrets already exist
    if kubectl get secret db-credentials -n ai-wealth &>/dev/null; then
        echo -e "${GREEN}✓ Secrets already exist${NC}"
        return 0
    fi

    echo ""
    echo -e "${BLUE}Please provide your credentials (or press Enter for defaults):${NC}"
    echo ""

    # Database URL
    read -p "DATABASE_URL [sqlite:///./dev.db]: " DB_URL
    DB_URL=${DB_URL:-"sqlite:///./dev.db"}

    # JWT Secret
    read -p "JWT_SECRET_KEY [auto-generate]: " JWT_SECRET
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || echo "super-secret-jwt-key-change-in-production")
    fi

    # Gemini API Key
    read -p "GEMINI_API_KEY [skip]: " GEMINI_KEY
    GEMINI_KEY=${GEMINI_KEY:-"placeholder-key"}

    # Create secrets
    kubectl create secret generic db-credentials \
        --from-literal=DATABASE_URL="$DB_URL" \
        -n ai-wealth

    kubectl create secret generic jwt-secret \
        --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
        -n ai-wealth

    kubectl create secret generic ai-credentials \
        --from-literal=GEMINI_API_KEY="$GEMINI_KEY" \
        --from-literal=OPENAI_API_KEY="placeholder" \
        -n ai-wealth

    echo -e "${GREEN}✓ Secrets created${NC}"
}

# Deploy with Helm
deploy_helm() {
    echo -e "${YELLOW}Deploying with Helm...${NC}"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    CHART_PATH="$PROJECT_DIR/helm/ai-wealth-companion"

    # Deploy
    helm upgrade --install ai-wealth "$CHART_PATH" \
        --namespace ai-wealth \
        --create-namespace \
        -f "$CHART_PATH/values-dev.yaml"

    echo -e "${GREEN}✓ Helm deployment complete${NC}"
}

# Wait for pods
wait_for_pods() {
    echo -e "${YELLOW}Waiting for pods to be ready...${NC}"

    kubectl wait --for=condition=ready pod \
        --all \
        --namespace=ai-wealth \
        --timeout=300s || {
        echo -e "${RED}Timeout waiting for pods${NC}"
        kubectl get pods -n ai-wealth
        return 1
    }

    echo -e "${GREEN}✓ All pods are ready${NC}"
}

# Setup hosts
setup_hosts() {
    echo -e "${YELLOW}Setting up hosts file...${NC}"

    MINIKUBE_IP=$(minikube ip)

    if grep -q "ai-wealth.local" /etc/hosts; then
        echo -e "${GREEN}✓ Hosts entry already exists${NC}"
    else
        echo "$MINIKUBE_IP ai-wealth.local" | sudo tee -a /etc/hosts
        echo -e "${GREEN}✓ Added hosts entry${NC}"
    fi
}

# Print status
print_status() {
    echo ""
    echo -e "${BLUE}=============================================="
    echo "           DEPLOYMENT COMPLETE!"
    echo "==============================================${NC}"
    echo ""

    echo -e "${GREEN}Pods:${NC}"
    kubectl get pods -n ai-wealth
    echo ""

    echo -e "${GREEN}Services:${NC}"
    kubectl get svc -n ai-wealth
    echo ""

    MINIKUBE_IP=$(minikube ip)
    echo -e "${GREEN}Access your application:${NC}"
    echo "  URL: http://ai-wealth.local"
    echo "  Minikube IP: $MINIKUBE_IP"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  kubectl get pods -n ai-wealth        # Check pods"
    echo "  kubectl logs -f <pod> -n ai-wealth   # View logs"
    echo "  minikube dashboard                   # Open dashboard"
    echo "  helm uninstall ai-wealth -n ai-wealth # Remove deployment"
    echo ""
}

# Main
main() {
    detect_os

    echo ""
    echo -e "${BLUE}Step 1/7: Checking prerequisites...${NC}"
    check_docker

    echo ""
    echo -e "${BLUE}Step 2/7: Installing tools...${NC}"
    install_kubectl
    install_minikube
    install_helm

    echo ""
    echo -e "${BLUE}Step 3/7: Starting Minikube...${NC}"
    start_minikube

    echo ""
    echo -e "${BLUE}Step 4/7: Building Docker images...${NC}"
    build_images

    echo ""
    echo -e "${BLUE}Step 5/7: Creating secrets...${NC}"
    create_secrets

    echo ""
    echo -e "${BLUE}Step 6/7: Deploying with Helm...${NC}"
    deploy_helm

    echo ""
    echo -e "${BLUE}Step 7/7: Waiting for deployment...${NC}"
    wait_for_pods
    setup_hosts

    print_status
}

# Run
main "$@"
