# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r crunchyroll_bot/requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Set the command to run the bot
CMD ["python", "main.py"]
