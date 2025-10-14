# Déploiement du Bot Telegram sur le Cloud ☁️

Ce guide vous explique comment héberger votre bot Telegram gratuitement 24/7.

## Option 1 : Railway (Recommandé) 🚂

### Étape 1 : Préparer le code
Votre code est déjà prêt avec tous les fichiers nécessaires !

### Étape 2 : Créer un compte Railway
1. Allez sur [railway.app](https://railway.app)
2. Cliquez sur "Start a New Project"
3. Connectez-vous avec GitHub

### Étape 3 : Créer un repository GitHub
```bash
cd /Users/arsh/CascadeProjects/windsurf-project
git init
git add .
git commit -m "Initial commit - Telegram bot"
```

Créez un nouveau repository sur GitHub et poussez le code :
```bash
git remote add origin https://github.com/VOTRE_USERNAME/telegram-bot.git
git branch -M main
git push -u origin main
```

### Étape 4 : Déployer sur Railway
1. Sur Railway, cliquez sur "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Choisissez votre repository
4. Railway détectera automatiquement le `Procfile` et `requirements.txt`
5. Le bot se déploiera automatiquement !

### Étape 5 : Le bot est en ligne 24/7 ! ✅

---

## Option 2 : Render 🎨

### Étape 1 : Créer un compte Render
1. Allez sur [render.com](https://render.com)
2. Inscrivez-vous gratuitement

### Étape 2 : Créer un repository GitHub (même que Railway)
```bash
cd /Users/arsh/CascadeProjects/windsurf-project
git init
git add .
git commit -m "Initial commit - Telegram bot"
```

Poussez sur GitHub (si pas déjà fait).

### Étape 3 : Déployer sur Render
1. Sur Render, cliquez sur "New +"
2. Sélectionnez "Background Worker"
3. Connectez votre repository GitHub
4. Configurez :
   - **Name:** telegram-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python telegram_bot.py`
5. Cliquez sur "Create Background Worker"

### Étape 4 : Le bot est en ligne 24/7 ! ✅

---

## Option 3 : PythonAnywhere 🐍

### Étape 1 : Créer un compte
1. Allez sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Créez un compte gratuit

### Étape 2 : Uploader les fichiers
1. Allez dans "Files"
2. Uploadez `telegram_bot.py` et `requirements.txt`

### Étape 3 : Installer les dépendances
Dans la console Bash :
```bash
pip3 install --user -r requirements.txt
```

### Étape 4 : Créer une tâche Always-On
1. Allez dans "Tasks"
2. Créez une nouvelle tâche
3. Commande : `python3 telegram_bot.py`

---

## ⚠️ Important : Sécurité

**AVANT de pousser sur GitHub**, vous devriez mettre le token du bot dans une variable d'environnement !

### Modifier le code pour utiliser des variables d'environnement :

Dans `telegram_bot.py`, remplacez :
```python
TOKEN = "7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg"
ADMIN_ID = 1692775134
```

Par :
```python
import os
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'VOTRE_TOKEN_ICI')
ADMIN_ID = int(os.getenv('ADMIN_ID', '1692775134'))
```

Puis sur Railway/Render, ajoutez les variables d'environnement :
- `TELEGRAM_BOT_TOKEN` = `7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg`
- `ADMIN_ID` = `1692775134`

---

## Vérifier que le bot fonctionne

Une fois déployé, testez votre bot sur Telegram. Il devrait répondre immédiatement !

Pour voir les logs :
- **Railway** : Onglet "Deployments" → Cliquez sur le déploiement → "View Logs"
- **Render** : Onglet "Logs"
- **PythonAnywhere** : Fichiers de log dans le dossier

---

## Avantages de l'hébergement cloud

✅ Bot actif 24/7
✅ Pas besoin de garder votre ordinateur allumé
✅ Redémarre automatiquement en cas d'erreur
✅ Gratuit pour toujours (avec les plans gratuits)
✅ Facile à mettre à jour (push sur GitHub)

---

## Besoin d'aide ?

Si vous avez des questions, consultez la documentation :
- Railway : https://docs.railway.app
- Render : https://render.com/docs
- PythonAnywhere : https://help.pythonanywhere.com
