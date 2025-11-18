import os
import asyncio
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from utils import get_episodes
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
EPISODES_PER_PAGE = 10

# ---------------- Helper Function to Display Episode Pages ----------------
async def display_episodes_page(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int = None):
    """
    Helper function to display a paginated list of episodes.
    Edits the message if message_id is provided, otherwise sends a new one.
    """
    episodes = context.user_data.get('episodes', [])
    page = context.user_data.get('page', 0)

    start_index = page * EPISODES_PER_PAGE
    end_index = start_index + EPISODES_PER_PAGE
    page_episodes = episodes[start_index:end_index]

    keyboard = [
        [InlineKeyboardButton(f"{title}", callback_data=f"ep|{ep_url}")]
        for title, ep_url in page_episodes
    ]

    # --- Pagination Buttons ---
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="page|prev"))
    if end_index < len(episodes):
        navigation_buttons.append(InlineKeyboardButton("Next ➡️", callback_data="page|next"))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    total_pages = -(-len(episodes) // EPISODES_PER_PAGE) # Ceiling division
    text = f"Select an episode (Page {page + 1}/{total_pages}):"

    if message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )

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

        context.user_data['episodes'] = episodes
        context.user_data['page'] = 0

        await display_episodes_page(context, chat_id=update.message.chat_id)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ---------------- Callback Handler ----------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("ep|"):
        ep_url = data.split("|")[1]
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
        filename = f"episode_{quality}.mp4"

        process = await asyncio.create_subprocess_exec(
            "streamlink", ep_url, quality, "-o", filename,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode() if stderr else "Unknown error."
            await query.edit_message_text(f"❌ Download failed.\n`{error_message}`")
            return

        await query.edit_message_text(f"✅ Uploading {quality} to Telegram...")
        try:
            with open(filename, "rb") as video:
                await context.bot.send_video(chat_id=query.message.chat_id, video=video, timeout=120)
            await query.edit_message_text("✅ Upload complete!")
        except Exception as e:
            await query.edit_message_text(f"❌ Upload failed: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    elif data.startswith("page|"):
        action = data.split("|")[1]
        page = context.user_data.get('page', 0)

        if action == "next":
            context.user_data['page'] = page + 1
        elif action == "prev":
            context.user_data['page'] = max(0, page - 1)

        await display_episodes_page(context, chat_id=query.message.chat_id, message_id=query.message.message_id)

# ---------------- Main ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("series", series))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()