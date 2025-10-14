#!/bin/bash

echo "🚀 Préparation du déploiement du bot Telegram..."
echo ""

# Vérifier si git est installé
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé. Installez-le d'abord : https://git-scm.com"
    exit 1
fi

# Initialiser git si nécessaire
if [ ! -d .git ]; then
    echo "📦 Initialisation de Git..."
    git init
    git add .
    git commit -m "Initial commit - Bot Telegram de commande"
    echo "✅ Git initialisé!"
else
    echo "✅ Git déjà initialisé"
fi

echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "1. Créez un repository sur GitHub :"
echo "   https://github.com/new"
echo ""
echo "2. Exécutez ces commandes (remplacez VOTRE_USERNAME) :"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/telegram-order-bot.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Déployez sur Railway :"
echo "   https://railway.app"
echo "   - Connectez-vous avec GitHub"
echo "   - Deploy from GitHub repo"
echo "   - Ajoutez les variables d'environnement :"
echo "     * TELEGRAM_BOT_TOKEN"
echo "     * ADMIN_ID"
echo ""
echo "📖 Guide complet : QUICK_DEPLOY.md"
echo ""
