# 🔐 Configuration des Secrets GitHub pour le Déploiement

Ce guide explique comment configurer les secrets GitHub Actions pour déployer automatiquement sur DigitalOcean.

## 📋 Secrets Requis

Vous devez configurer les secrets suivants dans votre repository GitHub :

### 1. Secrets de Connexion SSH

#### `SSH_PRIVATE_KEY`
**Description :** Clé SSH privée pour se connecter au droplet

**Comment l'obtenir :**

```bash
# Sur votre machine locale
# Si vous n'avez pas encore de clé SSH, créez-en une :
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Afficher la clé PRIVÉE (à copier dans GitHub Secret)
cat ~/.ssh/github_deploy

# Copier la clé PUBLIQUE sur votre droplet
ssh-copy-id -i ~/.ssh/github_deploy.pub root@YOUR_DROPLET_IP
# Ou manuellement :
cat ~/.ssh/github_deploy.pub
# Puis sur le droplet :
# echo "VOTRE_CLE_PUBLIQUE" >> ~/.ssh/authorized_keys
```

**Valeur :** Copiez TOUT le contenu de la clé privée, y compris :
```
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

#### `DROPLET_IP`
**Description :** Adresse IP de votre droplet DigitalOcean

**Comment l'obtenir :**
- Connectez-vous à DigitalOcean
- Trouvez votre droplet
- Copiez l'adresse IPv4

**Exemple :** `164.92.xxx.xxx`

#### `DROPLET_USER`
**Description :** Nom d'utilisateur pour la connexion SSH

**Valeurs courantes :**
- `root` (si vous utilisez l'utilisateur root)
- `deployer` (si vous avez créé un utilisateur dédié - recommandé)

**Recommandation :** Créez un utilisateur dédié sur le droplet :
```bash
# Sur le droplet
adduser deployer
usermod -aG sudo deployer
usermod -aG docker deployer
```

### 2. Secrets de l'Application

#### `CHAINLIT_AUTH_SECRET`
**Description :** Secret pour sécuriser l'application Chainlit

**Comment le générer :**
```bash
openssl rand -base64 32
```

**Exemple :** `xK8vN2mP9qR5sT7uW1yZ3aB4cD6eF8gH9iJ0kL2mN4oP6qR8sT0u=`

#### `CHAINLIT_URL`
**Description :** URL publique de votre chatbot

**Exemples :**
- Avec domaine : `https://chatbot.votre-domaine.com`
- Sans domaine : `http://164.92.xxx.xxx:8000`

#### `OPENAI_API_KEY`
**Description :** Clé API OpenAI (si vous utilisez OpenAI)

**Comment l'obtenir :**
1. Allez sur https://platform.openai.com/api-keys
2. Créez une nouvelle clé API
3. Copiez la clé (commence par `sk-...`)

**Exemple :** `sk-proj-abc123...`

#### `ANTHROPIC_API_KEY` (Optionnel)
**Description :** Clé API Anthropic Claude (alternative à OpenAI)

**Comment l'obtenir :**
1. Allez sur https://console.anthropic.com/
2. Créez une clé API
3. Copiez la clé (commence par `sk-ant-...`)

**Exemple :** `sk-ant-api03-abc123...`

---

## 🛠️ Comment Ajouter les Secrets dans GitHub

### Méthode 1 : Via l'Interface Web

1. **Allez sur votre repository GitHub**
2. **Cliquez sur Settings** (⚙️)
3. **Dans le menu de gauche** : Secrets and variables > Actions
4. **Cliquez sur "New repository secret"**
5. **Pour chaque secret** :
   - Entrez le **Name** (nom exact comme indiqué ci-dessus)
   - Collez la **Value** (valeur)
   - Cliquez sur **Add secret**

### Méthode 2 : Via GitHub CLI

```bash
# Installer GitHub CLI si nécessaire
brew install gh  # macOS
# ou : https://cli.github.com/

# Se connecter
gh auth login

# Ajouter les secrets
gh secret set SSH_PRIVATE_KEY < ~/.ssh/github_deploy
gh secret set DROPLET_IP -b "164.92.xxx.xxx"
gh secret set DROPLET_USER -b "root"
gh secret set CHAINLIT_AUTH_SECRET -b "$(openssl rand -base64 32)"
gh secret set CHAINLIT_URL -b "https://votre-domaine.com"
gh secret set OPENAI_API_KEY -b "sk-..."
gh secret set ANTHROPIC_API_KEY -b "sk-ant-..."
```

---

## ✅ Vérification des Secrets

### Vérifier que les secrets sont bien configurés :

1. Allez sur **Settings > Secrets and variables > Actions**
2. Vous devriez voir tous les secrets listés (les valeurs sont masquées)

### Liste complète des secrets requis :

- [x] `SSH_PRIVATE_KEY`
- [x] `DROPLET_IP`
- [x] `DROPLET_USER`
- [x] `CHAINLIT_AUTH_SECRET`
- [x] `CHAINLIT_URL`
- [x] `OPENAI_API_KEY` (ou ANTHROPIC_API_KEY)
- [ ] `ANTHROPIC_API_KEY` (optionnel)

---

## 🚀 Tester le Déploiement

### Déploiement Automatique

Le workflow se déclenche automatiquement à chaque push sur la branche `main` ou `master`.

```bash
git add .
git commit -m "Test deployment"
git push origin main
```

### Déploiement Manuel

1. Allez sur **Actions** dans votre repository
2. Sélectionnez le workflow **Deploy to DigitalOcean**
3. Cliquez sur **Run workflow**
4. Sélectionnez la branche
5. Cliquez sur **Run workflow**

### Suivre le Déploiement

1. Allez sur **Actions**
2. Cliquez sur le workflow en cours
3. Suivez les logs en temps réel

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Ne commitez JAMAIS les secrets** dans votre code
2. **Utilisez toujours les GitHub Secrets** pour les informations sensibles
3. **Créez un utilisateur dédié** pour les déploiements (pas root)
4. **Limitez les permissions** de la clé SSH au strict nécessaire
5. **Rotez régulièrement** vos secrets (API keys, SSH keys)

### Vérifier que .env n'est pas versionné

```bash
# Vérifier .gitignore
cat .gitignore | grep .env

# Si .env n'est pas listé, ajoutez-le :
echo ".env" >> .gitignore
```

---

## 🐛 Dépannage

### Erreur : "Permission denied (publickey)"

**Cause :** La clé SSH n'est pas correctement configurée

**Solution :**
1. Vérifiez que la clé publique est dans `~/.ssh/authorized_keys` sur le droplet
2. Vérifiez que la clé privée complète est dans `SSH_PRIVATE_KEY`
3. Testez manuellement : `ssh -i ~/.ssh/github_deploy user@droplet_ip`

### Erreur : "Host key verification failed"

**Cause :** Le droplet n'est pas dans known_hosts

**Solution :** Le workflow gère cela automatiquement avec `ssh-keyscan`

### Erreur : "docker: command not found"

**Cause :** Docker n'est pas installé sur le droplet

**Solution :**
```bash
ssh user@droplet_ip
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

### Le déploiement réussit mais l'app ne démarre pas

**Vérifier les logs :**
```bash
ssh user@droplet_ip
cd /opt/mindmoodle
docker-compose logs -f
```

---

## 📞 Aide Supplémentaire

### Commandes Utiles

```bash
# Tester la connexion SSH
ssh -i ~/.ssh/github_deploy user@droplet_ip

# Vérifier les secrets GitHub (liste seulement)
gh secret list

# Voir les logs du dernier déploiement
gh run view --log

# Relancer le dernier workflow
gh run rerun
```

### Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [DigitalOcean Droplet Documentation](https://docs.digitalocean.com/products/droplets/)

---

## 🎉 Félicitations !

Une fois tous les secrets configurés, votre application se déploiera automatiquement à chaque push sur GitHub ! 🚀
