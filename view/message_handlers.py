from view.bot import bot
from controller.role_switcher import *

role_switcher_ = RoleSwitcher(bot)

def handle_catalog(message):
    role_switcher_.admin_controller_.show_catalog(message)

def handle_new_orders(message):
    bot.send_message(message.chat.id, "Список новых заказов:")

def handle_in_progress(message):
    bot.send_message(message.chat.id, "Список заказов в работе:")

def handle_history(message):
    bot.send_message(message.chat.id, "Список выполненных заказов:")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    role_switcher_.admin_controller_.handle_photo_upload(message)

@bot.message_handler(func=lambda message: message.text in ["Каталог", "Новые заказы", "В работе", "История"])
def handle_default(message):
    if message.text == "Каталог":
        handle_catalog(message)
    elif message.text == "Новые заказы":
        handle_new_orders(message)
    elif message.text == "В работе":
        handle_in_progress(message)
    elif message.text == "История":
        handle_history(message)
    else:
        handle_unknown(message)

@bot.message_handler(commands=['start'])
def handle_start(message):
    role_switcher_.register_user(message)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    role_switcher_.choose_admin(message)

@bot.message_handler(commands=['user'])
def handle_user(message):
    role_switcher_.choose_user(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    role_switcher_.admin_controller_.handle_callback(call) #Обработчик callback