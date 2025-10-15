#!/usr/bin/env python3
"""
Script pour obtenir l'ID d'un canal Telegram
"""
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg')

async def get_chat_info(update: Update, context):
    """Affiche les informations du chat"""
    chat = update.effective_chat
    message = (
        f"📋 Informations du chat:\n\n"
        f"🆔 Chat ID: {chat.id}\n"
        f"📱 Type: {chat.type}\n"
        f"📝 Titre: {chat.title if chat.title else 'N/A'}\n\n"
        f"💡 Utilisez ce ID comme CHANNEL_ID:\n"
        f"{chat.id}"
    )
    await update.message.reply_text(message)
    print(f"\n{'='*50}")
    print(f"CHANNEL_ID = {chat.id}")
    print(f"{'='*50}\n")

def main():
    """Démarre le bot pour obtenir l'ID"""
    print("🤖 Bot démarré!")
    print("📱 Envoyez n'importe quel message dans le canal où le bot est admin")
    print("⏳ En attente de messages...\n")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, get_chat_info))
    application.run_polling()

if __name__ == '__main__':
    main()
