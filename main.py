import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from lambda_function import (
    start_message,
    oneoff_handler,
    calendar_conversation,
    past_handler,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def run_bot_locally():
    load_dotenv()

    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("Missing TELEGRAM TOKEN in .env")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start_message))
    app.add_handler(oneoff_handler)
    app.add_handler(calendar_conversation)
    app.add_handler(past_handler)

    print("🤖 Running bot locally in polling mode…")
    app.run_polling()

if __name__ == "__main__":
    run_bot_locally()
