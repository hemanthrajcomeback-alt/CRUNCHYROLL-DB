# Crunchyroll Telegram Bot

This is a Telegram bot that can download videos from Crunchyroll.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/crunchyroll-telegram-bot.git
    cd crunchyroll-telegram-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r crunchyroll_bot/requirements.txt
    ```

3.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

4.  **Configure the bot:**
    -   Rename `.env.example` to `.env`.
    -   Open `.env` and add your Telegram bot token.
    -   (Optional) If you have a Crunchyroll premium account, you can add the path to your cookies file to enable downloading premium content.

## Running the Bot

To start the bot, run the following command:
```bash
python crunchyroll_bot/bot.py
```

## Usage

1.  Start a chat with your bot on Telegram.
2.  Send the `/start` command.
3.  Send a link to a Crunchyroll series.
4.  The bot will reply with a list of episodes.
5.  Click on the episode you want to download.
