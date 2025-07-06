#!/bin/bash

# Uninstall any old version
pip uninstall -y python-telegram-bot

# Install dependencies
pip install -r requirements.txt

# Start the Telegram bot
python bot.py
