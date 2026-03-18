#!/bin/bash

# Script de démarrage de la plateforme ChatOps
# Auteur: FEDI LIMEM
# Date: 18 Mars 2026

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}🚀 Démarrage de la Plateforme ChatOps${NC}"
echo -e "${YELLOW}========================================${NC}"

# ---------------------------------------------------------------------
# 1. Démarrer Colima si nécessaire
# ---------------------------------------------------------------------
echo -e "\n${YELLOW}[1/5] Vérification de Colima...${NC}"
if ! colima status 2>/dev/null | grep -q "Running"; then
    echo -e "${YELLOW}⚙️  Démarrage de Colima...${NC}"
    colima start --cpu 4 --memory 8
else
    echo -e "${GREEN}✅ Colima déjà en cours d'exécution${NC}"
fi

# ---------------------------------------------------------------------
# 2. Démarrer StackStorm
# ---------------------------------------------------------------------
echo -e "\n${YELLOW}[2/5] Démarrage de StackStorm...${NC}"
cd ~/st2-docker 2>/dev/null
if [ $? -eq 0 ]; then
    docker-compose up -d
    echo -e "${GREEN}✅ StackStorm démarré${NC}"
else
    echo -e "${RED}❌ Dossier st2-docker introuvable${NC}"
fi

# ---------------------------------------------------------------------
# 3. Démarrer les autres services
# ---------------------------------------------------------------------
echo -e "\n${YELLOW}[3/5] Démarrage des services...${NC}"

# Vault
if docker ps -a --format '{{.Names}}' | grep -q "^vault$"; then
    docker start vault 2>/dev/null && echo -e "${GREEN}✅ Vault 
démarré${NC}" || echo -e "${RED}❌ Erreur Vault${NC}"
else
    echo -e "${YELLOW}⚠️  Vault non trouvé, création...${NC}"
    docker run -d --name vault -p 8200:8200 -e 
VAULT_DEV_ROOT_TOKEN_ID=root -e VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200 
vault:1.13.3
fi

# Qdrant
if docker ps -a --format '{{.Names}}' | grep -q "^qdrant$"; then
    docker start qdrant 2>/dev/null && echo -e "${GREEN}✅ Qdrant 
démarré${NC}" || echo -e "${RED}❌ Erreur Qdrant${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant non trouvé, création...${NC}"
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v 
qdrant_data:/qdrant/storage qdrant/qdrant
fi

# Loki
if docker ps -a --format '{{.Names}}' | grep -q "^loki$"; then
    docker start loki 2>/dev/null && echo -e "${GREEN}✅ Loki 
démarré${NC}" || echo -e "${RED}❌ Erreur Loki${NC}"
else
    echo -e "${YELLOW}⚠️  Loki non trouvé, création...${NC}"
    docker run -d --name loki -p 3100:3100 grafana/loki:latest
fi

# Grafana
if docker ps -a --format '{{.Names}}' | grep -q "^grafana$"; then
    docker start grafana 2>/dev/null && echo -e "${GREEN}✅ Grafana 
démarré${NC}" || echo -e "${RED}❌ Erreur Grafana${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana non trouvé, création...${NC}"
    docker run -d --name grafana -p 3000:3000 grafana/grafana:latest
fi

# Promtail
if docker ps -a --format '{{.Names}}' | grep -q "^promtail$"; then
    docker start promtail 2>/dev/null && echo -e "${GREEN}✅ Promtail 
démarré${NC}" || echo -e "${RED}❌ Erreur Promtail${NC}"
else
    echo -e "${YELLOW}⚠️  Promtail non trouvé, création...${NC}"
    docker run -d --name promtail -v 
/var/run/docker.sock:/var/run/docker.sock --network logs-network 
grafana/promtail:latest
fi

# ---------------------------------------------------------------------
# 4. Configuration des réseaux
# ---------------------------------------------------------------------
echo -e "\n${YELLOW}[4/5] Configuration des réseaux...${NC}"

# Créer les réseaux s'ils n'existent pas
docker network create logs-network 2>/dev/null
docker network create st2-docker_public 2>/dev/null

# Connecter les services
docker network connect logs-network loki 2>/dev/null
docker network connect logs-network grafana 2>/dev/null
docker network connect logs-network promtail 2>/dev/null
docker network connect st2-docker_public vault 2>/dev/null
docker network connect st2-docker_public qdrant 2>/dev/null

# Connecter tous les conteneurs StackStorm
for container in $(docker ps --format '{{.Names}}' | grep st2); do
    docker network connect logs-network $container 2>/dev/null
    docker network connect st2-docker_public $container 2>/dev/null
done

echo -e "${GREEN}✅ Réseaux configurés${NC}"

# ---------------------------------------------------------------------
# 5. Vérification finale
# ---------------------------------------------------------------------
echo -e "\n${YELLOW}[5/5] Vérification des services...${NC}"
sleep 10

# Compter les conteneurs en cours d'exécution
RUNNING=$(docker ps --format '{{.Names}}' | wc -l)
echo -e "${GREEN}✅ $RUNNING conteneurs en cours d'exécution${NC}"

# Vérifier quelques services clés
echo -e ""
echo -e "📊 État des services :"

# StackStorm
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep st2 | head -5

# Services
echo -e ""
for service in vault qdrant loki grafana promtail; do
    if docker ps --format '{{.Names}}' | grep -q "^$service$"; then
        echo -e "${GREEN}✅ $service : en cours${NC}"
    else
        echo -e "${RED}❌ $service : arrêté${NC}"
    fi
done

# ---------------------------------------------------------------------
# FIN
# ---------------------------------------------------------------------
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ PLATEFORME DÉMARRÉE AVEC SUCCÈS !${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "📌 Accès aux interfaces :"
echo -e "   StackStorm: ${YELLOW}http://localhost:9101${NC} 
(st2admin/Ch@ngeMe)"
echo -e "   Grafana:    ${YELLOW}http://localhost:3000${NC} (admin/admin)"
echo -e "   Vault:      ${YELLOW}http://localhost:8200${NC} (token: root)"
echo -e "   Qdrant:     ${YELLOW}http://localhost:6333/dashboard${NC}"
echo -e ""
echo -e "📱 Commandes Telegram :"
echo -e "   /search postgres"
echo -e "   /rag postgres lent"
echo -e "   /jira Titre | Description | CHAT"
echo -e "   /issue Titre | Description | bug"
echo -e "   /restart nginx prod + /approve"
echo -e "   /deploy api staging"
echo -e "   /run echo 'Hello'"
echo -e ""
echo -e "🔗 GitHub: 
${YELLOW}https://github.com/fedifedifedi/chatops-project${NC}"
echo -e "${GREEN}========================================${NC}"
