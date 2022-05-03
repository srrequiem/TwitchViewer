import os
from dotenv import load_dotenv
import telebot

# Custom
from db import DB
from ptypes import DaySchedule
from collector import TwitchPointCollector


class IsOwner(telebot.custom_filters.SimpleCustomFilter):
    key = 'isOwner'

    @staticmethod
    def check(message: telebot.types.Message):
        return message.chat.id == int(os.getenv('TELEGRAM_CHAT_ID'))


class FAMessageSender:
    def __init__(self, bot):
        self._botRef = bot
        self._chatID = int(os.getenv('TELEGRAM_CHAT_ID'))

    def notify(self):
        self._botRef.send_message(
            self._chatID, "Por favor, envía el código 2FA")


load_dotenv()
bot = telebot.TeleBot(
    os.getenv('TELEGRAM_TOKEN'), parse_mode="MarkdownV2")
bot.add_custom_filter(IsOwner())
db = DB()
pointCollector = TwitchPointCollector(
    os.getenv('USER'), os.getenv('PASSWORD'), os.getenv('STREAMER'), db, FAMessageSender(bot), faEnabled=os.getenv('FA_ENABLE'))
commandsCollection = [
    {'section': 'general', 'commands': [
        {'title': '/start \| /help',
            'desc': 'Envía listado de comandos disponibles\.'},
        {'title': '/launch', 'desc': 'Ejecuta acción de visualización sin considerar agenda\.'}]},
    {'section': 'schedule', 'commands': [
        {'title': '/getschedule', 'desc': 'Envía configuración actual de agenda\.'},
        {'title': '/setdayschedule',
            'desc': 'Cambia configuración de un día en específico, ejemplo: ``` /setdayschedule Monday 15:00\-15:30\.```'},
        {'title': '/setschedule', 'desc': 'Cambia configuración de múltiples días, ejemplo: ``` /setschedule Monday\=15:00\-15:30,Tuesday\=15:00\-15:30\.\.\.```'}]}]


def getScheduleAsMessage(response=''):
    for record in db.getSchedule():
        dayName = record.get("name")
        startAtMin = record.get("startAt") % 60
        startAt = f'{str(int(record.get("startAt") / 60))}:{str(startAtMin) if startAtMin > 9 else "0" + str(startAtMin)}'
        endAtMin = record.get("endAt") % 60
        endAt = f'{str(int(record.get("endAt") / 60))}:{str(endAtMin) if endAtMin > 9 else "0" + str(endAtMin)}'
        response += f'{dayName}: {startAt}\-{endAt}\n'
    return response


@ bot.message_handler(commands=['start', 'help'], isOwner=True)
def sendWelcome(message):
    resMsg = ''
    for collection in commandsCollection:
        resMsg += f"\n**{collection['section'].capitalize()}**\n\n"
        for command in collection['commands']:
            resMsg += f"{command['title']}: {command['desc']}\n"
    bot.reply_to(message, resMsg)


@ bot.message_handler(regexp="^\d{6}$")
def receive2faCode(message):
    pointCollector.set2faCode(message.text)


@ bot.message_handler(commands=['getschedule'], isOwner=True)
def getSchedule(message):
    bot.reply_to(message, getScheduleAsMessage())


@ bot.message_handler(commands=['setdayschedule'], isOwner=True)
def setDaySchedule(message):
    try:
        params = message.text.split(" ")
        db.updateDaySchedule(DaySchedule(params[1], params[2]))
        response = getScheduleAsMessage(
            '*Schedule has been updated successfully\!*\n')
    # Validar si el tipo de exepción es debido a que el start time es mayor al end time.
    # En caso contrario sólo mostrar error genérico
    except Exception as e:
        print(e)
        response = "Something went wrong\! *Usage: `/setdayschedule Monday 15:00-15:30`*"
    finally:
        bot.reply_to(message, response)


@ bot.message_handler(commands=['setschedule'], isOwner=True)
def setSchedule(message):
    try:
        params = message.text.split(" ")
        dataset = params[1].split(",")
        for dayDataset in dataset:
            dayConfig = dayDataset.split("=")
            db.updateDaySchedule(DaySchedule(dayConfig[0], dayConfig[1]))
        response = getScheduleAsMessage(
            '*Schedule has been updated successfully\!*\n')
    # Validar si el tipo de exepción es debido a que el start time es mayor al end time.
    # En caso contrario sólo mostrar error genérico
    except Exception as e:
        print(e)
        response = "Something went wrong\! *Usage: `/setschedule Monday=15:00-15:30,Tuesday=15:00-15:30...`*"
    finally:
        bot.reply_to(message, response)


bot.infinity_polling()