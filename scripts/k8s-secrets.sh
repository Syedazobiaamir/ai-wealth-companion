#!/bin/bash
# Phase IV: Kubernetes Secrets Creation Script
# Creates required secrets for AI Wealth Companion deployment

set -e

echo "================================================"
echo "AI Wealth Companion - Secrets Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-wealth}"

# Create namespace if it doesn't exist
create_namespace() {
    echo -e "${YELLOW}Ensuring namespace exists...${NC}"
    kubectl create namespace $NAMESPACE 2>/dev/null || true
    echo -e "${GREEN}✓ Namespace ready${NC}"
}

# Prompt for secret value with default
prompt_secret() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

# Prompt for secret value (hidden)
prompt_secret_hidden() {
    local prompt="$1"
    local result

    read -s -p "$prompt: " result
    echo ""
    echo "$result"
}

# Create database credentials secret
create_db_secret() {
    echo ""
    echo -e "${YELLOW}Creating database credentials secret...${NC}"

    if kubectl get secret db-credentials -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secret db-credentials already exists. Overwrite? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        kubectl delete secret db-credentials -n $NAMESPACE
    fi

    echo "Enter your Neon PostgreSQL connection string:"
    DATABASE_URL=$(prompt_secret_hidden "DATABASE_URL (e.g., postgresql+asyncpg://user:pass@host/db)")

    if [ -z "$DATABASE_URL" ]; then
        echo -e "${YELLOW}Skipping db-credentials (no value provided)${NC}"
        return
    fi

    kubectl create secret generic db-credentials \
        --namespace=$NAMESPACE \
        --from-literal=DATABASE_URL="$DATABASE_URL"

    echo -e "${GREEN}✓ Created db-credentials secret${NC}"
}

# Create JWT secret
create_jwt_secret() {
    echo ""
    echo -e "${YELLOW}Creating JWT secret...${NC}"

    if kubectl get secret jwt-secret -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secret jwt-secret already exists. Overwrite? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        kubectl delete secret jwt-secret -n $NAMESPACE
    fi

    # Generate a random secret if not provided
    DEFAULT_JWT=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    JWT_SECRET_KEY=$(prompt_secret "JWT_SECRET_KEY (press Enter for random)" "$DEFAULT_JWT")

    kubectl create secret generic jwt-secret \
        --namespace=$NAMESPACE \
        --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY"

    echo -e "${GREEN}✓ Created jwt-secret secret${NC}"
}

# Create AI credentials secret
create_ai_secret() {
    echo ""
    echo -e "${YELLOW}Creating AI credentials secret...${NC}"

    if kubectl get secret ai-credentials -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secret ai-credentials already exists. Overwrite? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        kubectl delete secret ai-credentials -n $NAMESPACE
    fi

    GEMINI_API_KEY=$(prompt_secret_hidden "GEMINI_API_KEY")
    OPENAI_API_KEY=$(prompt_secret_hidden "OPENAI_API_KEY (optional, press Enter to skip)")

    if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}Skipping ai-credentials (no values provided)${NC}"
        return
    fi

    kubectl create secret generic ai-credentials \
        --namespace=$NAMESPACE \
        --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
        --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}"

    echo -e "${GREEN}✓ Created ai-credentials secret${NC}"
}

# Create OAuth credentials secret
create_oauth_secret() {
    echo ""
    echo -e "${YELLOW}Creating OAuth credentials secret...${NC}"

    if kubectl get secret oauth-credentials -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secret oauth-credentials already exists. Overwrite? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        kubectl delete secret oauth-credentials -n $NAMESPACE
    fi

    echo "Google OAuth credentials:"
    GOOGLE_CLIENT_ID=$(prompt_secret "GOOGLE_CLIENT_ID" "")
    GOOGLE_CLIENT_SECRET=$(prompt_secret_hidden "GOOGLE_CLIENT_SECRET")

    echo ""
    echo "GitHub OAuth credentials:"
    GITHUB_CLIENT_ID=$(prompt_secret "GITHUB_CLIENT_ID" "")
    GITHUB_CLIENT_SECRET=$(prompt_secret_hidden "GITHUB_CLIENT_SECRET")

    if [ -z "$GOOGLE_CLIENT_ID" ] && [ -z "$GITHUB_CLIENT_ID" ]; then
        echo -e "${YELLOW}Skipping oauth-credentials (no values provided)${NC}"
        return
    fi

    kubectl create secret generic oauth-credentials \
        --namespace=$NAMESPACE \
        --from-literal=GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-}" \
        --from-literal=GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-}" \
        --from-literal=GITHUB_CLIENT_ID="${GITHUB_CLIENT_ID:-}" \
        --from-literal=GITHUB_CLIENT_SECRET="${GITHUB_CLIENT_SECRET:-}"

    echo -e "${GREEN}✓ Created oauth-credentials secret${NC}"
}

# Show current secrets
show_secrets() {
    echo ""
    echo "Current secrets in namespace $NAMESPACE:"
    kubectl get secrets -n $NAMESPACE 2>/dev/null || echo "No secrets found"
}

# Usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all           Create all secrets interactively"
    echo "  --db            Create database credentials only"
    echo "  --jwt           Create JWT secret only"
    echo "  --ai            Create AI credentials only"
    echo "  --oauth         Create OAuth credentials only"
    echo "  --show          Show current secrets"
    echo "  --namespace NS  Use custom namespace (default: ai-wealth)"
    echo "  --help          Show this help message"
}

# Main execution
main() {
    local create_all=false
    local create_db=false
    local create_jwt=false
    local create_ai=false
    local create_oauth=false
    local show_only=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                create_all=true
                shift
                ;;
            --db)
                create_db=true
                shift
                ;;
            --jwt)
                create_jwt=true
                shift
                ;;
            --ai)
                create_ai=true
                shift
                ;;
            --oauth)
                create_oauth=true
                shift
                ;;
            --show)
                show_only=true
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

    # Default to all if no specific option
    if [ "$create_all" = false ] && [ "$create_db" = false ] && \
       [ "$create_jwt" = false ] && [ "$create_ai" = false ] && \
       [ "$create_oauth" = false ] && [ "$show_only" = false ]; then
        create_all=true
    fi

    if [ "$show_only" = true ]; then
        show_secrets
        exit 0
    fi

    create_namespace

    if [ "$create_all" = true ] || [ "$create_db" = true ]; then
        create_db_secret
    fi

    if [ "$create_all" = true ] || [ "$create_jwt" = true ]; then
        create_jwt_secret
    fi

    if [ "$create_all" = true ] || [ "$create_ai" = true ]; then
        create_ai_secret
    fi

    if [ "$create_all" = true ] || [ "$create_oauth" = true ]; then
        create_oauth_secret
    fi

    echo ""
    echo -e "${GREEN}Secrets setup complete!${NC}"
    show_secrets
}

main "$@"
