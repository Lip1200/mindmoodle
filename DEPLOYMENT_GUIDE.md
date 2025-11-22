# 🚀 Guide de Déploiement - DigitalOcean

Guide complet pour déployer le chatbot Mental Health Support sur un droplet DigitalOcean.

## 📋 Prérequis

- Un compte DigitalOcean
- Un nom de domaine (optionnel mais recommandé)
- Docker et Docker Compose installés localement
- Clé API pour un service LLM (OpenAI, Anthropic, etc.)

## 🖥️ 1. Créer un Droplet DigitalOcean

1. **Connectez-vous à DigitalOcean**
2. **Créez un nouveau Droplet :**
   - **Image :** Ubuntu 22.04 LTS
   - **Plan :** Basic (2 GB RAM / 1 vCPU minimum recommandé)
   - **Datacenter :** Choisissez le plus proche (Europe - Frankfurt/Amsterdam)
   - **Authentification :** Clé SSH (recommandé)
   - **Hostname :** `mindmoodle-chatbot`

3. **Notez l'adresse IP** de votre droplet

## 🔧 2. Configuration du Droplet

### Connexion SSH

```bash
ssh root@your_droplet_ip
```

### Installation de Docker

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installer Docker Compose
apt install docker-compose -y

# Vérifier l'installation
docker --version
docker-compose --version
```

### Installation de Nginx (reverse proxy)

```bash
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

### Configuration du Firewall

```bash
# Autoriser SSH, HTTP et HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

## 📦 3. Déployer l'Application

### Méthode A : Déploiement Automatique avec GitHub Actions (Recommandé ⭐)

**Avantages :**
- Déploiement automatique à chaque push
- Pas besoin de connexion manuelle au serveur
- Historique des déploiements
- Rollback facile

**Configuration :**

1. **Configurer les secrets GitHub** (voir `.github/SETUP_SECRETS.md`) :
   - `SSH_PRIVATE_KEY` - Clé SSH pour accéder au droplet
   - `DROPLET_IP` - IP du droplet
   - `DROPLET_USER` - Utilisateur SSH (ex: root ou deployer)
   - `CHAINLIT_AUTH_SECRET` - Secret généré avec `openssl rand -base64 32`
   - `CHAINLIT_URL` - URL publique (ex: https://chatbot.unige.ch)
   - `OPENAI_API_KEY` - Clé API OpenAI

2. **Préparer le droplet** (une seule fois) :
```bash
# Sur le droplet
mkdir -p /opt/mindmoodle
```

3. **Push vers GitHub** :
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

4. **Suivre le déploiement** :
   - Allez sur GitHub > Actions
   - Suivez le workflow en temps réel

**Documentation complète :** Voir `.github/SETUP_SECRETS.md`

---

### Méthode B : Depuis Git (Manuel)

```bash
# Installer Git si nécessaire
apt install git -y

# Cloner le repository
cd /opt
git clone https://github.com/votre-username/mindmoodle.git
cd mindmoodle

# Copier et configurer les variables d'environnement
cp .env.example .env
nano .env
```

### Méthode C : Upload manuel

```bash
# Sur votre machine locale
scp -r /Users/Filipe/UNIGE/Master/hackademia/mindmoodle root@your_droplet_ip:/opt/

# Sur le droplet
cd /opt/mindmoodle
cp .env.example .env
nano .env
```

### Configuration de .env

Éditez `.env` avec vos valeurs :

```bash
CHAINLIT_AUTH_SECRET=votre-secret-super-securise-genere-aleatoirement
CHAINLIT_URL=https://votre-domaine.com
OPENAI_API_KEY=sk-votre-cle-api
CHAINLIT_TELEMETRY=false
COMPANION=dog
```

Pour générer un secret sécurisé :
```bash
openssl rand -base64 32
```

### Lancer l'application

```bash
# Rendre le script de déploiement exécutable
chmod +x deploy.sh

# Déployer
./deploy.sh
```

Ou manuellement :
```bash
docker-compose build
docker-compose up -d
```

### Vérifier le déploiement

```bash
# Voir les logs
docker-compose logs -f

# Vérifier le statut
docker-compose ps

# Tester localement
curl http://localhost:8000
```

## 🌐 4. Configuration Nginx

### Copier la configuration

```bash
cp nginx.conf /etc/nginx/sites-available/mindmoodle
```

### Éditer avec votre domaine

```bash
nano /etc/nginx/sites-available/mindmoodle
# Remplacez "your-domain.com" par votre domaine réel
```

### Activer la configuration

```bash
# Créer le lien symbolique
ln -s /etc/nginx/sites-available/mindmoodle /etc/nginx/sites-enabled/

# Supprimer la config par défaut
rm /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Recharger Nginx
systemctl reload nginx
```

## 🔒 5. Configuration SSL avec Let's Encrypt

### Installer Certbot

```bash
apt install certbot python3-certbot-nginx -y
```

### Obtenir un certificat SSL

```bash
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

Suivez les instructions interactives :
- Entrez votre email
- Acceptez les conditions
- Choisissez de rediriger HTTP vers HTTPS (recommandé)

### Renouvellement automatique

```bash
# Tester le renouvellement
certbot renew --dry-run

# Le renouvellement automatique est déjà configuré via cron
```

## 🔧 6. Configuration Moodle

### Mettre à jour le widget HTML

Dans `moodle_widget_animals.html`, changez :

```javascript
const CHAINLIT_SERVER_URL = 'https://votre-domaine.com';
```

### Intégrer dans Moodle

1. Connectez-vous à Moodle en tant qu'administrateur
2. Activez le mode édition
3. Ajoutez un bloc **HTML**
4. Collez le contenu de `moodle_widget_animals.html`
5. Sauvegardez

## 📊 7. Monitoring et Maintenance

### Voir les logs

```bash
# Logs en temps réel
docker-compose logs -f

# Logs des dernières 100 lignes
docker-compose logs --tail=100
```

### Redémarrer l'application

```bash
cd /opt/mindmoodle
docker-compose restart
```

### Mettre à jour l'application

```bash
cd /opt/mindmoodle
git pull  # Si depuis Git
docker-compose down
docker-compose build
docker-compose up -d
```

### Vérifier l'utilisation des ressources

```bash
# CPU et mémoire
docker stats

# Espace disque
df -h
docker system df
```

### Nettoyer les anciennes images

```bash
docker system prune -a --volumes
```

## 🔐 8. Sécurité

### Créer un utilisateur non-root

```bash
adduser deployer
usermod -aG sudo deployer
usermod -aG docker deployer
```

### Désactiver la connexion root par SSH

```bash
nano /etc/ssh/sshd_config
# Changez : PermitRootLogin no
systemctl restart sshd
```

### Installer Fail2Ban

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### Backups automatiques

Créez un script de backup :

```bash
nano /opt/backup.sh
```

Contenu :
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Backup de l'application
tar -czf $BACKUP_DIR/mindmoodle_$DATE.tar.gz /opt/mindmoodle

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "mindmoodle_*.tar.gz" -mtime +7 -delete
```

Rendre exécutable et ajouter au cron :
```bash
chmod +x /opt/backup.sh
crontab -e
# Ajouter : 0 2 * * * /opt/backup.sh
```

## 🐛 9. Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier la configuration
docker-compose config

# Reconstruire complètement
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Nginx ne peut pas se connecter au backend

```bash
# Vérifier que le container tourne
docker ps

# Vérifier les logs Nginx
tail -f /var/log/nginx/error.log

# Tester la connexion locale
curl http://localhost:8000
```

### WebSocket ne fonctionne pas

Vérifiez la configuration Nginx :
- `proxy_http_version 1.1;`
- `proxy_set_header Upgrade $http_upgrade;`
- `proxy_set_header Connection "upgrade";`

### Problèmes SSL

```bash
# Vérifier les certificats
certbot certificates

# Renouveler manuellement
certbot renew

# Tester la configuration SSL
nginx -t
```

## 📞 10. Support et Ressources

### Commandes utiles

```bash
# État du système
systemctl status nginx
systemctl status docker

# Utilisation des ressources
htop
df -h
free -h

# Logs système
journalctl -xe
```

### Documentation

- [DigitalOcean Docs](https://docs.digitalocean.com/)
- [Docker Docs](https://docs.docker.com/)
- [Chainlit Docs](https://docs.chainlit.io/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [Let's Encrypt Docs](https://letsencrypt.org/docs/)

## ✅ Checklist Pré-Production

- [ ] Variables d'environnement configurées
- [ ] Secret CHAINLIT_AUTH_SECRET sécurisé
- [ ] Clé API LLM configurée
- [ ] Domaine pointé vers le droplet
- [ ] SSL/HTTPS activé
- [ ] Firewall configuré
- [ ] Monitoring en place
- [ ] Backups configurés
- [ ] Widget Moodle mis à jour avec la bonne URL
- [ ] Tests de sécurité effectués
- [ ] Documentation à jour

## 🎉 Félicitations !

Votre chatbot Mental Health Support est maintenant déployé et prêt à aider les étudiants ! 🚀
