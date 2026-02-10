#!/bin/bash
# Phase V: DigitalOcean Kubernetes (DOKS) Setup Script
# Provisions DOKS cluster with Dapr, Kafka (Strimzi), and required infrastructure

set -e

echo "================================================"
echo "AI Wealth Companion - DOKS Cluster Setup"
echo "Phase V: Cloud-Native Production System"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-ai-wealth-doks}"
REGION="${REGION:-nyc1}"
NODE_SIZE="${NODE_SIZE:-s-2vcpu-4gb}"
NODE_COUNT="${NODE_COUNT:-3}"
K8S_VERSION="${K8S_VERSION:-1.29}"
NAMESPACE="${NAMESPACE:-ai-wealth}"

# Dapr Configuration
DAPR_VERSION="${DAPR_VERSION:-1.12.0}"

# Strimzi Configuration
STRIMZI_VERSION="${STRIMZI_VERSION:-0.38.0}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check doctl
    if ! command -v doctl &> /dev/null; then
        echo -e "${RED}Error: doctl CLI is not installed${NC}"
        echo "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ doctl installed${NC}"

    # Check if authenticated
    if ! doctl auth list &> /dev/null; then
        echo -e "${RED}Error: doctl not authenticated${NC}"
        echo "Run: doctl auth init"
        exit 1
    fi
    echo -e "${GREEN}✓ doctl authenticated${NC}"

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

# Provision DOKS cluster
provision_cluster() {
    echo -e "${YELLOW}Provisioning DOKS cluster...${NC}"

    # Check if cluster already exists
    if doctl kubernetes cluster get "$CLUSTER_NAME" &> /dev/null; then
        echo -e "${GREEN}✓ Cluster '$CLUSTER_NAME' already exists${NC}"
        # Update kubeconfig
        doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
        echo -e "${GREEN}✓ Kubeconfig updated${NC}"
        return 0
    fi

    # Create cluster with auto-scaling node pool
    echo "Creating DOKS cluster: $CLUSTER_NAME"
    echo "  Region: $REGION"
    echo "  Node Size: $NODE_SIZE"
    echo "  Node Count: $NODE_COUNT"
    echo "  Kubernetes Version: $K8S_VERSION"

    doctl kubernetes cluster create "$CLUSTER_NAME" \
        --region "$REGION" \
        --version "$K8S_VERSION" \
        --node-pool "name=default;size=$NODE_SIZE;count=$NODE_COUNT;auto-scale=true;min-nodes=2;max-nodes=5" \
        --wait

    echo -e "${GREEN}✓ DOKS cluster created${NC}"

    # Save kubeconfig
    doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"
    echo -e "${GREEN}✓ Kubeconfig saved${NC}"
}

# Install NGINX Ingress Controller
install_ingress() {
    echo -e "${YELLOW}Installing NGINX Ingress Controller...${NC}"

    # Add ingress-nginx repo
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>/dev/null || true
    helm repo update

    # Check if already installed
    if helm status ingress-nginx -n ingress-nginx &> /dev/null; then
        echo -e "${GREEN}✓ NGINX Ingress already installed${NC}"
        return 0
    fi

    # Install NGINX Ingress
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.publishService.enabled=true \
        --set controller.service.type=LoadBalancer \
        --set controller.metrics.enabled=true \
        --set controller.podAnnotations."prometheus\.io/scrape"="true" \
        --set controller.podAnnotations."prometheus\.io/port"="10254"

    # Wait for ingress controller to be ready
    echo "Waiting for Ingress Controller LoadBalancer..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s

    echo -e "${GREEN}✓ NGINX Ingress Controller installed${NC}"

    # Get LoadBalancer IP
    echo ""
    echo "Ingress LoadBalancer IP:"
    kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
    echo ""
}

# Install cert-manager for TLS
install_cert_manager() {
    echo -e "${YELLOW}Installing cert-manager for TLS...${NC}"

    # Add Jetstack repo
    helm repo add jetstack https://charts.jetstack.io 2>/dev/null || true
    helm repo update

    # Check if already installed
    if helm status cert-manager -n cert-manager &> /dev/null; then
        echo -e "${GREEN}✓ cert-manager already installed${NC}"
        return 0
    fi

    # Install cert-manager with CRDs
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true \
        --set prometheus.enabled=true

    # Wait for cert-manager to be ready
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/instance=cert-manager \
        --timeout=120s

    echo -e "${GREEN}✓ cert-manager installed${NC}"

    # Create Let's Encrypt ClusterIssuer
    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: ${ACME_EMAIL:-admin@example.com}
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

    echo -e "${GREEN}✓ Let's Encrypt ClusterIssuer created${NC}"
}

# Install Dapr
install_dapr() {
    echo -e "${YELLOW}Installing Dapr...${NC}"

    # Check if Dapr CLI is available
    if ! command -v dapr &> /dev/null; then
        echo "Installing Dapr CLI..."
        curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
    fi
    echo -e "${GREEN}✓ Dapr CLI available${NC}"

    # Check if Dapr is already installed in cluster
    if kubectl get namespace dapr-system &> /dev/null; then
        echo -e "${GREEN}✓ Dapr already installed in cluster${NC}"
        return 0
    fi

    # Initialize Dapr in Kubernetes
    dapr init -k --runtime-version "$DAPR_VERSION" --wait

    echo -e "${GREEN}✓ Dapr installed (version $DAPR_VERSION)${NC}"

    # Verify Dapr components
    dapr status -k
}

# Install Strimzi Kafka Operator
install_strimzi() {
    echo -e "${YELLOW}Installing Strimzi Kafka Operator...${NC}"

    # Add Strimzi repo
    helm repo add strimzi https://strimzi.io/charts/ 2>/dev/null || true
    helm repo update

    # Check if already installed
    if helm status strimzi-kafka-operator -n kafka &> /dev/null; then
        echo -e "${GREEN}✓ Strimzi Kafka Operator already installed${NC}"
        return 0
    fi

    # Create Kafka namespace
    kubectl create namespace kafka 2>/dev/null || true

    # Install Strimzi Operator
    helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
        --namespace kafka \
        --version "$STRIMZI_VERSION" \
        --set watchAnyNamespace=true

    # Wait for operator to be ready
    kubectl wait --namespace kafka \
        --for=condition=ready pod \
        --selector=name=strimzi-cluster-operator \
        --timeout=300s

    echo -e "${GREEN}✓ Strimzi Kafka Operator installed (version $STRIMZI_VERSION)${NC}"
}

# Create application namespace with Dapr enabled
create_namespace() {
    echo -e "${YELLOW}Creating application namespace...${NC}"

    # Create namespace with Dapr injection enabled
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
  labels:
    app.kubernetes.io/name: ai-wealth-companion
    app.kubernetes.io/part-of: ai-wealth-ecosystem
    dapr.io/inject: "true"
EOF

    echo -e "${GREEN}✓ Namespace '$NAMESPACE' created with Dapr injection enabled${NC}"
}

# Print cluster info
print_cluster_info() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}DOKS Cluster Setup Complete!${NC}"
    echo "================================================"
    echo ""

    echo -e "${BLUE}Cluster Info:${NC}"
    kubectl cluster-info
    echo ""

    echo -e "${BLUE}Nodes:${NC}"
    kubectl get nodes
    echo ""

    echo -e "${BLUE}Ingress LoadBalancer:${NC}"
    kubectl get svc -n ingress-nginx ingress-nginx-controller
    echo ""

    echo -e "${BLUE}Dapr Status:${NC}"
    dapr status -k || true
    echo ""

    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Configure DNS to point to Ingress LoadBalancer IP"
    echo "  2. Create secrets: kubectl create secret -n $NAMESPACE ..."
    echo "  3. Deploy Kafka cluster: kubectl apply -f helm/ai-wealth-companion/templates/kafka/"
    echo "  4. Deploy application: ./scripts/doks-deploy.sh"
    echo ""
}

# Show usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --cluster-name NAME    Cluster name (default: ai-wealth-doks)"
    echo "  --region REGION        DigitalOcean region (default: nyc1)"
    echo "  --node-size SIZE       Node size (default: s-2vcpu-4gb)"
    echo "  --node-count COUNT     Initial node count (default: 3)"
    echo "  --namespace NS         Application namespace (default: ai-wealth)"
    echo "  --skip-ingress         Skip NGINX Ingress installation"
    echo "  --skip-cert-manager    Skip cert-manager installation"
    echo "  --skip-dapr            Skip Dapr installation"
    echo "  --skip-strimzi         Skip Strimzi Kafka installation"
    echo "  --help                 Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ACME_EMAIL             Email for Let's Encrypt certificates"
    echo ""
}

# Parse arguments
SKIP_INGRESS=false
SKIP_CERT_MANAGER=false
SKIP_DAPR=false
SKIP_STRIMZI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cluster-name)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --node-size)
            NODE_SIZE="$2"
            shift 2
            ;;
        --node-count)
            NODE_COUNT="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --skip-ingress)
            SKIP_INGRESS=true
            shift
            ;;
        --skip-cert-manager)
            SKIP_CERT_MANAGER=true
            shift
            ;;
        --skip-dapr)
            SKIP_DAPR=true
            shift
            ;;
        --skip-strimzi)
            SKIP_STRIMZI=true
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
    check_prerequisites
    provision_cluster

    if [ "$SKIP_INGRESS" = false ]; then
        install_ingress
    fi

    if [ "$SKIP_CERT_MANAGER" = false ]; then
        install_cert_manager
    fi

    if [ "$SKIP_DAPR" = false ]; then
        install_dapr
    fi

    if [ "$SKIP_STRIMZI" = false ]; then
        install_strimzi
    fi

    create_namespace
    print_cluster_info
}

main "$@"
