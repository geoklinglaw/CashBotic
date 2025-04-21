import os, json, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from app.bot_logic import start_message, oneoff_handler, calendar_conversation, past_handler

TOKEN = os.environ["TOKEN"]

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_message))
app.add_handler(oneoff_handler)
app.add_handler(calendar_conversation)
app.add_handler(past_handler)

# Initialize the Application only once
initialised = False
async def ensure_initialised():
    global initialised
    if not initialised:
        await app.initialize()
        initialised = True

async def _run(update):
    await ensure_initialised()
    await app.process_update(update)

def lambda_handler(event, context):
    if event.get("httpMethod") == "GET":
        return {"statusCode": 200, "body": "ok"}

    if event.get("httpMethod") == "POST":
        update = Update.de_json(json.loads(event["body"]), app.bot)

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(_run(update))
        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    return {"statusCode": 405, "body": "Method Not Allowed"}
