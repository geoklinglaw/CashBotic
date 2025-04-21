import os
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

from bot_logic import start_message, oneoff_handler, calendar_conversation, past_handler
from dotenv import load_dotenv

# Load .env locally
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
PORT        = int(os.getenv("PORT", 8080))
TOKEN       = os.environ["TOKEN"]
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # set only in Fly.io

# Build your bot
app_telegram = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)
app_telegram.add_handler(CommandHandler("start", start_message))
app_telegram.add_handler(oneoff_handler)
app_telegram.add_handler(calendar_conversation)
app_telegram.add_handler(past_handler)

# Webhook handler
async def handle(request):
    data   = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return web.Response()

# Healthcheck
async def healthcheck(_):
    return web.Response(text="CashBotic is alive!")

def run():
    web_app = web.Application()
    web_app.router.add_post("/webhook", handle)
    web_app.router.add_get("/", healthcheck)

    if WEBHOOK_URL:
        logger.info(f"▶️ Webhook mode on {PORT}")
        app_telegram.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            web_app=web_app,
            drop_pending_updates=True,
        )
    else:
        logger.info("▶️ Polling mode (local)")
        app_telegram.run_polling()

if __name__ == "__main__":
    run()
