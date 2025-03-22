import asyncio
import json
import os
import traceback

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, InlineQueryHandler
from telegram.constants import ParseMode
from constants import START_TEXT, INSTRUCTIONS_TEXT, RICKROLL_TEXT
from dice_roller import roll_query


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(START_TEXT, parse_mode=ParseMode.MARKDOWN)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(INSTRUCTIONS_TEXT, parse_mode=ParseMode.MARKDOWN)


async def rickroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RICKROLL_TEXT, parse_mode=ParseMode.MARKDOWN)


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args is None and update.message.text is not None:
        dice_formula = update.message.text
    else:
        dice_formula = "".join(context.args)
    await update.message.reply_text(
        roll_query(dice_formula),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def app_process_update(app, event):
    async with app:
        data = json.loads(event["body"])
        update = Update.de_json(data=data, bot=app.bot)
        await app.process_update(update)


def create_app():
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token is None:
        raise Exception("No bot token found")
    app = Application.builder().token(bot_token).build()
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", instructions))
    app.add_handler(CommandHandler("rickroll", rickroll))
    app.add_handler(CommandHandler("roll", roll, has_args=True))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, roll))
    app.add_handler(InlineQueryHandler(roll))
    return app


APPLICATION = create_app()


def lambda_handler(event, context):
    try:
        asyncio.run(app_process_update(APPLICATION, event))
        return {"statusCode": 200, "body": json.dumps("Webhook request received")}
    except Exception as e:
        traceback.print_exc()
        print(e)
        return {"statusCode": 500, "body": json.dumps("Problems with the webhook request")}
