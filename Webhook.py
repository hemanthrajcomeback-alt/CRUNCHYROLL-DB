import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
from main import build_application  # function that returns Application

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
PORT = int(os.getenv("PORT", 10000))
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

app = Flask(__name__)
application: Application = build_application()

@app.post(WEBHOOK_PATH)
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.process_update(update)
    return "OK", 200

@app.get("/")
def home():
    return "Crunchyroll Downloader Bot Webhook Running", 200

@app.get("/setwebhook")
def set_webhook():
    url = f"https://{HOSTNAME}/webhook/{TOKEN}"
    application.bot.set_webhook(url)
    return f"Webhook set to {url}", 200

if __name__ == "__main__":
    # Run Flask server
    app.run(host="0.0.0.0", port=PORT)
