#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example and fill in all required values."
  exit 1
fi

git pull origin main

docker compose -f docker-compose.prod.yml up -d --build

DOMAIN=$(grep -E '^DOMAIN=' .env | cut -d= -f2)
echo "Deployed. App available at https://${DOMAIN}"
