#!/usr/bin/env bash
set -euo pipefail

# Costa Coffee Frontline AI Agent - Azure Container Apps Deployment
# Usage: ./deploy.sh [resource-group] [location]

RESOURCE_GROUP="${1:-costa-mcp-rg}"
LOCATION="${2:-uksouth}"
ACR_NAME="costamcpacr$(openssl rand -hex 4)"
APP_NAME="costa-mcp-server"
ENVIRONMENT_NAME="costa-mcp-env"
IMAGE_TAG="latest"

echo "=== Costa Coffee MCP Server - Azure Container Apps Deployment ==="
echo "Resource Group : $RESOURCE_GROUP"
echo "Location       : $LOCATION"
echo ""

# 1. Login check
echo "[1/8] Checking Azure login..."
az account show --query "user.name" -o tsv || { echo "Run 'az login' first"; exit 1; }

# 2. Create resource group
echo "[2/8] Creating resource group $RESOURCE_GROUP..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" -o none

# 3. Create Azure Container Registry
echo "[3/8] Creating Container Registry $ACR_NAME..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --admin-enabled true \
  -o none

# 4. Build and push image
echo "[4/8] Building and pushing Docker image..."
az acr build \
  --registry "$ACR_NAME" \
  --image "$APP_NAME:$IMAGE_TAG" \
  .

# 5. Get ACR credentials
ACR_SERVER="${ACR_NAME}.azurecr.io"
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# 6. Create Container Apps environment
echo "[5/8] Creating Container Apps environment..."
az containerapp env create \
  --name "$ENVIRONMENT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  -o none

# 7. Deploy Container App
echo "[6/8] Deploying Container App..."
az containerapp create \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ENVIRONMENT_NAME" \
  --image "${ACR_SERVER}/${APP_NAME}:${IMAGE_TAG}" \
  --registry-server "$ACR_SERVER" \
  --registry-username "$ACR_NAME" \
  --registry-password "$ACR_PASSWORD" \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 5 \
  --env-vars MCP_HOST=0.0.0.0 MCP_PORT=8000 \
  -o none

# 8. Get FQDN
echo "[7/8] Retrieving app URL..."
FQDN=$(az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "=== Deployment Complete ==="
echo "MCP Server URL : https://${FQDN}"
echo "Health check   : https://${FQDN}/health"
echo ""
echo "To configure in your MCP client:"
echo '  {"mcpServers": {"costa": {"url": "https://'"${FQDN}"'/mcp"}}}'
