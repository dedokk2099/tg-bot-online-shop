from telebot import types

def generate_main_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_catalog = types.KeyboardButton("Каталог")
        button_new_orders = types.KeyboardButton("Новые заказы")
        button_in_progress = types.KeyboardButton("В работе")
        button_history = types.KeyboardButton("История")
        markup.add(button_catalog, button_new_orders)
        markup.add(button_in_progress, button_history)
        return markup

def generate_edit_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Название", "Цена", "Описание", "Количество", "Изображение", "Выход")
    return markup