#!/usr/bin/env python3
"""Script pour supprimer les webhooks et réinitialiser le bot"""
import asyncio
import os
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg')

async def reset_webhook():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Supprimer le webhook
    result = await bot.delete_webhook(drop_pending_updates=True)
    print(f"✅ Webhook supprimé: {result}")
    
    # Vérifier qu'il n'y a plus de webhook
    webhook_info = await bot.get_webhook_info()
    print(f"📋 Info webhook: {webhook_info}")
    
    if webhook_info.url:
        print(f"⚠️ Webhook encore actif: {webhook_info.url}")
    else:
        print("✅ Aucun webhook actif - le bot peut utiliser polling")

if __name__ == '__main__':
    asyncio.run(reset_webhook())
