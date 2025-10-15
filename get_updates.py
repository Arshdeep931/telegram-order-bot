#!/usr/bin/env python3
"""
Script pour obtenir l'ID du canal via les updates Telegram
"""
import asyncio
import os
from telegram import Bot

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7369442513:AAGqGlMvf_401OH-QsNgjFLEAJAd_AJz1Jg')

async def get_updates():
    """Récupère les dernières updates pour trouver l'ID du canal"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("🔍 Récupération des updates...")
    print("📱 Envoyez un message dans votre canal MAINTENANT\n")
    
    # Attendre 3 secondes
    await asyncio.sleep(3)
    
    updates = await bot.get_updates()
    
    if not updates:
        print("❌ Aucune update trouvée.")
        print("💡 Assurez-vous que:")
        print("   1. Le bot est admin du canal")
        print("   2. Vous avez envoyé un message dans le canal")
        return
    
    print(f"✅ {len(updates)} update(s) trouvée(s)\n")
    
    for update in updates:
        if update.channel_post:
            chat = update.channel_post.chat
            print("="*60)
            print(f"🎯 CANAL TROUVÉ!")
            print(f"📝 Titre: {chat.title}")
            print(f"🆔 ID: {chat.id}")
            print(f"📱 Type: {chat.type}")
            print("="*60)
            print(f"\n💡 Utilisez cet ID comme CHANNEL_ID:")
            print(f"   CHANNEL_ID={chat.id}\n")
            return
    
    print("⚠️ Aucun canal trouvé dans les updates récentes")
    print("💡 Envoyez un nouveau message dans le canal et relancez ce script")

if __name__ == '__main__':
    asyncio.run(get_updates())
