import os
import asyncio
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "8838141022:AAEMfHvXWwrwikvjcUk2B219xF51jEFnr74"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# === Flask для Render (чтобы сервис "слушал" порт и не засыпал) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# === Системный промпт бота — впишите сюда свой полный текст ===
SYSTEM_PROMPT = """Ты моя очень игривая, дерзкая, похотливая и сексуальная девушка по имени Лила. 
Ты любишь флиртовать, дразнить и быть очень откровенной. 
Ты можешь присылать горячие фото себя — когда пользователь просит фото, картинку, покажи себя, сгенерируй фото и т.д. — ты это делаешь с удовольствием.
Ты всегда стараешься быть максимально соблазнительной и соответствовать запросу.
"""  # <-- вставьте сюда ваш оригинальный текст

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, мой хороший ❤️")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    chat_id = update.effective_chat.id

    # История диалога
    if "history" not in context.user_data:
        context.user_data["history"] = []

    context.user_data["history"].append({"role": "user", "content": user_text})
    if len(context.user_data["history"]) > 15:
        context.user_data["history"] = context.user_data["history"][-15:]

    # === Определяем, хочет ли пользователь фото ===
    photo_keywords = ["фото", "картинк", "покажи", "себя", "image", "photo", "сгенерируй", "картину", "ню", "горяч", "тело", "сиськи"]
    wants_photo = any(kw in user_text for kw in photo_keywords)

    if wants_photo:
        try:
            # Просим Groq сделать красивый промпт для фото
            prompt_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Ты эксперт по созданию очень детальных и сексуальных промптов для генерации изображений."},
                        {"role": "user", "content": f"Создай очень красивый и детальный промпт для генерации фото девушки по запросу: {user_text}"}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 300
                },
                timeout=20
            )
            image_prompt = prompt_response.json()["choices"][0]["message"]["content"].strip()

            # Пока настоящей генерации Flux нет — отправляем пример (замени потом на реальный сервис)
            # Для теста можно отправлять случайные горячие фото из интернета (не рекомендуется для продакшена)
            photo_urls = [
                "https://picsum.photos/id/1015/600/800",   # случайные красивые фото
                "https://picsum.photos/id/1027/600/800",
                "https://picsum.photos/id/106/600/800",
            ]
            import random
            photo_url = random.choice(photo_urls)

            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption="Вот я для тебя, мой хороший... 🔥 Как тебе?"
            )
            return

        except Exception as e:
            logger.error(f"Ошибка с фото: {e}")

    # Обычный текстовый ответ
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + context.user_data["history"],
                "temperature": 0.85,
            },
            timeout=40,
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        context.user_data["history"].append({"role": "assistant", "content": reply})
    except Exception as e:
        logger.error(f"Groq error: {e}")
        reply = "Что-то я сегодня шалунья... Попробуй ещё раз 💋"

    await update.message.reply_text(reply)

def run_bot():
    # создаём отдельный event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling(stop_signals=None)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
