# =============================================================================
# AI Wealth Companion - Windows Installation & Deployment Script
# =============================================================================
# Run this in PowerShell as Administrator
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Blue
Write-Host "  AI Wealth Companion - Auto Install & Deploy" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue
Write-Host ""

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run as Administrator!" -ForegroundColor Red
    exit 1
}

# Check winget
function Test-Winget {
    try {
        winget --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Install tools via winget
function Install-Tools {
    Write-Host "Installing tools via winget..." -ForegroundColor Yellow

    # Docker Desktop
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
        winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
        Write-Host "Please start Docker Desktop and rerun this script" -ForegroundColor Red
        exit 1
    }
    Write-Host "Docker installed" -ForegroundColor Green

    # Minikube
    if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Minikube..." -ForegroundColor Yellow
        winget install -e --id Kubernetes.minikube --accept-package-agreements --accept-source-agreements
    }
    Write-Host "Minikube installed" -ForegroundColor Green

    # Helm
    if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Helm..." -ForegroundColor Yellow
        winget install -e --id Helm.Helm --accept-package-agreements --accept-source-agreements
    }
    Write-Host "Helm installed" -ForegroundColor Green

    # kubectl
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Host "Installing kubectl..." -ForegroundColor Yellow
        winget install -e --id Kubernetes.kubectl --accept-package-agreements --accept-source-agreements
    }
    Write-Host "kubectl installed" -ForegroundColor Green
}

# Start Minikube
function Start-MinikubeCluster {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow

    $status = minikube status 2>$null
    if ($status -match "Running") {
        Write-Host "Minikube already running" -ForegroundColor Green
    } else {
        minikube start --cpus=4 --memory=8192 --driver=docker
        Write-Host "Minikube started" -ForegroundColor Green
    }

    # Enable addons
    minikube addons enable ingress
    minikube addons enable metrics-server
    Write-Host "Addons enabled" -ForegroundColor Green
}

# Build images
function Build-Images {
    Write-Host "Building Docker images..." -ForegroundColor Yellow

    # Set Minikube Docker env
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression

    $projectDir = Split-Path -Parent $PSScriptRoot

    # Build backend
    docker build -t ai-wealth-companion/backend:dev "$projectDir\backend"
    Write-Host "Backend image built" -ForegroundColor Green

    # Build frontend
    docker build -t ai-wealth-companion/frontend:dev "$projectDir\frontend"
    Write-Host "Frontend image built" -ForegroundColor Green
}

# Create secrets
function New-Secrets {
    Write-Host "Creating secrets..." -ForegroundColor Yellow

    kubectl create namespace ai-wealth 2>$null

    # Check existing
    $existing = kubectl get secret db-credentials -n ai-wealth 2>$null
    if ($existing) {
        Write-Host "Secrets already exist" -ForegroundColor Green
        return
    }

    # Prompt for values
    $dbUrl = Read-Host "DATABASE_URL [sqlite:///./dev.db]"
    if ([string]::IsNullOrEmpty($dbUrl)) { $dbUrl = "sqlite:///./dev.db" }

    $jwtSecret = Read-Host "JWT_SECRET_KEY [auto-generate]"
    if ([string]::IsNullOrEmpty($jwtSecret)) { $jwtSecret = [guid]::NewGuid().ToString() }

    $geminiKey = Read-Host "GEMINI_API_KEY [skip]"
    if ([string]::IsNullOrEmpty($geminiKey)) { $geminiKey = "placeholder" }

    # Create secrets
    kubectl create secret generic db-credentials --from-literal=DATABASE_URL="$dbUrl" -n ai-wealth
    kubectl create secret generic jwt-secret --from-literal=JWT_SECRET_KEY="$jwtSecret" -n ai-wealth
    kubectl create secret generic ai-credentials --from-literal=GEMINI_API_KEY="$geminiKey" -n ai-wealth

    Write-Host "Secrets created" -ForegroundColor Green
}

# Deploy
function Deploy-Helm {
    Write-Host "Deploying with Helm..." -ForegroundColor Yellow

    $projectDir = Split-Path -Parent $PSScriptRoot
    $chartPath = "$projectDir\helm\ai-wealth-companion"

    helm upgrade --install ai-wealth $chartPath `
        --namespace ai-wealth `
        --create-namespace `
        -f "$chartPath\values-dev.yaml"

    Write-Host "Helm deployment complete" -ForegroundColor Green
}

# Wait for pods
function Wait-ForPods {
    Write-Host "Waiting for pods..." -ForegroundColor Yellow

    kubectl wait --for=condition=ready pod --all --namespace=ai-wealth --timeout=300s

    Write-Host "All pods ready" -ForegroundColor Green
}

# Setup hosts
function Set-HostsEntry {
    Write-Host "Setting up hosts file..." -ForegroundColor Yellow

    $minikubeIp = minikube ip
    $hostsFile = "C:\Windows\System32\drivers\etc\hosts"
    $entry = "$minikubeIp ai-wealth.local"

    $content = Get-Content $hostsFile
    if ($content -match "ai-wealth.local") {
        Write-Host "Hosts entry exists" -ForegroundColor Green
    } else {
        Add-Content -Path $hostsFile -Value $entry
        Write-Host "Hosts entry added" -ForegroundColor Green
    }
}

# Print status
function Show-Status {
    Write-Host ""
    Write-Host "==============================================" -ForegroundColor Blue
    Write-Host "           DEPLOYMENT COMPLETE!" -ForegroundColor Blue
    Write-Host "==============================================" -ForegroundColor Blue
    Write-Host ""

    kubectl get pods -n ai-wealth
    Write-Host ""

    $minikubeIp = minikube ip
    Write-Host "Access: http://ai-wealth.local" -ForegroundColor Green
    Write-Host "Minikube IP: $minikubeIp" -ForegroundColor Green
}

# Main
if (-not (Test-Winget)) {
    Write-Host "winget not found. Please install App Installer from Microsoft Store" -ForegroundColor Red
    exit 1
}

Install-Tools
Start-MinikubeCluster
Build-Images
New-Secrets
Deploy-Helm
Wait-ForPods
Set-HostsEntry
Show-Status
