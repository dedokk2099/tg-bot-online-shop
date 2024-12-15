import view.keyboards as keyboards
import model.database as database
import telebot
from telebot import types
from PIL import Image
import io
import requests
import os
import uuid
from html import escape #для экранирования html символов

from model.orders import add_new_order, get_orders, OrderStatus, DeliveryType
from model.products import products_as_class
from model.user import User
from model.pickup_points import pickup_points

class UserController:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}
        self.users = {}
        self.products = products_as_class
        self.cart_messages = {}
        self.catalog_messages = {}
        self.show_catalog_message_id = None
        self.show_cart_message_id = None
        self.show_cart_sum_message_id = None
        self.chat_messages = {}


    def delete_catalog_messages(self, chat_id):
        for message_id in self.catalog_messages.values():
            try:
                self.bot.delete_message(chat_id, message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения: {e}")
        self.catalog_messages = {} # Очищаем словарь после удаления
        try:
            new_text = "Внимание: каталог очищен, для перехода в него нажмите кнопку 'Товары'"
            self.bot.edit_message_text(text=new_text, chat_id=chat_id, message_id=self.show_catalog_message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка редактирования сообщения: {e}")

    def delete_cart_messages(self, chat_id):
        for message_id in self.cart_messages.values():
            try:
                self.bot.delete_message(chat_id, message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения: {e}")
        self.cart_messages = {}  # Очищаем словарь
        try:
            new_text = "Корзина пуста"
            self.bot.edit_message_text(text=new_text, chat_id=chat_id, message_id=self.show_cart_message_id)
            self.show_cart_message_id = None
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Ошибка редактирования сообщения: {e}")
        try:
            self.bot.delete_message(chat_id, self.show_cart_sum_message_id)
            self.show_cart_sum_message_id = None
        except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения: {e}")

    def update_cart_item_message(self, call, product_id, quantity):
        item = next((item for item in self.users[call.message.chat.id].get_cart_items() if item['product'].id == product_id), None)
        if item:
            product = item['product']
            total_price = product.price * quantity
            text = f"<b>{product.name}</b>\n{product.price} ₽ x {quantity} = {total_price} ₽"
            try:
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=self.cart_messages[product_id], text=text, parse_mode="HTML", reply_markup=keyboards.generate_cart_item_keyboard(product_id, quantity))
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка редактирования сообщения: {e}")
    
    def update_cart_sum_message(self, chat_id):
        user = self.users.get(chat_id)
        if not user:
            return
        total_sum = self.calculate_total_sum(user.get_cart_items())
        message_id = self.show_cart_sum_message_id
        if message_id:
            try:
                self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Итого: {total_sum} ₽", reply_markup=keyboards.generate_cart_keyboard())
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка обновления сообщения с суммой: {e}")
        else:
            print("Message ID for cart sum not found")


    def send_product_info(self, chat_id, product):
        user = self.users.get(chat_id)
        markup = keyboards.generate_add_to_cart_keyboard(product.id)
        if user:
            number = user.cart.get(product.id, 0)
            if number > 0:
                markup = keyboards.generate_go_to_cart_keyboard(product.id, number)
        text = f"<b>{product.name}</b>\nСтоимость: {product.price} ₽\nОписание: {product.description}"
        try:
            if product.image:
                image_url_or_path = product.image
                # Проверяем, является ли image URL или локальным путем
                if image_url_or_path.startswith(('http://', 'https://')):
                    response = requests.get(image_url_or_path, stream=True)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                else:
                    # Если это локальный файл, открываем его
                    with open(image_url_or_path, 'rb') as file:
                        image = Image.open(file)
                        # Копируем изображение в буфер памяти
                        image_io = io.BytesIO()
                        image.save(image_io, format='JPEG')
                        image_io.seek(0)
                # Уменьшаем размер изображения
                image.thumbnail((200, 200))
                image_io = io.BytesIO()
                image.save(image_io, format='JPEG')
                image_io.seek(0)
                msg = self.bot.send_photo(chat_id, image_io, caption=text, parse_mode="HTML", reply_markup=markup)
            else:
                msg = self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

            
            self.catalog_messages[product.id] = msg.message_id
        except requests.exceptions.RequestException as e:
            self.bot.send_message(chat_id, f"Ошибка загрузки изображения для товара {product.name}: {e}")
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при обработке изображения для товара {product.name}: {e}")
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    
    def show_catalog(self, message):
        chat_id = message.chat.id
        print(f"show_catalog called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        if not self.products:
            self.bot.send_message(chat_id, "Каталог пуст")
            return

        msg = self.bot.send_message(message.chat.id, "Список товаров в каталоге:")
        self.show_catalog_message_id = msg.message_id

        # if message.chat.id not in self.user_states:
        self.user_states[message.chat.id] = {"state": 0}  # Начальное состояние
        if self.user_states[message.chat.id].get('state') == 0:
            for product in self.products:
                self.send_product_info(chat_id, product)
        if self.show_cart_message_id is not None:
            for message_id in self.cart_messages.values():
                try:
                    self.bot.delete_message(chat_id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка удаления сообщения: {e}")
            self.cart_messages = {}  # Очищаем словарь
            try:
                self.bot.delete_message(chat_id, self.show_cart_sum_message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения: {e}")
            try:
                new_text = "Внимание: сообщения корзины удалены, для перехода в неё нажмите кнопку 'Корзина'"
                self.bot.edit_message_text(text=new_text, chat_id=chat_id, message_id=self.show_cart_message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка редактирования сообщения: {e}")
  

    def send_cart_item(self, chat_id, item):
        product = item['product']
        quantity = item['quantity']
        total_price = product.price * quantity
        text = f"<b>{product.name}</b>\n{product.price} ₽ x {quantity} = {total_price} ₽"
        msg = self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=keyboards.generate_cart_item_keyboard(product.id, quantity))
        self.cart_messages[item['product'].id] = msg.message_id
        
    def calculate_total_sum(self, cart_items):
        return sum(item['product'].price * item['quantity'] for item in cart_items)

    def show_cart(self, message, call):
        chat_id = message.chat.id
        print(f"show_cart called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        user = self.users.get(chat_id)
        if user is None or not user.cart:
            if call:
                self.bot.answer_callback_query(call.id, text="Корзина пуста")
                return
            else:
                self.bot.send_message(chat_id, "Корзина пуста")
                return

        msg = self.bot.send_message(message.chat.id, "Список товаров в корзине:")
        self.show_cart_message_id = msg.message_id

        for item in user.get_cart_items():
            self.send_cart_item(chat_id, item)
        total_sum = self.calculate_total_sum(user.get_cart_items())
        text = f"Итого: {total_sum} ₽"
        msg = self.bot.send_message(chat_id, text, reply_markup=keyboards.generate_cart_keyboard())
        self.show_cart_sum_message_id = msg.message_id
        self.delete_catalog_messages(chat_id)
        

    def get_open_orders(self, chat_id):
        return [order for order in get_orders(customer_id=chat_id) if order.status != OrderStatus.RECEIVED]

    def get_received_orders(self, chat_id):
        return [order for order in get_orders(customer_id=chat_id) if order.status == OrderStatus.RECEIVED]

    def send_order_info(self, order, chat_id):
        items_str = ""
        for i, item in enumerate(order.items):
            product_name = escape(item['product'].name) # экранируем от html атак
            product_price = item['product'].price
            quantity = item['quantity']
            total_item_price = product_price * quantity
            items_str += f"{i+1}. <b>{product_name}</b>\n{product_price} ₽ x {quantity} = {total_item_price} ₽\n"
            text = f"""Номер заказа: <b>{order.id}</b>
Статус: <b>{order.status.value}</b>
Дата и время: {order.order_datetime.strftime('%d.%m.%y %H:%M')}
Способ получения: <b>{order.delivery_type.value}</b>\n
Состав заказа:
{items_str}
Итого: {order.total_sum} ₽"""
        if order.delivery_type == DeliveryType.DELIVERY:
            text += f"\n\nАдрес доставки: {order.delivery_address}"
        else:
            text += f"\n\nАдрес пункта самовывоза: {order.delivery_address}"
        self.bot.send_message(chat_id, text, parse_mode='html', reply_markup=keyboards.generate_watch_products_keyboard(order))


    def show_open_orders(self, message):
        chat_id = message.chat.id
        open_orders = self.get_open_orders(chat_id)
        if open_orders:
            self.bot.send_message(chat_id, "Список открытых заказов:")
            for order in open_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "У Вас нет открытых заказов")

    def show_received_orders(self, message):
        chat_id = message.chat.id
        received_orders = self.get_received_orders(chat_id)
        if received_orders:
            self.bot.send_message(chat_id, "Список полученных заказов:")
            for order in received_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "У Вас пока нет полученных заказов")
    

    def show_delivery_options(self, chat_id):
        msg = self.bot.send_message(chat_id, "Выберите способ получения заказа:", reply_markup=keyboards.generate_delivery_type_keyboard())
        self.chat_messages[f"{chat_id}:delivery_message_id"] = msg.message_id

    def handle_delivery_address(self, message):
        chat_id = message.chat.id
        delivery_address = message.text
        self.user_states[chat_id] = self.user_states.get(chat_id, {})
        self.user_states[chat_id]["delivery_address"] = delivery_address
        print(f"handle_delivery_address called for chat_id: {chat_id}, address: {delivery_address}")
        self.show_payment_options(message, DeliveryType.DELIVERY)

    def show_payment_options(self, message, delivery_type):
        chat_id = message.chat.id
        msg = self.bot.send_message(chat_id, "Выберите способ оплаты:", reply_markup=keyboards.generate_payment_type_keyboard(delivery_type))
        self.chat_messages[f"{chat_id}:payment_message_id"] = msg.message_id

    def create_order(self, chat_id, delivery_type, delivery_address):
        user = self.users.get(chat_id)
        new_order = user.create_order(delivery_type, delivery_address)
        self.bot.send_message(chat_id, f"Заказ №{new_order.id} оформлен!\nТип получения: {new_order.delivery_type.value}", reply_markup=keyboards.generate_user_keyboard())
        self.delete_cart_messages(chat_id)

  
    def handle_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        message_id = call.message.message_id
        state_data = self.user_states.get(chat_id, {})
        print(f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        data = callback_data.split(":")
        if data[1] == "add":
            print(f"handle_callback (add) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user = self.users.get(chat_id)
            if user is None:
                # Новый пользователь
                user = User(chat_id)
                print(f"Создали User {chat_id}")
                self.users[chat_id] = user
            user.add_to_cart(product_id)
            print(f"Добавили товар {product_id} в корзину")
            self.bot.answer_callback_query(call.id, text="Товар добавлен в корзину!")
            # Создаем новые кнопки
            try:
                self.bot.edit_message_reply_markup(reply_markup=keyboards.generate_go_to_cart_keyboard(product_id, 1), chat_id=chat_id, message_id=message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка редактирования сообщения: {e}")
        elif data[1] == "decrease":
            print(f"handle_callback (decrease) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user = self.users.get(chat_id)
            user.decrease_from_cart(product_id)
            number = user.cart[product_id]
            if number == 0:
                user.remove_from_cart(product_id)
                self.bot.edit_message_reply_markup(reply_markup=keyboards.generate_add_to_cart_keyboard(product_id), chat_id=call.message.chat.id, message_id=call.message.message_id)
            else:
                self.bot.edit_message_reply_markup(reply_markup=keyboards.generate_go_to_cart_keyboard(product_id, number), chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif data[1] == "increase":
            print(f"handle_callback (increase) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user = self.users.get(chat_id)
            user.add_to_cart(product_id)
            number = user.cart[product_id]
            self.bot.edit_message_reply_markup(reply_markup=keyboards.generate_go_to_cart_keyboard(product_id, number), chat_id=call.message.chat.id, message_id=call.message.message_id)
        elif data[1] == "go_to_cart":
            print(f"handle_callback (cart) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            self.show_cart(call.message, call)

    def handle_cart_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        user = self.users.get(chat_id)
        print(f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_cart_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        data = callback_data.split(":")
        if data[1] == "decrease":
            print(f"handle_cart_callback (decrease) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user.decrease_from_cart(product_id)
            number = user.cart[product_id]
            if number > 0:
                self.update_cart_item_message(call, product_id, number)
            else:
                user.remove_from_cart(product_id)
                message_id = self.cart_messages.pop(product_id, None) # Удаляем message_id из словаря
                if message_id:
                    try:
                        self.bot.delete_message(call.message.chat.id, message_id)
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"Ошибка удаления сообщения: {e}")
            self.update_cart_sum_message(chat_id)
        elif data[1] == "increase":
            print(f"handle_cart_callback (increase) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user.add_to_cart(product_id)
            number = user.cart[product_id]
            self.update_cart_item_message(call, product_id, number)
            self.update_cart_sum_message(chat_id)
        elif data[1] == "remove":
            print(f"handle_cart_callback (remove) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            product_id = data[2]
            user.remove_from_cart(product_id)
            message_id = self.cart_messages.pop(product_id, None)
            if message_id:
                try:
                    self.bot.delete_message(call.message.chat.id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка удаления сообщения: {e}")
            self.update_cart_sum_message(chat_id)
        elif data[1] == "clear":
            user.cart = {}
            self.delete_cart_messages(chat_id)
        elif data[1] == "add":
            print(f"handle_cart_callback (add) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            self.show_delivery_options(chat_id)

    def handle_delivery_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_delivery_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        data = callback_data.split(":")
        if data[1] == "pickup":
            message_text = "Выберите пункт выдачи:\n\n"
            for point in pickup_points:
                message_text += (
                    f"<b>{point['name']}</b>\n"
                    f"Адрес: {point['address']}\n"
                    f"Время работы: {point['working_hours']}\n\n"
                )
            self.bot.send_message(chat_id, message_text, parse_mode='html', reply_markup=keyboards.generate_pickup_points_keyboard(pickup_points))
        elif data[1] == "delivery":
            self.bot.send_message(chat_id, "Введите адрес доставки:")
            self.bot.register_next_step_handler(call.message, self.handle_delivery_address)

    def handle_payment_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_payment_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        data = callback_data.split(":")
        delivery_type_str = data[2] 
        delivery_type = DeliveryType(delivery_type_str)
        delivery_address = state_data.get("delivery_address")
        if data[1] == "on_delivery":
            self.create_order(chat_id, delivery_type, delivery_address)
        elif data[1] == "online":
            # Здесь должен быть код имитации онлайн-оплаты
            self.bot.send_message(chat_id, "Заказ оплачен!")
            self.create_order(chat_id, delivery_type, delivery_address)

    def handle_pickup_point_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_pickup_point_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        data = callback_data.split(":")
        pickup_point_id = data[1]
        pickup_point = next((point for point in pickup_points if point["id"] == pickup_point_id), None)
        if not pickup_point:
            self.bot.send_message(chat_id, "Ошибка выбора пункта выдачи")
            return
        print(f"выбран пункт выдачи:{pickup_point["name"]}")
        self.user_states[chat_id]["delivery_address"] = pickup_point["address"]
        self.show_payment_options(call.message, DeliveryType.PICKUP)
            
    