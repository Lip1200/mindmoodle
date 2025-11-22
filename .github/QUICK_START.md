# 🚀 Déploiement Rapide sur DigitalOcean avec GitHub Actions

Guide ultra-rapide pour déployer en 10 minutes.

## ⚡ Étapes Rapides

### 1. Préparer votre Droplet (5 min)

```bash
# Créer un droplet Ubuntu 22.04 sur DigitalOcean
# Note son IP : XXX.XXX.XXX.XXX

# Se connecter
ssh root@XXX.XXX.XXX.XXX

# Installer Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose -y

# Créer le dossier de déploiement
mkdir -p /opt/mindmoodle

# (Optionnel mais recommandé) Créer un utilisateur dédié
adduser deployer
usermod -aG sudo deployer
usermod -aG docker deployer
```

### 2. Générer une Clé SSH (2 min)

```bash
# Sur votre machine locale
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy -N ""

# Copier la clé publique sur le droplet
ssh-copy-id -i ~/.ssh/github_deploy.pub root@XXX.XXX.XXX.XXX

# Tester la connexion
ssh -i ~/.ssh/github_deploy root@XXX.XXX.XXX.XXX
```

### 3. Configurer les Secrets GitHub (3 min)

Allez sur votre repo GitHub > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

Créez ces secrets :

| Nom | Valeur | Comment l'obtenir |
|-----|--------|-------------------|
| `SSH_PRIVATE_KEY` | Contenu de `~/.ssh/github_deploy` | `cat ~/.ssh/github_deploy` |
| `DROPLET_IP` | `XXX.XXX.XXX.XXX` | IP de votre droplet |
| `DROPLET_USER` | `root` | ou `deployer` si créé |
| `CHAINLIT_AUTH_SECRET` | Secret aléatoire | `openssl rand -base64 32` |
| `CHAINLIT_URL` | `http://XXX.XXX.XXX.XXX:8000` | URL publique |
| `OPENAI_API_KEY` | `sk-proj-...` | Depuis platform.openai.com |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | (Optionnel) Depuis console.anthropic.com |

**Commande rapide** (avec GitHub CLI) :

```bash
# Installer gh si nécessaire : brew install gh
gh auth login

# Ajouter tous les secrets d'un coup
gh secret set SSH_PRIVATE_KEY < ~/.ssh/github_deploy
gh secret set DROPLET_IP -b "XXX.XXX.XXX.XXX"
gh secret set DROPLET_USER -b "root"
gh secret set CHAINLIT_AUTH_SECRET -b "$(openssl rand -base64 32)"
gh secret set CHAINLIT_URL -b "http://XXX.XXX.XXX.XXX:8000"
gh secret set OPENAI_API_KEY -b "sk-proj-VOTRE-CLE"
```

### 4. Déployer ! (30 secondes)

```bash
git add .
git commit -m "🚀 Initial deployment"
git push origin main
```

Allez sur **GitHub > Actions** et regardez le déploiement en temps réel ! 🎉

---

## ✅ Vérification

Une fois le workflow terminé (2-3 minutes) :

```bash
# Tester l'accès
curl http://XXX.XXX.XXX.XXX:8000

# Ou ouvrir dans le navigateur
open http://XXX.XXX.XXX.XXX:8000
```

---

## 🔒 (Optionnel) Ajouter un Domaine et SSL

### Configurer un domaine

1. Dans votre DNS, créez un enregistrement A pointant vers `XXX.XXX.XXX.XXX`
2. Attendez la propagation DNS (5-30 min)

### Installer Nginx et SSL

```bash
# Sur le droplet
apt install nginx certbot python3-certbot-nginx -y

# Copier la config Nginx
scp nginx.conf root@XXX.XXX.XXX.XXX:/etc/nginx/sites-available/mindmoodle

# Sur le droplet, éditer le fichier
nano /etc/nginx/sites-available/mindmoodle
# Remplacer "your-domain.com" par votre vrai domaine

# Activer la config
ln -s /etc/nginx/sites-available/mindmoodle /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# Obtenir le certificat SSL
certbot --nginx -d votre-domaine.com

# Mettre à jour le secret CHAINLIT_URL
gh secret set CHAINLIT_URL -b "https://votre-domaine.com"
```

---

## 🔄 Déploiements Futurs

À chaque push sur `main`, l'application se redéploie automatiquement !

```bash
# Faire une modification
git add .
git commit -m "✨ New feature"
git push
# 🚀 Auto-déployé !
```

---

## 🐛 Dépannage Express

### Le workflow échoue ?

```bash
# Vérifier les logs
# GitHub > Actions > Cliquer sur le workflow > Voir les étapes

# Problème SSH ?
ssh -i ~/.ssh/github_deploy root@XXX.XXX.XXX.XXX
# Si ça marche pas, refaire l'étape 2

# Problème Docker ?
ssh root@XXX.XXX.XXX.XXX
docker ps
docker-compose logs
```

### L'app ne démarre pas ?

```bash
ssh root@XXX.XXX.XXX.XXX
cd /opt/mindmoodle

# Voir les logs
docker-compose logs -f

# Reconstruire
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Aide

- Problème de secrets ? Voir `.github/SETUP_SECRETS.md`
- Guide complet ? Voir `DEPLOYMENT_GUIDE.md`
- Issues GitHub ? Ouvrez une issue sur le repo

---

## 🎉 C'est tout !

Votre chatbot est maintenant déployé et se met à jour automatiquement à chaque push ! 🚀
