import os
from dotenv import load_dotenv
import telebot

load_dotenv()
bot = telebot.TeleBot(
    os.getenv('TELEGRAM_TOKEN'), parse_mode="MarkdownV2")

@ bot.message_handler(commands=['start'])
def sendChatID(message):
    print(f"Chat ID: {message.chat.id}")
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

bot.infinity_polling()