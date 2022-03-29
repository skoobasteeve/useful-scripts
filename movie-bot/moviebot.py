#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
from telegram import Update
import os

token = os.environ.get("TG_BOT_TOKEN")

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


updater.start_polling()

