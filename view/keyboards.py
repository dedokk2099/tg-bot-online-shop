from telebot import types
from model.orders import OrderStatus

# Клавиатуры админа

def generate_admin_keyboard():
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

def generate_add_keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
        return markup

def generate_add_or_update_keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
        markup.add(types.InlineKeyboardButton("Обновить каталог", callback_data="catalog"))
        return markup

def generate_product_keyboard(product):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit:{product['id']}"),
            types.InlineKeyboardButton(text="Удалить", callback_data=f"delete:{product['id']}"),
        )
        return markup

def generate_change_status_keyboard(order):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить статус", callback_data=f"change_status:{order.id}"))
        return markup

def generate_status_keyboard(order_id, order_status):
        markup = types.InlineKeyboardMarkup()
        for status in OrderStatus:
                if status == order_status:
                        continue
                button = types.InlineKeyboardButton(text=status.value, callback_data=f"status:{status.name}:{order_id}")
                markup.add(button)
        return markup

# Клавиатуры юзера

def generate_user_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_catalog = types.KeyboardButton("Товары")
        button_my_orders = types.KeyboardButton("Мои заказы")
        button_cart = types.KeyboardButton("Корзина")
        markup.add(button_catalog, button_my_orders, button_cart)
        return markup