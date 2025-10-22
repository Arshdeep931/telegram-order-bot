#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from aiohttp import web
from datetime import datetime

# --- LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIG ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret123")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN manquant")
if not PUBLIC_URL:
    raise RuntimeError("❌ PUBLIC_URL manquant (ex: https://xxx.onrender.com)")

# --- ÉTATS ---
(RESTAURANT, ADRESSE, PRIX_SUBTOTAL, PRIX_TTC, MOYEN_PAIEMENT,
 SCREENSHOT, LIVRAISON_TYPE, CRENEAU) = range(8)


class OrderBot:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Bonjour ! Indiquez le restaurant et la ville :")
        context.user_data["order"] = {}
        return RESTAURANT

    async def restaurant(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["restaurant"] = update.message.text
        await update.message.reply_text("✅ Restaurant enregistré ! Donnez votre adresse :")
        return ADRESSE

    async def adresse(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["adresse"] = update.message.text
        await update.message.reply_text("Prix HT (minimum 20€) :")
        return PRIX_SUBTOTAL

    async def prix_subtotal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            prix = float(update.message.text.replace("€", "").replace(",", "."))
            if prix < 20:
                await update.message.reply_text("❌ Minimum 20€, recommencez :")
                return PRIX_SUBTOTAL
            context.user_data["order"]["prix_ht"] = prix
            await update.message.reply_text("Entrez le prix TTC :")
            return PRIX_TTC
        except ValueError:
            await update.message.reply_text("❌ Format invalide. Exemple: 25.50")
            return PRIX_SUBTOTAL

    async def prix_ttc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            prix_ttc = float(update.message.text.replace("€", "").replace(",", "."))
            prix_ht = context.user_data["order"]["prix_ht"]
            if prix_ttc < prix_ht:
                await update.message.reply_text("❌ TTC inférieur au HT.")
                return PRIX_TTC
            context.user_data["order"]["prix_ttc"] = prix_ttc
            keyboard = [["🏦 Virement", "📱 PayPal"], ["🍎 Apple Pay"]]
            await update.message.reply_text("Moyen de paiement ?",
                                            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
            return MOYEN_PAIEMENT
        except ValueError:
            await update.message.reply_text("❌ Format invalide. Exemple: 30.00")
            return PRIX_TTC

    async def moyen_paiement(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["order"]["paiement"] = update.message.text
        await update.message.reply_text("Envoyez un screenshot 📸",
                                        reply_markup=ReplyKeyboardRemove())
        return SCREENSHOT

    async def screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message.photo:
            await update.message.reply_text("❌ Envoyez une image.")
            return SCREENSHOT
        await update.message.reply_text("🚀 Commander maintenant ou 📅 Planifier ?",
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🚀 Maintenant", callback_data="now")],
                                            [InlineKeyboardButton("📅 Planifier", callback_data="plan")]
                                        ]))
        return LIVRAISON_TYPE

    async def livraison_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        if query.data == "now":
            await query.edit_message_text("✅ Commande enregistrée, merci 🙏")
            return ConversationHandler.END
        else:
            await query.edit_message_text("Entrez l’heure souhaitée (HH:MM) :")
            return CRENEAU

    async def creneau(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            datetime.strptime(update.message.text.strip(), "%H:%M")
            await update.message.reply_text("✅ Commande planifiée ! Merci 🙏")
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("❌ Mauvais format. Exemple: 14:30")
            return CRENEAU

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Commande annulée ❌")
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
