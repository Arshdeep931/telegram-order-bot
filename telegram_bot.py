#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram pour la collecte des informations de commande
"""

import logging
import os
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler,
)

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# États de la conversation
(
    RESTAURANT,      # 0
    ADRESSE,         # 1
    PRIX_SUBTOTAL,   # 2
    PRIX_TTC,        # 3
    MOYEN_PAIEMENT,  # 4
    SCREENSHOT,      # 5
    LIVRAISON_TYPE,  # 6
    CRENEAU,         # 7
    PRIX_CORRIGE     # 8 - État spécial après correction de prix
) = range(9)

# Configuration depuis les variables d'environnement (ou valeurs par défaut)
ADMIN_ID = int(os.getenv('ADMIN_ID', '1692775134'))
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg')
CHANNEL_ID = os.getenv('CHANNEL_ID', None)  # ID du canal pour les notifications


class OrderBot:
    def __init__(self):
        self.orders = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Démarre la conversation et demande le restaurant."""
        user = update.effective_user
        await update.message.reply_text(
            f"Bonjour {user.first_name}! 👋\n\n"
            "Je vais vous aider à passer votre commande.\n\n"
            "Pour commencer, veuillez indiquer le **nom du restaurant et la ville**\n"
            "(exemple: McDonald's Paris) :",
            parse_mode='Markdown'
        )
        
        # Initialiser les données de commande pour cet utilisateur
        context.user_data['order'] = {}
        context.user_data['order']['username'] = f"@{user.username}" if user.username else f"ID: {user.id}"
        context.user_data['order']['user_id'] = user.id
        context.user_data['order']['user_fullname'] = f"{user.first_name} {user.last_name or ''}".strip()
        
        return RESTAURANT

    async def restaurant(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre le restaurant et demande l'adresse."""
        context.user_data['order']['restaurant'] = update.message.text
        
        await update.message.reply_text(
            "✅ Restaurant enregistré!\n\n"
            "Maintenant, veuillez indiquer votre **adresse de livraison** complète :",
            parse_mode='Markdown'
        )
        
        return ADRESSE

    async def adresse(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre l'adresse et demande le prix sous-total."""
        context.user_data['order']['adresse'] = update.message.text
        
        await update.message.reply_text(
            "✅ Adresse enregistrée!\n\n"
            "Maintenant, veuillez indiquer le **prix sous-total** (HT) :"
        )
        
        return PRIX_SUBTOTAL

    async def prix_subtotal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre le prix sous-total et demande le prix TTC."""
        prix_text = update.message.text.replace('€', '').replace(',', '.').strip()
        
        try:
            # Extraire le nombre du texte
            prix = float(prix_text)
            
            # Vérifier le minimum de 20€
            if prix < 20:
                await update.message.reply_text(
                    "❌ Le prix sous-total minimum est de **20€**.\n\n"
                    "Veuillez indiquer un montant d'au moins 20€ :",
                    parse_mode='Markdown'
                )
                return PRIX_SUBTOTAL
            
            context.user_data['order']['prix_subtotal'] = update.message.text
            
            await update.message.reply_text(
                "✅ Prix sous-total enregistré!\n\n"
                "Veuillez indiquer le **prix TTC** (toutes taxes comprises) :"
            )
            
            return PRIX_TTC
            
        except ValueError:
            await update.message.reply_text(
                "❌ Veuillez entrer un prix valide (exemple: 25 ou 25.50) :"
            )
            return PRIX_SUBTOTAL

    async def prix_ttc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre le prix TTC et demande le moyen de paiement."""
        prix_ttc_text = update.message.text.replace('€', '').replace(',', '.').strip()
        
        try:
            # Extraire le nombre du texte
            prix_ttc = float(prix_ttc_text)
            
            # Récupérer le prix HT pour comparaison
            prix_ht_text = context.user_data['order']['prix_subtotal'].replace('€', '').replace(',', '.').strip()
            prix_ht = float(prix_ht_text)
            
            # Vérifier que le prix TTC est >= au prix HT
            if prix_ttc < prix_ht:
                await update.message.reply_text(
                    f"❌ Le prix TTC ({prix_ttc}€) ne peut pas être inférieur au prix HT ({prix_ht}€).\n\n"
                    "Veuillez entrer un prix TTC valide :",
                    parse_mode='Markdown'
                )
                return PRIX_TTC
            
            context.user_data['order']['prix_ttc'] = update.message.text
            
            # Clavier avec les options de paiement
            keyboard = [
                ['🏦 Virement instant', '📱 PayPal'],
                ['🍎 Apple Pay']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ Prix TTC enregistré!\n\n"
                "Quel sera votre **moyen de paiement** ?",
                reply_markup=reply_markup
            )
            
            return MOYEN_PAIEMENT
            
        except ValueError:
            await update.message.reply_text(
                "❌ Veuillez entrer un prix valide (exemple: 30 ou 30.50) :"
            )
            return PRIX_TTC

    async def moyen_paiement(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre le moyen de paiement et demande le screenshot."""
        context.user_data['order']['moyen_paiement'] = update.message.text
        
        # Uber One est obligatoire, donc on l'enregistre directement
        context.user_data['order']['uber_one'] = 'Obligatoire ✅'
        context.user_data['order']['uber_one_requis'] = True
        
        await update.message.reply_text(
            "✅ Moyen de paiement enregistré!\n\n"
            "⚠️ **Important:** Le restaurant doit accepter Uber One (obligatoire)\n\n"
            "Veuillez maintenant envoyer un **screenshot de votre panier** 📸",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
        
        return SCREENSHOT

    async def screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre le screenshot et demande le type de livraison."""
        if update.message.photo:
            # Récupérer la photo en meilleure qualité
            photo = update.message.photo[-1]
            context.user_data['order']['screenshot_file_id'] = photo.file_id
            
            # Boutons pour choisir entre commande immédiate ou planifiée
            keyboard = [
                [InlineKeyboardButton("🚀 Commander maintenant", callback_data='commander_maintenant')],
                [InlineKeyboardButton("📅 Planifier la livraison", callback_data='planifier')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ Screenshot du panier reçu!\n\n"
                "Souhaitez-vous **commander maintenant** ou **planifier** votre livraison ?",
                reply_markup=reply_markup
            )
            
            return LIVRAISON_TYPE
        else:
            await update.message.reply_text(
                "❌ Veuillez envoyer une image (screenshot de votre panier)."
            )
            return SCREENSHOT

    async def livraison_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Gère le choix entre livraison immédiate ou planifiée."""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'commander_maintenant':
            context.user_data['order']['type_livraison'] = 'Immédiate'
            context.user_data['order']['creneau'] = 'Dès que possible'
            
            # Envoyer la commande à l'admin
            await self.send_order_to_admin(context, query)
            
            await query.edit_message_text(
                "✅ **Commande enregistrée!**\n\n"
                "Un cuisto va vous envoyer un message privé dans quelques instants.\n\n"
                "📱 Restez à l'affût de vos notifications!\n\n"
                "Merci pour votre confiance! 🙏",
                parse_mode='Markdown'
            )
            
            return ConversationHandler.END
        
        elif query.data == 'planifier':
            await query.edit_message_text(
                "📅 Veuillez indiquer l'**heure de réception souhaitée**\n\n"
                "⚠️ **Important:** L'heure indiquée est l'heure à laquelle vous recevrez la commande (pas l'heure de lancement)\n\n"
                "Format: HH:MM (exemple: 14:30 ou 20:00)",
                parse_mode='Markdown'
            )
            
            context.user_data['order']['type_livraison'] = 'Planifiée'
            
            return CRENEAU

    def generate_time_slots(self):
        """Génère des créneaux horaires pour aujourd'hui et demain."""
        slots = []
        now = datetime.now()
        
        # Arrondir à la prochaine heure
        start_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        # Générer 24 créneaux (24 heures)
        for i in range(24):
            slot_time = start_time + timedelta(hours=i)
            
            # Format: "Aujourd'hui 14:00" ou "Demain 09:00"
            if slot_time.date() == now.date():
                day_label = "Aujourd'hui"
            elif slot_time.date() == (now + timedelta(days=1)).date():
                day_label = "Demain"
            else:
                day_label = slot_time.strftime("%d/%m")
            
            slot_str = f"{day_label} {slot_time.strftime('%H:%M')}"
            slots.append(slot_str)
        
        return slots

    async def creneau(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enregistre l'heure saisie et envoie la commande."""
        heure_text = update.message.text.strip()
        
        # Valider le format de l'heure
        try:
            # Essayer de parser l'heure
            datetime.strptime(heure_text, '%H:%M')
            context.user_data['order']['creneau'] = heure_text
            
            # Envoyer la commande à l'admin
            await self.send_order_to_admin(context, update)
            
            await update.message.reply_text(
                f"✅ **Commande enregistrée!**\n\n"
                f"Heure de réception prévue: **{heure_text}**\n\n"
                "Un cuisto va vous envoyer un message privé pour confirmer.\n\n"
                "📱 Restez à l'affût de vos notifications!\n\n"
                "Merci pour votre confiance! 🙏",
                parse_mode='Markdown'
            )
            
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "❌ Format d'heure invalide.\n\n"
                "Veuillez utiliser le format HH:MM (exemple: 14:30 ou 18:00) :"
            )
            return CRENEAU

    async def send_order_to_admin(self, context: ContextTypes.DEFAULT_TYPE, query_or_update):
        """Envoie les détails de la commande à l'administrateur."""
        order = context.user_data['order']
        
        # Construire le message pour l'admin
        uber_one_info = order['uber_one']
        
        # Créer un lien cliquable vers le profil de l'utilisateur
        user_id = order['user_id']
        user_link = f"[{order['user_fullname']}](tg://user?id={user_id})"
        
        # Message ultra compact - juste la notification
        compact_message = (
            "🛒 **NOUVELLE COMMANDE**\n\n"
            f"👤 Client: {user_link}"
        )
        
        # Message détaillé complet
        detailed_message = (
            "🛒 **DÉTAILS DE LA COMMANDE**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **Client:** {user_link}\n"
            f"📱 **Username:** {order['username']}\n\n"
            f"🍽️ **Restaurant:** {order['restaurant']}\n"
            f"📍 **Adresse de livraison:**\n{order['adresse']}\n\n"
            f"💰 **Prix sous-total (min 20€ HT):** {order['prix_subtotal']}\n"
            f"💳 **Prix TTC:** {order['prix_ttc']}\n"
            f"💵 **Moyen de paiement:** {order['moyen_paiement']}\n"
            f"🎫 **Uber One :** {uber_one_info}\n\n"
            f"🚚 **Type de livraison:** {order['type_livraison']}\n"
            f"⏰ **Heure de réception:** {order['creneau']}\n\n"
            f"📅 **Date de commande:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        )
        
        # Récapitulatif pour le client
        recap_message = (
            "📋 **RÉCAP POUR LE CLIENT**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🍽️ Restaurant: {order['restaurant']}\n"
            f"📍 Adresse: {order['adresse']}\n"
            f"💰 Sous-total: {order['prix_subtotal']}\n"
            f"💳 TTC: {order['prix_ttc']}\n"
            f"💵 Paiement: {order['moyen_paiement']}\n"
            f"🎫 Uber One: {uber_one_info}\n"
            f"🚚 Livraison: {order['type_livraison']}\n"
            f"⏰ Heure: {order['creneau']}\n\n"
            "✅ Commande confirmée!"
        )
        
        # Envoyer le message à l'admin ET/OU au canal/groupe
        targets = []
        if ADMIN_ID:
            targets.append(('admin', ADMIN_ID, None))  # Pas de topic pour l'admin
        if CHANNEL_ID:
            targets.append(('groupe', CHANNEL_ID, order['user_fullname']))  # Avec nom pour le topic
        
        if targets:
            for target_type, target_id, topic_name in targets:
                try:
                    message_thread_id = None
                    
                    # Si c'est un groupe et qu'on a un nom, créer un topic
                    if target_type == 'groupe' and topic_name:
                        try:
                            # Utiliser le username si disponible, sinon le nom complet
                            username = order.get('username', '').replace('@', '')
                            topic_display_name = username if username and username != f"ID: {user_id}" else topic_name
                            
                            # Créer un nouveau topic pour cette commande avec le statut 'À faire' par défaut
                            topic = await context.bot.create_forum_topic(
                                chat_id=target_id,
                                name=f"📌 {topic_display_name}"  # Marqué comme 'À faire' par défaut
                            )
                            message_thread_id = topic.message_thread_id
                            logger.info(f"Topic créé: {topic.name} (ID: {message_thread_id})")
                            
                            # Stocker les informations du topic pour les boutons
                            context.bot_data[f'thread_{user_id}'] = message_thread_id
                            context.bot_data[f'chat_{user_id}'] = target_id
                            context.bot_data[f'topic_name_{user_id}'] = topic_display_name
                        except Exception as e:
                            logger.warning(f"Impossible de créer un topic (le groupe n'a peut-être pas les topics activés): {e}")
                            # Continuer sans topic si ça échoue
                    
                    # Boutons inline pour voir les détails et gérer le statut
                    keyboard = [
                        [InlineKeyboardButton("📋 Voir détails complets", callback_data=f"details_{user_id}")],
                        [InlineKeyboardButton("📝 Récap pour client", callback_data=f"recap_{user_id}")],
                        [InlineKeyboardButton("✅ Marquer comme fait", callback_data=f"done_{user_id}"),
                         InlineKeyboardButton("📌 À faire", callback_data=f"todo_{user_id}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Envoyer le message compact avec boutons (dans le topic si créé)
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=compact_message,
                        parse_mode='Markdown',
                        reply_markup=reply_markup,
                        message_thread_id=message_thread_id
                    )
                    
                    # Stocker les messages détaillés ET le screenshot pour les callbacks
                    context.bot_data[f'details_{user_id}'] = detailed_message
                    context.bot_data[f'recap_{user_id}'] = recap_message
                    context.bot_data[f'screenshot_{user_id}'] = order.get('screenshot_file_id')
                    context.bot_data[f'thread_{user_id}'] = message_thread_id  # Stocker le thread ID
                    context.bot_data[f'chat_{user_id}'] = target_id  # Stocker le chat ID
                    context.bot_data[f'topic_name_{user_id}'] = topic_display_name if target_type == 'groupe' and topic_name else None  # Stocker le nom du topic
                    
                    logger.info(f"Commande envoyée au {target_type} ({target_id}) pour l'utilisateur {order['username']}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi au {target_type} ({target_id}): {e}")
        else:
            logger.warning("Ni ADMIN_ID ni CHANNEL_ID ne sont configurés! La commande n'a pas été envoyée.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les clics sur les boutons inline."""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        # Récupérer le thread_id si disponible
        message_thread_id = query.message.message_thread_id if hasattr(query.message, 'message_thread_id') else None
        
        # Vérifier si c'est un bouton de détails ou de récap
        if callback_data.startswith('details_'):
            message = context.bot_data.get(callback_data, "❌ Détails non disponibles")
            await query.message.reply_text(message, parse_mode='Markdown')
            
            # Envoyer aussi le screenshot si disponible
            user_id = callback_data.replace('details_', '')
            screenshot_id = context.bot_data.get(f'screenshot_{user_id}')
            if screenshot_id:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=screenshot_id,
                    caption="📸 Screenshot du panier",
                    message_thread_id=message_thread_id
                )
        elif callback_data.startswith('recap_'):
            message = context.bot_data.get(callback_data, "❌ Récapitulatif non disponible")
            await query.message.reply_text(message, parse_mode='Markdown')
        elif callback_data.startswith('done_'):
            # Marquer comme fait
            user_id = callback_data.replace('done_', '')
            thread_id = context.bot_data.get(f'thread_{user_id}')
            chat_id = context.bot_data.get(f'chat_{user_id}')
            topic_name = context.bot_data.get(f'topic_name_{user_id}')
            
            # Modifier le message
            await query.edit_message_text(
                query.message.text + "\n\n✅ **COMMANDE TERMINÉE**",
                parse_mode='Markdown'
            )
            
            # Modifier le nom du topic si disponible
            if thread_id and chat_id and topic_name:
                try:
                    await context.bot.edit_forum_topic(
                        chat_id=chat_id,
                        message_thread_id=thread_id,
                        name=f"✅ {topic_name}"
                    )
                except Exception as e:
                    logger.error(f"Erreur lors de la modification du topic: {e}")
            
            await query.answer("✅ Commande marquée comme terminée!")
            
        elif callback_data.startswith('todo_'):
            # Marquer comme à faire
            user_id = callback_data.replace('todo_', '')
            thread_id = context.bot_data.get(f'thread_{user_id}')
            chat_id = context.bot_data.get(f'chat_{user_id}')
            topic_name = context.bot_data.get(f'topic_name_{user_id}')
            
            # Modifier le message
            await query.edit_message_text(
                query.message.text + "\n\n📌 **À FAIRE**",
                parse_mode='Markdown'
            )
            
            # Modifier le nom du topic si disponible
            if thread_id and chat_id and topic_name:
                try:
                    await context.bot.edit_forum_topic(
                        chat_id=chat_id,
                        message_thread_id=thread_id,
                        name=f"📌 {topic_name}"
                    )
                except Exception as e:
                    logger.error(f"Erreur lors de la modification du topic: {e}")
            
            await query.answer("📌 Commande marquée comme à faire!")

    async def get_channel_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Récupère l'ID du canal/groupe où la commande est envoyée."""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = update.effective_chat.title if hasattr(update.effective_chat, 'title') else 'N/A'
        
        await update.message.reply_text(
            f"📋 **Informations du chat:**\n\n"
            f"🆔 **Chat ID:** `{chat_id}`\n"
            f"📱 **Type:** {chat_type}\n"
            f"📝 **Titre:** {chat_title}\n\n"
            f"💡 **Pour utiliser ce canal:**\n"
            f"Ajoutez cette variable d'environnement:\n"
            f"`CHANNEL_ID={chat_id}`",
            parse_mode='Markdown'
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Annule la conversation."""
        await update.message.reply_text(
            "❌ Commande annulée.\n\n"
            "Tapez /start pour recommencer.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return ConversationHandler.END


def main():
    """Démarre le bot."""
    # Créer l'application avec le token depuis les variables d'environnement
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Créer l'instance du bot
    bot = OrderBot()
    
    # Définir le gestionnaire de conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            RESTAURANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.restaurant)],
            ADRESSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.adresse)],
            PRIX_SUBTOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.prix_subtotal)],
            PRIX_TTC: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.prix_ttc)],
            MOYEN_PAIEMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.moyen_paiement)],
            SCREENSHOT: [MessageHandler(filters.PHOTO, bot.screenshot)],
            LIVRAISON_TYPE: [CallbackQueryHandler(bot.livraison_type)],
            CRENEAU: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.creneau)],
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Ajouter le handler pour les boutons inline (en dehors de la conversation)
    application.add_handler(CallbackQueryHandler(bot.button_callback, pattern='^(details_|recap_)'))
    
    # Ajouter la commande pour obtenir l'ID du canal
    application.add_handler(CommandHandler('get_channel_id', bot.get_channel_id))
    
    logger.info("Bot prêt à démarrer...")
    return application


if __name__ == '__main__':
    import os
    
    # Configuration du logger
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Afficher les variables d'environnement (sans le token pour des raisons de sécurité)
    logger.info("=== Configuration du bot ===")
    logger.info(f"ADMIN_ID: {os.environ.get('ADMIN_ID', 'Non défini')}")
    logger.info(f"CHANNEL_ID: {os.environ.get('CHANNEL_ID', 'Non défini')}")
    logger.info("===========================")
    
    try:
        application = main()
        logger.info("Démarrage du bot en mode polling...")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Erreur au démarrage du bot: {str(e)}")
        raise
