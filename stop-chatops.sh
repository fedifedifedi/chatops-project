#!/bin/bash
cd ~/st2-docker && docker-compose down
docker stop vault qdrant loki grafana promtail 2>/dev/null
echo "✅ Plateforme arrêtée"
