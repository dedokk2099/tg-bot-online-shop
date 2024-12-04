from role_switcher import *
import telebot
from telebot import types
from dotenv import load_dotenv
#import os
# import admin_interface
# import user_interface
#from database import *

#load_dotenv()
#Token = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot('7344618019:AAEcLhHpsggJaSsVxfg9watitiIg08CR3zM')
role_switcher = RoleSwitcher(bot)

# admin_interface_ = admin_interface.AdminInterface(bot)
# user_interface_ = user_interface.UserInterface(bot)

@bot.message_handler(commands=['start'])
def handle_start(message):
    if role_switcher.user.is_new(message.chat.id):
        role_switcher.user.add_new(message.chat.id)
    bot.send_message(message.chat.id, 'Получена команда /start')
    print(message.chat.id)

# @bot.message_handler(commands=['admin'])
# def handle_admin(message):
#     # Сбрасываем состояние пользователя
#     chat_id = message.chat.id
#     if chat_id in admin_interface_.user_states:
#         admin_interface_.user_states[chat_id] = {}
#     # Отображаем клавиатуру администратора
#     bot.send_message(message.chat.id, 'Админ-панель:', reply_markup=admin_interface_.generate_main_keyboard())
#     print(f"Admin panel accessed by chat_id: {chat_id}, state reset.")

# @bot.message_handler(commands=['user'])
# def handle_user(message):
#     # Сбрасываем состояние пользователя
#     chat_id = message.chat.id
#     if chat_id in user_interface_.user_states:
#         user_interface_.user_states[chat_id] = {}
#     # Отображаем клавиатуру юзера
#     bot.send_message(message.chat.id, 'Юзер-панель:', reply_markup=user_interface_.generate_main_keyboard())
#     print(f"User panel accessed by chat_id: {chat_id}, state reset.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    role_switcher.admin_interface_.handle_callback(call) #Обработчик callback

bot.polling(none_stop = True)