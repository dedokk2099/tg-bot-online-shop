import telebot
from telebot import types
#from database import *

bot = telebot.TeleBot('7344618019:AAEcLhHpsggJaSsVxfg9watitiIg08CR3zM')
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('IT', 'ENG')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Hello, i reveive /start')
    print(message.chat.id)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'it':
        bot.send_message(message.chat.id, 'Your language is IT')
        print('Да')
    elif message.text.lower() == 'eng':
        bot.send_message(message.chat.id, 'Your language is ENG')
        print('нет')

bot.polling(none_stop = True)