# Déploiement Rapide sur Railway 🚀

## Étape 1 : Créer un compte GitHub (si vous n'en avez pas)
1. Allez sur [github.com](https://github.com)
2. Créez un compte gratuit

## Étape 2 : Pousser le code sur GitHub

Ouvrez le terminal dans ce dossier et exécutez :

```bash
# Initialiser git
git init

# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Bot Telegram prêt pour le déploiement"
```

Ensuite, créez un nouveau repository sur GitHub :
1. Allez sur github.com
2. Cliquez sur le "+" en haut à droite
3. Sélectionnez "New repository"
4. Nommez-le "telegram-order-bot"
5. Ne cochez RIEN (pas de README, pas de .gitignore)
6. Cliquez sur "Create repository"

Puis dans le terminal :

```bash
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/telegram-order-bot.git
git branch -M main
git push -u origin main
```

## Étape 3 : Déployer sur Railway

1. Allez sur [railway.app](https://railway.app)
2. Cliquez sur "Login" et connectez-vous avec GitHub
3. Cliquez sur "New Project"
4. Sélectionnez "Deploy from GitHub repo"
5. Choisissez votre repository "telegram-order-bot"
6. Railway va détecter automatiquement que c'est un projet Python

## Étape 4 : Configurer les variables d'environnement

1. Dans Railway, cliquez sur votre projet
2. Allez dans l'onglet "Variables"
3. Ajoutez ces deux variables :
   - `TELEGRAM_BOT_TOKEN` = `7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg`
   - `ADMIN_ID` = `1692775134`
4. Cliquez sur "Deploy" (si ce n'est pas automatique)

## Étape 5 : Vérifier que ça fonctionne ✅

1. Dans Railway, allez dans l'onglet "Deployments"
2. Cliquez sur le déploiement en cours
3. Regardez les logs - vous devriez voir "Bot démarré!"
4. Testez votre bot sur Telegram !

## 🎉 C'est tout ! Votre bot est maintenant en ligne 24/7 !

---

## Pour mettre à jour le bot plus tard

Modifiez votre code localement, puis :

```bash
git add .
git commit -m "Description des changements"
git push
```

Railway redéploiera automatiquement votre bot !

---

## Alternative : Render

Si Railway ne fonctionne pas, suivez le guide complet dans `DEPLOYMENT.md` pour utiliser Render.

---

## Besoin d'aide ?

- Railway : https://docs.railway.app
- GitHub : https://docs.github.com
