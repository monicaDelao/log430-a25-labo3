# Script pour déployer manuellement sur la VM
# À exécuter sur la VM (10.194.32.238)

echo "=== Déploiement manuel sur VM ==="

# Créer le répertoire de déploiement
mkdir -p ~/log430-labo3-deploy
cd ~/log430-labo3-deploy

# Télécharger les fichiers nécessaires
curl -o docker-compose.vm.yml https://raw.githubusercontent.com/monicaDelao/log430-a25-labo3/main/scripts/docker-compose.yml
curl -o db-init.sql https://raw.githubusercontent.com/monicaDelao/log430-a25-labo3/main/db-init/init.sql

# Se connecter au registry GitHub
echo "Connexion au registry GitHub..."
echo $GITHUB_TOKEN | docker login ghcr.io -u monicaDelao --password-stdin

# Tirer l'image
echo "Téléchargement de l'image..."
docker pull ghcr.io/monicadelao/log430-a25-labo3/log430-labo3:production

# Créer le fichier docker-compose pour la VM
cat > docker-compose.vm.yml << 'EOF'
version: '3.8'
services:
  app:
    image: ghcr.io/monicadelao/log430-a25-labo3/log430-labo3:production
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_NAME=labo03_db
      - DB_USER=root
      - DB_PASS=root
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
    depends_on:
      - mysql
      - redis
    networks:
      - app-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=labo03_db
      - MYSQL_USER=labo03
      - MYSQL_PASSWORD=labo03
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network

volumes:
  mysql_data:

networks:
  app-network:
    driver: bridge
EOF

# Arrêter les anciens conteneurs
docker compose -f docker-compose.vm.yml down || true

# Démarrer les nouveaux conteneurs
echo "Démarrage des services..."
docker compose -f docker-compose.vm.yml up -d

# Attendre et tester
echo "Attente que les services démarrent..."
sleep 30

echo "Test de l'application..."
curl -f http://localhost:5000/health || {
    echo "ERREUR: L'application ne répond pas"
    echo "Logs de l'application:"
    docker compose -f docker-compose.vm.yml logs app
    exit 1
}

echo "SUCCESS: Application déployée et fonctionnelle!"
echo "L'application est accessible sur http://10.194.32.238:5000"

# Afficher le statut
docker compose -f docker-compose.vm.yml ps