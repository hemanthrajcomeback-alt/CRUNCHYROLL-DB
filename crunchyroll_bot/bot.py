import os
import asyncio
import subprocess
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from utils import get_episodes
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ---------------- Start Command ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Welcome! Use /series <Crunchyroll_Series_URL> to list episodes."
    )

# ---------------- Series Command ----------------
async def series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Provide the series URL: /series <URL>")
        return

    url = context.args[0]
    await update.message.reply_text("🔍 Fetching episodes...")

    try:
        episodes = await get_episodes(url)
        if not episodes:
            await update.message.reply_text("❌ No episodes found or URL is invalid.")
            return

        # Display first 10 episodes
        keyboard = [
            [InlineKeyboardButton(f"{title}", callback_data=f"ep|{ep_url}")]
            for title, ep_url in episodes[:10]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select an episode:", reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------------- Callback for Episode Selection ----------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("ep|"):
        ep_url = data.split("|")[1]
        # Ask for quality
        keyboard = [
            [InlineKeyboardButton("480p", callback_data=f"dl|{ep_url}|480p")],
            [InlineKeyboardButton("720p", callback_data=f"dl|{ep_url}|720p")],
            [InlineKeyboardButton("1080p", callback_data=f"dl|{ep_url}|1080p")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select quality:", reply_markup=reply_markup)

    elif data.startswith("dl|"):
        _, ep_url, quality = data.split("|")
        await query.edit_message_text(f"⏳ Downloading {quality}...")
        filename = f"episode_{uuid.uuid4()}_{quality}.mp4"

        # Async download
        process = await asyncio.create_subprocess_exec(
            "streamlink", ep_url, quality, "-o", filename,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            await query.edit_message_text("❌ Download failed.")
            return

        # Check file size
        file_size = os.path.getsize(filename)
        if file_size > 50 * 1024 * 1024:  # 50 MB
            await query.edit_message_text("❌ File is too large to upload to Telegram.")
            os.remove(filename)
            return

        await query.edit_message_text(f"✅ Uploading {quality} to Telegram...")
        with open(filename, "rb") as video:
            await context.bot.send_video(chat_id=query.message.chat_id, video=video)

        os.remove(filename)

# ---------------- Main ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("series", series))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()
