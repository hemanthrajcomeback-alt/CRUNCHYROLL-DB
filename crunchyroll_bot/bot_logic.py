
import os
import logging
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from .utils import fetch_episodes
from .config import settings
import streamlink
import subprocess

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """
    Removes invalid characters from a filename.
    """
    return re.sub(r'[\\/*?:"<>|]',"", filename)

# Helper function to create paginated episode list
def build_episode_keyboard(episodes, page=0):
    keyboard = []
    page_size = 10
    start_index = page * page_size
    end_index = start_index + page_size

    for i, (title, link) in enumerate(episodes[start_index:end_index]):
        keyboard.append([InlineKeyboardButton(title, callback_data=f'download_{link}|{title}')])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f'page_{page-1}'))
    if end_index < len(episodes):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f'page_{page+1}'))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! Send me a Crunchyroll series URL to get started.')

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not "crunchyroll.com" in url:
        await update.message.reply_text('Please send a valid Crunchyroll series URL.')
        return

    await update.message.reply_text('Fetching episodes, please wait...')

    try:
        episodes = await fetch_episodes(url)
        if not episodes:
            await update.message.reply_text('Could not find any episodes for this series.')
            return

        context.user_data['episodes'] = episodes
        context.user_data['page'] = 0

        reply_markup = build_episode_keyboard(episodes)
        await update.message.reply_text('Please select an episode to download:', reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error fetching episodes: {e}")
        await update.message.reply_text('An error occurred while fetching episodes. Please try again later.')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith('page_'):
        page = int(data.split('_')[1])
        context.user_data['page'] = page
        episodes = context.user_data.get('episodes', [])

        if episodes:
            reply_markup = build_episode_keyboard(episodes, page)
            await query.edit_message_text('Please select an episode to download:', reply_markup=reply_markup)

    elif data.startswith('download_'):
        parts = data.replace('download_', '').split('|')
        episode_url = parts[0]
        title = sanitize_filename(parts[1]) if len(parts) > 1 else episode_url.split('/')[-1]

        await query.edit_message_text('Starting download, this may take a while...')

        try:
            filename = f"{title}.mp4"

            # Run streamlink in a subprocess
            command = ['streamlink', episode_url, 'best', '-o', filename]
            if settings.CRUNCHYROLL_COOKIES_FILE:
                command.extend(['--crunchyroll-cookies', settings.CRUNCHYROLL_COOKIES_FILE])

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Streamlink error: {stderr.decode()}")
                await query.edit_message_text('An error occurred during download.')
                return

            # Check file size before uploading
            file_size = os.path.getsize(filename)
            if file_size > 49 * 1024 * 1024: # 49MB
                await query.edit_message_text('The episode is too large to send via Telegram.')
                os.remove(filename)
                return

            # Send the video
            await context.bot.send_video(chat_id=query.message.chat_id, video=open(filename, 'rb'), supports_streaming=True)

            # Clean up
            os.remove(filename)
            await query.edit_message_text('Download complete!')

        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            await query.edit_message_text('An error occurred while downloading the video.')


def main():
    if not settings.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set!")
        return

    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()
