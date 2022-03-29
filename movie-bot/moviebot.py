#!/usr/bin/python3

from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import logging
from telegram import Update
import os
from datetime import datetime
import movie_check

tmdb_api_token = os.environ.get("TMDB_API_TOKEN")
sa_api_token = os.environ.get("SA_API_TOKEN")

tmdb_url = "https://api.themoviedb.org/3"
tmdb_headers = {
    'Authorization': f'Bearer {tmdb_api_token}',
    'Content-Type': 'application/json;charset=utf-8',
    'Accept': 'application/json;charset=utf-8'
}

sa_url = "https://streaming-availability.p.rapidapi.com/get/basic"
sa_headers = {
    'x-rapidapi-host': "streaming-availability.p.rapidapi.com",
    'x-rapidapi-key': sa_api_token
    }

bot_token = os.environ.get("TG_BOT_TOKEN")

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# def start(update: Update, context: CallbackContext):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


# def echo(update: Update, context: CallbackContext):
#     context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def movie_lookup(movie):
    logger.info('movie check started')
    movie_id, movie_title, movie_year, movie_rating = movie_check.tmdb_lookup(tmdb_url, tmdb_headers, movie)
    sa_response, services = movie_check.sa_lookup(sa_url, sa_headers, movie_id)
    tg_reply = f"{movie_title} ({movie_year})\nhttps://themoviedb.org/movie/{movie_id}\nRating: {movie_rating}"

    if not services:
        tg_reply = tg_reply + "\n\nStreaming not available :("
    else:
        for s in services:
            leaving_epoch = sa_response["streamingInfo"][s]["us"]["leaving"]
            leaving_date = datetime.fromtimestamp(
                int(leaving_epoch)).strftime('%Y-%m-%d')
            link = sa_response["streamingInfo"][s]["us"]["link"]

            s_pretty = movie_check.services_speller(s)
            tg_reply = tg_reply + f"\n\nAvailable on {s_pretty}"

            if leaving_epoch != 0:
                tg_reply = tg_reply + f"Will be leaving on {leaving_date}"
            
            tg_reply = tg_reply + f"\nWatch here: {link}"
    return tg_reply


# def input_movie(update: Update, context: CallbackContext):
#     movie = ' '.join(context.args)
#     # logger.info(movie)
#     # movie_info = movie_lookup(movie)
#     context.bot.send_message(chat_id=update.effective_chat.id, text=movie)

def echo(update: Update, context: CallbackContext):
    movie = update.message.text
    movie_info = movie_lookup(movie)
    context.bot.send_message(chat_id=update.effective_chat.id, text=movie_info)

def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


# start_handler = CommandHandler('start', start)
# dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

# movie_handler = CommandHandler('input_movie', input_movie)
# dispatcher.add_handler(movie_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)


updater.start_polling()
