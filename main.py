import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

TELEGRAM_TOKEN = "8672402090:AAGZnLthbPa2-_xblrkHu9tCQRg0YoOZuwE"
GROQ_API_KEY = "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"

# === Flask для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# === Твой бот ===
SYSTEM_PROMPT = """Ты моя очень игривая, дерзкая и похотливая девушка..."""  # оставь как было

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, мой хороший ❤️")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (оставь тот же код, что был)
    pass  # замени на свой предыдущий код handle_message

def run_bot():
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()

# Запуск
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
