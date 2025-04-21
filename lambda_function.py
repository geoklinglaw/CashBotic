import os, json, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from bot_logic import start_message, oneoff_handler, calendar_conversation, past_handler

TOKEN = os.environ["TOKEN"]

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_message))
app.add_handler(oneoff_handler)
app.add_handler(calendar_conversation)
app.add_handler(past_handler)

_initialised = False
async def ensure_initialised():
    global _initialised
    if not _initialised:
        await app.initialize()
        _initialised = True


async def _run(update):
    await ensure_initialised()
    await app.process_update(update)

def lambda_handler(event, context):
    if event.get("httpMethod") == "GET":
        return {"statusCode": 200, "body": "ok"}   # health‑check

    if event.get("httpMethod") == "POST":
        update = Update.de_json(json.loads(event["body"]), app.bot)
        asyncio.run(_run(update))
        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    return {"statusCode": 405, "body": "Method Not Allowed"}
