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
            types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit:{product.id}"),
            types.InlineKeyboardButton(text="Удалить", callback_data=f"delete:{product.id}"),
        )
        return markup

def generate_delete_keyboard(product_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Да", callback_data=f"confirm_delete:{product_id}"),
                types.InlineKeyboardButton("Нет", callback_data="cancel_delete"))
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
        button_cart = types.KeyboardButton("Корзина")
        button_open_orders = types.KeyboardButton("Открытые заказы")
        button_history = types.KeyboardButton("История заказов")
        markup.add(button_catalog, button_cart) 
        markup.add(button_open_orders, button_history)
        return markup

def generate_add_to_cart_keyboard(product_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Добавить в корзину", callback_data=f"user:add:{product_id}"))
        return markup

def generate_go_to_cart_keyboard(product_id, number):
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 3 #Указываем ширину ряда в 3 кнопки
        markup.add(
            types.InlineKeyboardButton("-", callback_data=f"user:decrease:{product_id}"),
            types.InlineKeyboardButton(f"{number} шт.", callback_data="number"),
            types.InlineKeyboardButton("+", callback_data=f"user:increase:{product_id}")
        )
        markup.add(types.InlineKeyboardButton("Перейти в корзину", callback_data=f"user:go_to_cart"))
        return markup

def generate_cart_item_keyboard(product_id, number):
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 3
        markup.add(
            types.InlineKeyboardButton("-", callback_data=f"cart:decrease:{product_id}"),
            types.InlineKeyboardButton(f"{number} шт.", callback_data="number"),
            types.InlineKeyboardButton("+", callback_data=f"cart:increase:{product_id}")
        )
        markup.add(types.InlineKeyboardButton("Удалить из корзины", callback_data=f"cart:remove:{product_id}"))
        return markup

def generate_cart_keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Очистить корзину", callback_data="cart:clear"))
        markup.add(types.InlineKeyboardButton("Оформить заказ", callback_data="cart:add"))
        return markup

def generate_watch_products_keyboard(order):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Посмотреть товары", callback_data=f"watch:{order.id}"))
        return markup

def generate_delivery_type_keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Самовывоз", callback_data=f"delivery:pickup"))
        markup.add(types.InlineKeyboardButton("Доставка", callback_data=f"delivery:delivery"))
        return markup

def generate_payment_type_keyboard(delivery_type):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Онлайн", callback_data=f"payment:online:{delivery_type.value}"))
        markup.add(types.InlineKeyboardButton("При получении", callback_data=f"payment:on_delivery:{delivery_type.value}"))
        return markup

def generate_pickup_points_keyboard(pickup_points):
        markup = types.InlineKeyboardMarkup()
        for point in pickup_points:
            markup.add(types.InlineKeyboardButton(point["name"], callback_data=f"pickup_point:{point['id']}"))
        return markup