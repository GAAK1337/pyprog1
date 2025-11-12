import telebot
from config import API_KEY

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands = ['start'])

def start(message):
    bot.send_message(message.chat.id, text = "Hello world")

@bot.message_handler(commands = ['help'])

def help(message):
    bot.send_message(message.chat.id, text = "\n start - запуск бота. \n help - выводит список команд и их функции. \n about - выдает информацию о боте")

@bot.message_handler(commands = ['about'])

def about(message):
    bot.send_message(message.chat.id, text = "Этот бот создан для группы 8341")

bot.polling()



