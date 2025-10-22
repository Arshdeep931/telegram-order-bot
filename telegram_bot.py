#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ÉTATS ---
(
    RESTAURANT,
    ADRESSE,
    PRIX_SUBTOTAL,
    PRIX_TTC,
    MOYEN_PAIEMENT,
    SCREENSHOT,
    LIVRAISON_TYPE,
    CRENEAU,
    PRIX_CORRIGE
) = range(9)

# --- CONFIG ---
ADMIN_ID = int(os.getenv("ADMIN_ID", "1692775134"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

if not TELEGRAM_BOT_TOKEN or ":" not in TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN invalide ou manquant")
    raise SystemExit(1)

PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
if not PUBLIC_URL:
    logger.error("❌ PUBLIC_URL manquant (ex: https://xxx.onrender.com)")
    raise SystemExit(1)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret123")


# --- BOT ---
class OrderBot:
    def __init__(self):
        self.orders = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        await update.message.reply_text(
            f"Bonjour {user.first_name}! 👋\n\n"
            "Veuillez indiquer le **nom du restaurant et la ville** :",
            parse_mode="Markdown"
        )
        context.user_data["order"] = {"user_id": user.id}
        return RESTAURANT

    async def restaurant(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["restaurant"] = update.message.text
        await update.message.reply_text("✅ Restaurant enregistré!\n\nEntrez votre **adresse complète** :",
                                        parse_mode="Markdown")
        return ADRESSE

    async def adresse(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["adresse"] = update.message.text
        await update.message.reply_text("✅ Adresse enregistrée!\n\nPrix **sous-total (HT)** :")
        return PRIX_SUBTOTAL

    async def prix_subtotal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            prix = float(update.message.text.replace("€", "").replace(",", "."))
            if prix < 20:
                await update.message.reply_text("❌ Minimum 20€ HT, réessayez :")
                return PRIX_SUBTOTAL
            context.user_data["order"]["prix_subtotal"] = prix
            await update.message.reply_text("✅ Prix HT enregistré!\n\nEntrez le **prix TTC** :")
            return PRIX_TTC
        except ValueError:
            await update.message.reply_text("❌ Format invalide, ex: 25.50")
            return PRIX_SUBTOTAL

    async def prix_ttc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            prix_ttc = float(update.message.text.replace("€", "").replace(",", "."))
            prix_ht = context.user_data["order"]["prix_subtotal"]
            if prix_ttc < prix_ht:
                await update.message.reply_text("❌ Le TTC ne peut pas être inférieur au HT.")
                return PRIX_TTC
            context.user_data["order"]["prix_ttc"] = prix_ttc
            keyboard = [["🏦 Virement", "📱 PayPal"], ["🍎 Apple Pay"]]
            await update.message.reply_text("✅ TTC enregistré!\n\nMoyen de paiement ?",
                                            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
            return MOYEN_PAIEMENT
        except ValueError:
            await update.message.reply_text("❌ Format invalide, ex: 30.00")
            return PRIX_TTC

    async def moyen_paiement(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["moyen_paiement"] = update.message.text
        await update.message.reply_text("✅ Paiement enregistré!\n\nEnvoyez un **screenshot** du panier 📸",
                                        reply_markup=ReplyKeyboardRemove())
        return SCREENSHOT

    async def screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.photo:
            await update.message.reply_text("❌ Envoyez une **image**.")
            return SCREENSHOT
        await update.message.reply_text("✅ Screenshot reçu!\n\n🚀 Commander maintenant ou 📅 Planifier ?",
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🚀 Maintenant", callback_data="now")],
                                            [InlineKeyboardButton("📅 Planifier", callback_data="plan")]
                                        ]))
        return LIVRAISON_TYPE

    async def livraison_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        if query.data == "now":
            await query.edit_message_text("✅ Commande enregistrée, un cuisto vous contacte 🔔")
            return ConversationHandler.END
        else:
            await query.edit_message_text("📅 Entrez l’heure souhaitée (HH:MM) :")
            return CRENEAU

    async def creneau(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            datetime.strptime(update.message.text.strip(), "%H:%M")
            await update.message.reply_text("✅ Commande planifiée, merci 🙏")
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("❌ Format invalide, ex: 14:30")
            return CRENEAU

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("❌ Commande annulée. Tapez /start pour recommencer.")
        return ConversationHandler.END


# --- APPLICATION ---
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot = OrderBot()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", bot.start)],
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
    fallbacks=[CommandHandler("cancel", bot.cancel)],
)
application.add_handler(conv_handler)

# --- Health Check ---
async def health(_):
    return web.Response(text="ok")

application.web_app.add_routes([web.get("/", health)])

# --- Run webhook ---
if __name__ == "__main__":
    logger.info("🚀 Bot démarré (Render webhook)")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path=TELEGRAM_BOT_TOKEN,
        secret_token=WEBHOOK_SECRET,
        webhook_url=f"{PUBLIC_URL}/{TELEGRAM_BOT_TOKEN}",
    )
