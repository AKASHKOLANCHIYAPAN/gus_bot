import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher
from bot_logic import start, handle_text, feedback

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, Filters

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
dispatcher.add_handler(CallbackQueryHandler(feedback))

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "Gus Bot is Live 🚀"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    await bot.set_webhook(webhook_url + WEBHOOK_PATH)
