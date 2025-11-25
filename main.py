import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

def start(update, context):
    update.message.reply_text("Hello! Crunchyroll Downloader Bot is running via webhook.")

def build_application():
    token = os.getenv("TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    # Add other command/message handlers here

    return application

if __name__ == "__main__":
    # For local testing (polling)
    application = build_application()
    application.run_polling()
