from view.bot import bot
from controller.role_switcher import *

role_switcher_ = RoleSwitcher(bot)

def handle_admin_catalog(message):
    role_switcher_.admin_controller_.show_catalog(message)
def handle_new_orders(message):
    bot.send_message(message.chat.id, "Список новых заказов:")
    role_switcher_.admin_controller_.show_new_orders(message)
def handle_in_progress(message):
    bot.send_message(message.chat.id, "Список заказов в работе:")
    role_switcher_.admin_controller_.show_in_progress_orders(message)
def handle_admin_history(message):
    bot.send_message(message.chat.id, "Список выполненных заказов:")
    role_switcher_.admin_controller_.show_completed_orders(message)

def handle_user_catalog(message):
    role_switcher_.user_controller_.show_catalog(message)
def handle_cart(message):
    role_switcher_.user_controller_.show_cart(message, call = None)
def handle_open_orders(message):
    role_switcher_.user_controller_.show_open_orders(message)
def handle_user_history(message):
    role_switcher_.user_controller_.show_received_orders(message)
def handle_unknown(message):
    bot.send_message(message.chat.id, "Неизвестная команда")


@bot.message_handler(commands=['start'])
def handle_start(message):
    role_switcher_.register_user(message)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    role_switcher_.choose_admin(message)

@bot.message_handler(commands=['user'])
def handle_user(message):
    role_switcher_.choose_user(message)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    role_switcher_.admin_controller_.handle_photo_upload(message)

@bot.message_handler(func=lambda message: message.text in ["Каталог", "Новые заказы", "В работе", "История"])
def handle__admin_menu(message):
    chat_id = message.chat.id
    if role_switcher_.user.is_admin(chat_id):
        if message.text == "Каталог":
            handle_admin_catalog(message)
        elif message.text == "Новые заказы":
            handle_new_orders(message)
        elif message.text == "В работе":
            handle_in_progress(message)
        elif message.text == "История":
            handle_admin_history(message)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда")

@bot.message_handler(func=lambda message: message.text in ["Товары", "Корзина", "Открытые заказы", "История заказов"])
def handle_user_menu(message):
    if message.text == "Товары":
        handle_user_catalog(message)
    elif message.text == "Корзина":
        handle_cart(message)
    elif message.text == "Открытые заказы":
        handle_open_orders(message)
    elif message.text == "История заказов":
        handle_user_history(message)

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(message.chat.id, "Неизвестная команда")


@bot.callback_query_handler(func=lambda call: call.data.startswith("status"))
def handle_status_callback(call):
    role_switcher_.admin_controller_.handle_change_status(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("user"))
def handle_user_callback(call):
    role_switcher_.user_controller_.handle_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cart"))
def handle_cart_callback(call):
    role_switcher_.user_controller_.handle_cart_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delivery"))
def handle_delivery_callback(call):
    role_switcher_.user_controller_.handle_delivery_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment"))
def handle_payment_callback(call):
    role_switcher_.user_controller_.handle_payment_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pickup_point"))
def handle_pickup_point_callback(call):
    role_switcher_.user_controller_.handle_pickup_point_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("watch"))
def handle_watch_products_callback(call):
    role_switcher_.user_controller_.handle_watch_products_callback(call)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    role_switcher_.admin_controller_.handle_callback(call)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout_payment_query(query):
    role_switcher_.user_controller_.checkout_payment(query)

@bot.message_handler(content_types=['successful_payment'])
def handle_got_payment(message):
    role_switcher_.user_controller_.got_payment(message)