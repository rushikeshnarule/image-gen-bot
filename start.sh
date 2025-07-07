#!/bin/bash
rm -rf /workspace/.heroku/python/lib/python3.13/site-packages/telegram*

# Uninstall any old version
pip uninstall -y python-telegram-bot

# Install dependencies
pip install -r requirements.txt

# Start the Telegram bot
python bot.py
