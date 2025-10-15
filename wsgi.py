import asyncio
from telegram_bot import main
from telegram.ext import Application

def create_app():
    # Créer et retourner l'application
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(main())

# Variable d'application requise par Gunicorn
app = create_app()

if __name__ == "__main__":
    # Pour le développement local uniquement
    app.run_polling()
