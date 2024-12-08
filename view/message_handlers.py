from view.bot import bot
from controller.role_switcher import *

role_switcher_ = RoleSwitcher(bot)

@bot.message_handler(commands=['start'])
def handle_start(message):
    role_switcher_.register_user(message)

@bot.message_handler(func=lambda message: message.text in ["Каталог"])
def handle_catalog_command(message):
    role_switcher_.admin_controller_.show_catalog(message)

@bot.message_handler(commands=['new_orders'])
def handle_new_orders_command(message):
    bot.send_message(message.chat.id, "Список новых заказов:")
    #handle_new_orders(message)

@bot.message_handler(commands=['in_progress'])
def handle_in_progress_command(message):
    bot.send_message(message.chat.id, "Список заказов в работе:")
    #handle_in_progress(message)

@bot.message_handler(commands=['history'])
def handle_history_command(message):
    bot.send_message(message.chat.id, "Список выполненных заказов:")
    #handle_history(message)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    role_switcher_.admin_controller_.handle_photo_upload(message)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    role_switcher_.choose_admin(message)

@bot.message_handler(commands=['user'])
def handle_user(message):
    role_switcher_.choose_user(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    role_switcher_.admin_controller_.handle_callback(call) #Обработчик callback