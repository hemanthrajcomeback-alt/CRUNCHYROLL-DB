# Crunchyroll Telegram Bot

This is a Telegram bot that can download videos from Crunchyroll.

## Setup

This project is designed to be run with Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t crunchyroll-bot .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -it --rm \
        -e TELEGRAM_TOKEN=<your_telegram_token> \
        -e CRUNCHYROLL_COOKIES_FILE=<path_to_your_cookies_file> \
        crunchyroll-bot
    ```

## Usage

1.  Start a chat with your bot on Telegram.
2.  Send the `/start` command.
3.  Send a link to a Crunchyroll series.
4.  The bot will reply with a list of episodes.
5.  Click on the episode you want to download.

## Deployment on Render

This project is configured for deployment on [Render](https://render.com/).

1.  Fork this repository to your GitHub account.
2.  Go to the Render dashboard and create a new **Blueprint Instance**.
3.  Connect your GitHub account and select the forked repository.
4.  Render will automatically detect the `render.yaml` file and configure the service.
5.  In the **Environment** section, add your `TELEGRAM_TOKEN` and `CRUNCHYROLL_COOKIES_FILE` as environment variables.
6.  Click **Create New Blueprint Instance** to deploy the bot.
