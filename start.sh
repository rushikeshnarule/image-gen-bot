#!/bin/bash

# Remove any old telegram package to avoid version conflicts
rm -rf /workspace/.heroku/python/lib/python3.13/site-packages/telegram*

# Install the correct version
pip install --force-reinstall python-telegram-bot==20.7

# Install all other dependencies
pip install -r requirements.txt

# Start the Telegram bot
python bot.py 