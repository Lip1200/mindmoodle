#!/bin/bash
# Deployment script for DigitalOcean Droplet

set -e

echo "🚀 Mental Health Chatbot - Deployment Script"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure your variables"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$CHAINLIT_AUTH_SECRET" ] || [ "$CHAINLIT_AUTH_SECRET" = "your-super-secret-key-change-me-in-production" ]; then
    echo -e "${RED}❌ Error: CHAINLIT_AUTH_SECRET not configured${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker compose build

echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker compose down

echo -e "${YELLOW}🚀 Starting containers...${NC}"
docker compose up -d

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Container status:"
docker compose ps

echo ""
echo "📝 View logs with: docker compose logs -f"
echo "🔍 Check health: docker compose ps"
echo "🛑 Stop service: docker compose down"

echo ""
echo -e "${GREEN}🎉 Your chatbot is now running!${NC}"
if [ ! -z "$DOMAIN" ]; then
    echo -e "Access it at: ${GREEN}https://$DOMAIN${NC}"
else
    echo -e "Access it at: ${GREEN}http://localhost:8000${NC}"
fi
