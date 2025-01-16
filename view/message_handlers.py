from view.bot import bot
from controller.role_switcher import *

role_switcher_ = RoleSwitcher(bot)
"""
Объект для переключения между ролями (админ/пользователь).

Используется для определения, какой контроллер (административный или пользовательский)
должен обрабатывать входящие сообщения.

:type: view.role_switcher.RoleSwitcher
"""

def handle_admin_catalog(message):
    '''
    Вызывает функцию отображения каталога администратору
    '''
    role_switcher_.admin_controller_.show_catalog(message)
def handle_new_orders(message):
    '''
    Вызывает функцию отображения новых заказов администратору
    '''
    bot.send_message(message.chat.id, "Список новых заказов:")
    role_switcher_.admin_controller_.show_new_orders(message)
def handle_in_progress(message):
    '''
    Вызывает функцию отображения заказов в работе
    '''
    bot.send_message(message.chat.id, "Список заказов в работе:")
    role_switcher_.admin_controller_.show_in_progress_orders(message)
def handle_admin_history(message):
    '''
    Вызывает функцию отображения выполненных заказов администратору
    '''
    bot.send_message(message.chat.id, "Список выполненных заказов:")
    role_switcher_.admin_controller_.show_completed_orders(message)

def handle_user_catalog(message):
    '''
    Вызывает функцию отображения каталога пользователю
    '''
    role_switcher_.user_controller_.show_catalog(message)
def handle_cart(message):
    '''
    Вызывает функцию отображения корзины
    '''
    role_switcher_.user_controller_.show_cart(message, call = None)
def handle_open_orders(message):
    '''
    Вызывает функцию отображения открытых заказов пользователю
    '''
    role_switcher_.user_controller_.show_open_orders(message)
def handle_user_history(message):
    '''
    Вызывает функцию отображения полученных заказов пользователю
    '''
    role_switcher_.user_controller_.show_received_orders(message)
def handle_unknown(message):
    '''
    Отправляет в чат сообщение о неизвестной команде
    '''
    bot.send_message(message.chat.id, "Неизвестная команда")


@bot.message_handler(commands=['start'])
def handle_start(message):
    """
    Обрабатывает команду /start.

    Регистрирует пользователя в системе через RoleSwitcher.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    role_switcher_.register_user(message)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    """
    Обрабатывает команду /admin.

    Переключает пользователя в режим администратора через RoleSwitcher.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    role_switcher_.choose_admin(message)

@bot.message_handler(commands=['user'])
def handle_user(message):
    """
    Обрабатывает команду /user.

    Переключает пользователя в режим пользователя через RoleSwitcher.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    role_switcher_.choose_user(message)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """
    Обрабатывает загрузку фото.

    Передает запрос на обработку фото административному контроллеру.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    role_switcher_.admin_controller_.handle_photo_upload(message)

@bot.message_handler(func=lambda message: message.text in ["Каталог", "Новые заказы", "В работе", "История"])
def handle__admin_menu(message):
    """
    Обрабатывает сообщения с командами админ-меню.

    Вызывает соответствующие обработчики для запрошенной команды
    если пользователь является админом.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
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
    """
    Обрабатывает сообщения с командами пользовательского меню.

    Вызывает соответствующие обработчики для запрошенной команды.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
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
    """
    Обрабатывает неизвестные текстовые сообщения.

    Отправляет сообщение "Неизвестная команда" в чат пользователя.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    bot.send_message(message.chat.id, "Неизвестная команда")

@bot.callback_query_handler(func=lambda call: call.data.startswith("status"))
def handle_status_callback(call):
    """
    Обрабатывает callback-запросы, связанные со статусом заказа (админ).

    Передает callback-запрос административному контроллеру для
    обработки изменения статуса.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.admin_controller_.handle_change_status(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("user"))
def handle_user_callback(call):
    """
    Обрабатывает callback-запросы, связанные с пользователем.

    Передает callback-запрос пользовательскому контроллеру для обработки
    операций, связанных с пользователем.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cart"))
def handle_cart_callback(call):
    """
    Обрабатывает callback-запросы, связанные с корзиной пользователя.

    Передает callback-запрос пользовательскому контроллеру для обработки
    операций, связанных с корзиной.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_cart_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delivery"))
def handle_delivery_callback(call):
    """
    Обрабатывает callback-запросы, связанные с выбором типа доставки.

    Передает callback-запрос пользовательскому контроллеру для обработки
    выбора типа доставки.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_delivery_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("payment"))
def handle_payment_callback(call):
    """
     Обрабатывает callback-запросы, связанные с выбором способа оплаты.
     Передает callback-запрос пользовательскому контроллеру для обработки выбора способа оплаты.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_payment_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pickup_point"))
def handle_pickup_point_callback(call):
    """
     Обрабатывает callback-запросы, связанные с выбором пункта самовывоза.
     Передает callback-запрос пользовательскому контроллеру для обработки выбора пункта самовывоза.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_pickup_point_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("watch"))
def handle_watch_products_callback(call):
    """
    Обрабатывает callback-запросы для просмотра товаров в заказе.
    Передает callback-запрос пользовательскому контроллеру для
    обработки запроса на просмотр товаров в заказе.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.user_controller_.handle_watch_products_callback(call)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """
    Обрабатывает callback-запросы, не связанные с пользовательскими действиями.
    Передает callback-запрос административному контроллеру для обработки
    непосредственно им.

    :param call: Объект callback-запроса Telegram
    :type call: telebot.types.CallbackQuery
    """
    role_switcher_.admin_controller_.handle_callback(call)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout_payment_query(query):
    """
    Обрабатывает запрос подтверждения перед оплатой.

    Передает запрос пользовательскому контроллеру для обработки
    подтверждения оплаты.

    :param query: Объект запроса Telegram
    :type query: telebot.types.PreCheckoutQuery
    """
    role_switcher_.user_controller_.checkout_payment(query)

@bot.message_handler(content_types=['successful_payment'])
def handle_got_payment(message):
    """
    Обрабатывает подтверждение успешной оплаты.

    Передает сообщение пользовательскому контроллеру для обработки
    успешной оплаты.

    :param message: Объект входящего сообщения Telegram
    :type message: telebot.types.Message
    """
    role_switcher_.user_controller_.got_payment(message)

# @bot.message_handler(commands=['start'])
# def handle_start(message):
#     role_switcher_.register_user(message)

# @bot.message_handler(commands=['admin'])
# def handle_admin(message):
#     role_switcher_.choose_admin(message)

# @bot.message_handler(commands=['user'])
# def handle_user(message):
#     role_switcher_.choose_user(message)

# @bot.message_handler(content_types=['photo'])
# def handle_photo(message):
#     role_switcher_.admin_controller_.handle_photo_upload(message)

# @bot.message_handler(func=lambda message: message.text in ["Каталог", "Новые заказы", "В работе", "История"])
# def handle__admin_menu(message):
#     chat_id = message.chat.id
#     if role_switcher_.user.is_admin(chat_id):
#         if message.text == "Каталог":
#             handle_admin_catalog(message)
#         elif message.text == "Новые заказы":
#             handle_new_orders(message)
#         elif message.text == "В работе":
#             handle_in_progress(message)
#         elif message.text == "История":
#             handle_admin_history(message)
#     else:
#         bot.send_message(message.chat.id, "Неизвестная команда")

# @bot.message_handler(func=lambda message: message.text in ["Товары", "Корзина", "Открытые заказы", "История заказов"])
# def handle_user_menu(message):
#     if message.text == "Товары":
#         handle_user_catalog(message)
#     elif message.text == "Корзина":
#         handle_cart(message)
#     elif message.text == "Открытые заказы":
#         handle_open_orders(message)
#     elif message.text == "История заказов":
#         handle_user_history(message)

# @bot.message_handler(func=lambda message: True)
# def handle_unknown(message):
#     bot.send_message(message.chat.id, "Неизвестная команда")


# @bot.callback_query_handler(func=lambda call: call.data.startswith("status"))
# def handle_status_callback(call):
#     role_switcher_.admin_controller_.handle_change_status(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("user"))
# def handle_user_callback(call):
#     role_switcher_.user_controller_.handle_callback(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("cart"))
# def handle_cart_callback(call):
#     role_switcher_.user_controller_.handle_cart_callback(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("delivery"))
# def handle_delivery_callback(call):
#     role_switcher_.user_controller_.handle_delivery_callback(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("payment"))
# def handle_payment_callback(call):
#     role_switcher_.user_controller_.handle_payment_callback(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("pickup_point"))
# def handle_pickup_point_callback(call):
#     role_switcher_.user_controller_.handle_pickup_point_callback(call)

# @bot.callback_query_handler(func=lambda call: call.data.startswith("watch"))
# def handle_watch_products_callback(call):
#     role_switcher_.user_controller_.handle_watch_products_callback(call)

# @bot.callback_query_handler(func=lambda call: True)
# def handle_callback_query(call):
#     role_switcher_.admin_controller_.handle_callback(call)


# @bot.pre_checkout_query_handler(func=lambda query: True)
# def checkout_payment_query(query):
#     role_switcher_.user_controller_.checkout_payment(query)

# @bot.message_handler(content_types=['successful_payment'])
# def handle_got_payment(message):
#     role_switcher_.user_controller_.got_payment(message)