import telegram
print("python-telegram-bot version:", telegram.__version__)
import os
import requests
import base64
import logging
from io import BytesIO
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8164728305:AAF8JwZ-OlmPT6ySYUsj7c3UhERF8uQUtLU")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")

INVOKE_URL = "https://ai.api.nvidia.com/v1/genai/nvidia/consistory"
FORCE_SUB_CHANNEL = "@Topdeals_Off"

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# --- Command: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("Subscribe to Top deals and offers 💥💥", url="https://t.me/Topdeals_Off")],
            [InlineKeyboardButton("🔄 Refresh Now", callback_data="refresh_subscribe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🚫 To use this bot, please subscribe to our channel first!",
            reply_markup=reply_markup
        )
        return
    await update.message.reply_text(
        "👋 Welcome to the NVIDIA AI Image Bot!\n"
        "Send me a command like:\n"
        "`/generate a cat wearing sunglasses at the beach`",
        parse_mode="Markdown"
    )

# --- Command: /generate ---
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("Subscribe to Top deals and offers 💥💥", url="https://t.me/Topdeals_Off")],
            [InlineKeyboardButton("🔄 Refresh Now", callback_data="refresh_subscribe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🚫 To use this bot, please subscribe to our channel first!",
            reply_markup=reply_markup
        )
        return
    prompt = " ".join(context.args).strip()

    # Validate prompt
    if not prompt or len(prompt.split()) < 3:
        await update.message.reply_text("⚠️ Please provide a more descriptive prompt (at least 3 words).")
        return

    await update.message.reply_text(f"🧠 Generating image for: *{prompt}*\n⏳ Please wait...", parse_mode="Markdown")

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Create payload with default values if needed
    payload = {
        "mode": "init",
        "subject_prompt": prompt,
        "subject_tokens": prompt.split()[:5],  # Limit tokens to 5 for safety
        "subject_seed": 43,
        "style_prompt": "A photo of",
        "scene_prompt1": "natural light, clean background",
        "scene_prompt2": "realistic, high quality",
        "negative_prompt": "blurry, low quality, distorted, bad anatomy",
        "cfg_scale": 5,
        "same_initial_noise": False
    }

    try:
        response = requests.post(INVOKE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if "artifacts" in data and data["artifacts"]:
            for idx, img_data in enumerate(data["artifacts"]):
                if "base64" in img_data:
                    img_bytes = base64.b64decode(img_data["base64"])
                    img_io = BytesIO(img_bytes)
                    img_io.name = f"generated_{idx+1}.jpg"
                    img_io.seek(0)
                    await update.message.reply_photo(
                        photo=InputFile(img_io),
                        caption=f"🖼️ Image {idx+1} for: {prompt}"
                    )
                else:
                    await update.message.reply_text(f"⚠️ No image data found for image {idx+1}.")
        else:
            await update.message.reply_text("❌ No images were generated. Try changing the prompt.")

    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh.response.status_code} - {errh.response.text}")
        await update.message.reply_text(f"🚫 API error: {errh.response.status_code}")
    except Exception as e:
        logger.exception("Unexpected error occurred")
        await update.message.reply_text(f"🚨 Unexpected error:\n{str(e)}")

# --- Command: /about ---
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ *About this bot*\n"
        "Developer: Rushikesh Narule\n"
        "Powered by NVIDIA AI Image Generation.",
        parse_mode="Markdown"
    )

# --- Callback for Refresh Button ---
async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if await check_subscription(user_id, context.bot):
        await query.edit_message_text(
            "✅ Subscription verified! You can now use the bot. Send /start or /generate."
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Subscribe to Top deals and offers 💥💥", url="https://t.me/Topdeals_Off")],
            [InlineKeyboardButton("🔄 Refresh Now", callback_data="refresh_subscribe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🚫 You are still not subscribed. Please join the channel and then click 'Refresh Now'.",
            reply_markup=reply_markup
        )

# --- Handle Non-Command Messages ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 Please use `/generate your prompt` to create an image.")

# --- Run the Bot ---
def main():
    if "YOUR_TELEGRAM_BOT_TOKEN_HERE" in TELEGRAM_BOT_TOKEN:
        logger.warning("🚨 Set TELEGRAM_BOT_TOKEN in environment variables.")
    if "YOUR_NVIDIA_API_KEY_HERE" in NVIDIA_API_KEY:
        logger.warning("🚨 Set NVIDIA_API_KEY in environment variables.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_image))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(refresh_callback, pattern="refresh_subscribe"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("✅ Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
