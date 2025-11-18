
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    CRUNCHYROLL_COOKIES_FILE = os.getenv('CRUNCHYROLL_COOKIES_FILE')

settings = Settings()
