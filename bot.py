import logging
import os
from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import telegramcalendar

from spreadsheet import write
from expenditure import Expenditure
from utils import find_date, chunk_list, KEYBOARD_CATEGORIES, format_calendar_date, import_token

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# State constants
WAITING_FOR_EXPENSE_INPUT = 0
WAITING_FOR_CATEGORY_CHOICE = 1
SELECTING_DATE = 2

### COMMAND HANDLERS ####

async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {update.effective_user.first_name}! Welcome to your expenditure tracker."
    )

async def prompt_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Entered prompt_product_price()")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Please send the expense in the format: Product-Price"
    )
    return WAITING_FOR_EXPENSE_INPUT

async def store_date_and_prompt_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected_date = query.data 
    formatted_date = format_calendar_date(selected_date)
    context.user_data['selected_date'] = formatted_date

    await query.edit_message_text(f"Date selected: {formatted_date}")

    return await prompt_product_price(update, context)


async def past_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Please send the expense in the format: Intended Date(dd/mm/yy)-Product-Price"
    )

def parse_product_price(user_input: str) -> Expenditure:
    """
    Parses user input in 'Product-Price' format and creates an Expenditure object.

    Args:
        user_input (str): User input string.

    Returns:
        Expenditure: A validated expenditure object.

    Raises:
        ValueError: If the input format is invalid or price is not a number.
    """
    product, price = user_input.split('-')
    price = float(price)
    date = find_date().strftime("%x")
    return Expenditure(product, price, date)


async def validate_and_prompt_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save expenditure and product
    Prompt categories keyboard

    Args:
        update (Update)
        context (ContextTypes)

    Returns:
        int: state ('WAITING_FOR_CATEGORY_CHOICE') that represents that categories have been chosen
    """
    logging.info("Entered WAITING_FOR_EXPENSE_INPUT state")
    user_input = update.message.text
    try:
        expenditure = parse_product_price(user_input)
        context.user_data["expenditure"] = expenditure

        keyboard = [[InlineKeyboardButton(cat, callback_data=cat) for cat in row] for row in chunk_list(KEYBOARD_CATEGORIES, 3)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose a category:", reply_markup=reply_markup)
        return WAITING_FOR_CATEGORY_CHOICE
    
    except ValueError as e:
        logging.exception("ValueError occurred while processing user input.")
        await update.message.reply_text(
            "Incorrect format. Please use 'Product-Price' format (e.g., 'Coffee-3.50')."
        )
        return WAITING_FOR_EXPENSE_INPUT
    
async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    expenditure = context.user_data.get("expenditure")
    if not expenditure:
        await query.edit_message_text("An error occurred. Please start again.")
        return ConversationHandler.END
    expenditure.category = category
    logging.info(f"Expenditure updated with category: {category}")
    await query.edit_message_text(f"Category '{category}' chosen.")
    await write_to_spreadsheet(expenditure, update, context)

async def write_to_spreadsheet(expenditure: Expenditure, update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Save expense triggered via message.")
    expenditure = context.user_data.get("expenditure")
    if not expenditure:
        await update.message.reply_text("An error occurred. Please start again.")
        return ConversationHandler.END
    try:
        result = await write(expenditure)
        logging.info(f"Write result: {result}")
        
        if result:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Successfully saved: {expenditure}",
                parse_mode='MarkdownV2'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Failed to save the expense (no result returned)."
            )
    except Exception as e:
        logging.exception("Exception while writing to spreadsheet:")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ An error occurred while saving to the spreadsheet. Please try again later."
        )

    return ConversationHandler.END

# Calendar handler to display the calendar
async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Please select a date:",
        reply_markup=telegramcalendar.create_calendar()
    )
    return SELECTING_DATE

# Inline handler to process calendar interactions
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query
    
    selected, date = telegramcalendar.process_calendar_selection(None, update)
    if selected:
        await query.edit_message_text(
            text=f"You selected {date.strftime('%d/%m/%Y')}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    return SELECTING_DATE
        
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END


if __name__ == '__main__':
    TOKEN = import_token()
    logging.info(f"got the token in main! {TOKEN}")
    application = ApplicationBuilder().token(TOKEN).build()

    oneoff_handler = ConversationHandler(
        entry_points=[CommandHandler('oneoff', prompt_product_price)],
        states={
            WAITING_FOR_EXPENSE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_and_prompt_category)],
            WAITING_FOR_CATEGORY_CHOICE: [CallbackQueryHandler(save_expense)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    calendar_conversation = ConversationHandler(
        entry_points=[CommandHandler('calendar', calendar_handler)],
        states={
            SELECTING_DATE: [CallbackQueryHandler(inline_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    past_handler = ConversationHandler(
        entry_points=[CommandHandler('past', calendar_handler)],
        states={
            SELECTING_DATE: [CallbackQueryHandler(store_date_and_prompt_price)],
            WAITING_FOR_EXPENSE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, validate_and_prompt_category)],
            WAITING_FOR_CATEGORY_CHOICE: [CallbackQueryHandler(save_expense)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    start_handler = CommandHandler('start', start_message)
    # past_handler = CommandHandler('past', past_command)
    application.add_handler(calendar_conversation)


    application.add_handler(start_handler)
    application.add_handler(oneoff_handler)
    application.add_handler(past_handler)
    application.run_polling()
