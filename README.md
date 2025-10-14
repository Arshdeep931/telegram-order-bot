# Bot Telegram de Commande 🤖

Bot Telegram pour collecter les informations de commande des clients et les transmettre à l'administrateur.

## 🚀 Déploiement Cloud (Recommandé)

**Le bot peut être hébergé gratuitement 24/7 sur le cloud !**

👉 **Suivez le guide rapide :** [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

Ou consultez le guide complet : [DEPLOYMENT.md](DEPLOYMENT.md)

## Fonctionnalités ✨

Le bot collecte les informations suivantes :
- 📍 Adresse de livraison
- 💰 Prix sous-total (HT)
- 💳 Prix TTC
- 💵 Moyen de paiement
- 📸 Screenshot du panier
- ⏰ Type de livraison (immédiate ou planifiée avec créneaux de 30 min)

Une fois toutes les informations collectées, le bot envoie un message privé à l'administrateur avec :
- Toutes les informations de la commande
- Le username Telegram du client (@username)
- Le screenshot du panier

## Installation 🚀

### 1. Installer Python

Assurez-vous d'avoir Python 3.8 ou supérieur installé sur votre système.

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Configuration ⚙️

### 1. Créer un bot Telegram

1. Ouvrez Telegram et recherchez **@BotFather**
2. Envoyez la commande `/newbot`
3. Suivez les instructions pour créer votre bot
4. Copiez le **token** fourni par BotFather

### 2. Obtenir votre ID Telegram

Pour recevoir les commandes, vous devez connaître votre ID Telegram :

1. Recherchez **@userinfobot** sur Telegram
2. Démarrez une conversation avec ce bot
3. Il vous donnera votre ID (un nombre comme `123456789`)

### 3. Configurer le bot

Ouvrez le fichier `telegram_bot.py` et modifiez les lignes suivantes :

```python
# Ligne 23 : Remplacer par votre ID Telegram
ADMIN_ID = 123456789  # Remplacer par votre vrai ID

# Ligne 243 : Remplacer par le token de votre bot
TOKEN = "VOTRE_TOKEN_BOT_ICI"  # Remplacer par le token fourni par BotFather
```

## Utilisation 🎯

### Démarrer le bot

```bash
python telegram_bot.py
```

Le bot sera maintenant en ligne et prêt à recevoir des commandes !

### Utilisation pour les clients

1. Les clients recherchent votre bot sur Telegram (par son nom ou @username)
2. Ils envoient `/start` pour commencer
3. Le bot leur pose les questions une par une :
   - Adresse de livraison
   - Prix sous-total
   - Prix TTC
   - Moyen de paiement (avec clavier personnalisé)
   - Screenshot du panier
   - Type de livraison (immédiate ou planifiée)
   - Si planifiée : choix du créneau de 30 minutes

4. Une fois terminé, vous recevez un message privé avec toutes les informations !

### Commandes disponibles

- `/start` - Démarrer une nouvelle commande
- `/cancel` - Annuler la commande en cours

## Structure du projet 📁

```
.
├── telegram_bot.py      # Code principal du bot
├── requirements.txt     # Dépendances Python
└── README.md           # Ce fichier
```

## Exemple de message reçu 📨

Quand un client passe une commande, vous recevrez un message comme celui-ci :

```
🛒 NOUVELLE COMMANDE
━━━━━━━━━━━━━━━━━━━━

👤 Client: Jean Dupont
📱 Username: @jeandupont

📍 Adresse de livraison:
123 Rue de la Paix, 75001 Paris

💰 Prix sous-total (HT): 45.50€
💳 Prix TTC: 54.60€
💵 Moyen de paiement: Carte bancaire

🚚 Type de livraison: Planifiée
⏰ Créneau: Aujourd'hui 15:30

📅 Date de commande: 14/10/2025 à 13:26
```

Suivi du screenshot du panier.

## Dépannage 🔧

### Le bot ne démarre pas

- Vérifiez que vous avez bien installé les dépendances : `pip install -r requirements.txt`
- Vérifiez que le token du bot est correct
- Vérifiez votre connexion Internet

### Je ne reçois pas les commandes

- Vérifiez que `ADMIN_ID` est bien configuré avec votre ID Telegram
- Vérifiez que vous avez démarré une conversation avec votre bot au moins une fois

### Erreur "Unauthorized"

- Le token du bot est incorrect, vérifiez-le auprès de @BotFather

## Personnalisation 🎨

Vous pouvez personnaliser :
- Les messages du bot (dans les fonctions `async def`)
- Les options de paiement (ligne 85)
- Le nombre de créneaux générés (ligne 167)
- Les emojis et le formatage

## Support 💬

Pour toute question ou problème, consultez la documentation officielle de python-telegram-bot :
https://docs.python-telegram-bot.org/

## Licence 📄

Ce projet est libre d'utilisation.
