import io
import logging
from html import escape  # для экранирования html символов

import requests
import telebot
from PIL import Image
from telebot import types
from telebot.apihelper import ApiException

from model.orders import DeliveryType, OrderStatus, get_order_items, get_orders
from model.pickup_points import pickup_points
from model.products import Product, get_products
from model.user import User
from view import keyboards
from view.bot import payment_token


class UserController:
    """
    Отвечает за работу бота в части пользователя
    """

    def __init__(self, bot):
        """
        Инициализирует бот, состояния, словарь пользователей, загружает товары из базы
        """
        self.bot = bot
        self.user_states = {}
        self.users = {}
        self.products = get_products()
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            encoding="utf-8",
        )

    def delete_catalog_messages(self, chat_id):
        """
        Удаляет сообщение каталога из чата с уведомлением пользователя
        """
        if "catalog_message_ids" in self.user_states[chat_id]:
            for product_id, message_id in self.user_states[chat_id][
                "catalog_message_ids"
            ].items():
                try:
                    self.bot.delete_message(chat_id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка удаления сообщения товара каталога: {e}")
            self.user_states[chat_id]["catalog_message_ids"] = {}
        if "show_catalog_message_id" in self.user_states[chat_id]:
            try:
                new_text = "Внимание: каталог очищен, для перехода в него нажмите кнопку 'Товары'"
                self.bot.edit_message_text(
                    text=new_text,
                    chat_id=chat_id,
                    message_id=self.user_states[chat_id]["show_catalog_message_id"],
                )
                self.user_states[chat_id]["show_catalog_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка редактирования сообщения вывода каталога: {e}")

    def delete_all_catalog_messages(self, chat_id):
        """
        Удаляет все сообщения каталога без уведомления пользователю
        """
        if "catalog_message_ids" in self.user_states[chat_id]:
            for product_id, message_id in self.user_states[chat_id][
                "catalog_message_ids"
            ].items():
                try:
                    self.bot.delete_message(chat_id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка удаления сообщения товара каталога: {e}")
            self.user_states[chat_id]["catalog_message_ids"] = {}
        if "show_catalog_message_id" in self.user_states[chat_id]:
            try:
                self.bot.delete_message(
                    chat_id, self.user_states[chat_id]["show_catalog_message_id"]
                )
                self.user_states[chat_id]["show_catalog_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения вывода каталога: {e}")

    def delete_cart_messages(self, chat_id):
        """
        Удаляет сообщения корзины
        """
        if "cart_message_ids" in self.user_states[chat_id]:
            for product_id, message_id in self.user_states[chat_id][
                "cart_message_ids"
            ].items():
                try:
                    self.bot.delete_message(chat_id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(
                        f"Ошибка удаления сообщения товара корзины в delete_cart_messages: {e}"
                    )
            self.user_states[chat_id]["cart_message_ids"] = {}
        if "show_cart_sum_message_id" in self.user_states[chat_id]:
            try:
                self.bot.delete_message(
                    chat_id, self.user_states[chat_id]["show_cart_sum_message_id"]
                )
                self.user_states[chat_id]["show_cart_sum_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(
                    f"Ошибка удаления сообщения вывода суммы корзины в delete_cart_messages: {e}"
                )
        if "chat_message_ids" in self.user_states[chat_id]:
            for message_id in self.user_states[chat_id]["chat_message_ids"]:
                try:
                    self.bot.delete_message(chat_id, message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка удаления сообщения: {e}")
            self.user_states[chat_id]["chat_message_ids"] = []

    def delete_cart_messages_and_cart_is_not_empty(self, chat_id):
        """
        Удаляет сообщения корзины с уведомлением пользователя
        """
        self.delete_cart_messages(chat_id)
        if "show_cart_message_id" in self.user_states[chat_id]:
            try:
                new_text = "Внимание: сообщения корзины удалены, для перехода в неё нажмите кнопку 'Корзина'"
                self.bot.edit_message_text(
                    text=new_text,
                    chat_id=chat_id,
                    message_id=self.user_states[chat_id]["show_cart_message_id"],
                )
                self.user_states[chat_id]["show_cart_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(
                    f"Ошибка редактирования сообщения вывода корзины в delete_cart_messages_and_cart_is_not_empty: {e}"
                )

    def delete_cart_messages_and_cart_is_empty(self, chat_id):
        """
        Удаляет сообщения корзины при очистке корзины
        """
        self.delete_cart_messages(chat_id)
        if "show_cart_message_id" in self.user_states[chat_id]:
            try:
                new_text = "Корзина пуста"
                self.bot.edit_message_text(
                    text=new_text,
                    chat_id=chat_id,
                    message_id=self.user_states[chat_id]["show_cart_message_id"],
                )
                self.user_states[chat_id]["show_cart_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(
                    f"Ошибка редактирования сообщения вывода корзины в delete_cart_messages_and_cart_is_empty: {e}"
                )

    def delete_all_cart_messages(self, chat_id):
        """
        Удаляет сообщения корзины без уведомления пользователя
        """
        self.delete_cart_messages(chat_id)
        if "show_cart_message_id" in self.user_states[chat_id]:
            try:
                self.bot.delete_message(
                    chat_id, self.user_states[chat_id]["show_cart_message_id"]
                )
                self.user_states[chat_id]["show_cart_message_id"] = None
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка удаления сообщения вывода корзины: {e}")

    def update_cart_item_message(self, call, product_id, quantity):
        """
        Обновляет сообщения о товаре корзины

        :param product_id: id товара
        :type product_id:
        :param quantity: кол-во единиц товара в корзине
        :type quantity:
        """
        chat_id = call.message.chat.id
        item = next(
            (
                item
                for item in self.users[chat_id].get_cart_items()
                if item["product"].id == product_id
            ),
            None,
        )
        if item:
            product = item["product"]
            total_price = product.price * quantity
            text = f"<b>{product.name}</b>\n{product.price} ₽ x {quantity} = {total_price} ₽"
            try:
                self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=self.user_states[chat_id]["cart_message_ids"][
                        product_id
                    ],
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboards.generate_cart_item_keyboard(
                        product_id, quantity
                    ),
                )
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка редактирования сообщения товара корзины: {e}")

    def update_cart_sum_message(self, chat_id):
        """
        Обновляет сообщение о сумме корзины
        """
        user = self.users.get(chat_id)
        if not user:
            return
        total_sum = user.calculate_total_sum()
        message_id = self.user_states[chat_id]["show_cart_sum_message_id"]
        if message_id:
            try:
                self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"Итого: {total_sum} ₽",
                    reply_markup=keyboards.generate_cart_keyboard(),
                )
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка обновления сообщения с суммой: {e}")
        else:
            print("Message ID for cart sum not found")

    def send_product_info(self, chat_id, product: Product):
        """
        Выводит в чат информацию о товаре
        :param product: товар, информацию о котором надо вывести
        """
        if not product.is_active:
            self.bot.send_message(
                chat_id,
                f"Название: {product.name}\nОписание: {product.description}\nПоследняя цена: {product.price} ₽\n\nТовар снят с продажи",
            )
            return
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
                if image_url_or_path.startswith(("http://", "https://")):
                    response = requests.get(image_url_or_path, stream=True, timeout=10)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                else:
                    # Если это локальный файл, открываем его
                    with open(image_url_or_path, "rb") as file:
                        image = Image.open(file)
                        # Копируем изображение в буфер памяти
                        image_io = io.BytesIO()
                        image.save(image_io, format="JPEG")
                        image_io.seek(0)
                # Уменьшаем размер изображения
                image.thumbnail((200, 200))
                image_io = io.BytesIO()
                image.save(image_io, format="JPEG")
                image_io.seek(0)
                msg = self.bot.send_photo(
                    chat_id,
                    image_io,
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=markup,
                )
            else:
                msg = self.bot.send_message(
                    chat_id, text, parse_mode="HTML", reply_markup=markup
                )

            if "catalog_message_ids" not in self.user_states[chat_id]:
                self.user_states[chat_id]["catalog_message_ids"] = {}
            self.user_states[chat_id]["catalog_message_ids"][
                product.id
            ] = msg.message_id
        except requests.exceptions.RequestException as e:
            self.bot.send_message(
                chat_id, f"Ошибка загрузки изображения для товара {product.name}: {e}"
            )
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            self.bot.send_message(
                chat_id,
                f"Ошибка при обработке изображения для товара {product.name}: {e}",
            )
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

    def show_catalog(self, message):
        """
        Вызывает отображение каталога в чате
        """
        chat_id = message.chat.id
        print(
            f"show_catalog called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
        )
        active_products = [product for product in self.products if product.is_active]
        if not active_products:
            self.bot.send_message(chat_id, "Каталог пуст")
            return
        msg = self.bot.send_message(chat_id, "Список товаров в каталоге:")
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {"state": 0}
        self.delete_all_catalog_messages(chat_id)
        self.user_states[chat_id]["show_catalog_message_id"] = msg.message_id
        for product in active_products:
            self.send_product_info(chat_id, product)
        self.delete_cart_messages_and_cart_is_not_empty(chat_id)

    def send_cart_item(self, chat_id, item):
        """
        Выводит в чат информацию о товаре в корзине

        :param item: элемент корзины - словарь 'товар : количество'
        """
        product = item["product"]
        quantity = item["quantity"]
        total_price = product.price * quantity
        text = (
            f"<b>{product.name}</b>\n{product.price} ₽ x {quantity} = {total_price} ₽"
        )
        msg = self.bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=keyboards.generate_cart_item_keyboard(product.id, quantity),
        )
        if "cart_message_ids" not in self.user_states[chat_id]:
            self.user_states[chat_id]["cart_message_ids"] = {}
        self.user_states[chat_id]["cart_message_ids"][product.id] = msg.message_id

    def show_cart(self, message, call):
        """
        Вызывает отображение корзины в чате
        """
        chat_id = message.chat.id
        print(
            f"show_cart called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
        )
        user = self.users.get(chat_id)
        if user is None or not user.get_cart_items():
            if call:
                self.bot.answer_callback_query(call.id, text="Корзина пуста")
                return
            else:
                self.bot.send_message(chat_id, "Корзина пуста")
                return
        self.delete_all_cart_messages(chat_id)
        msg = self.bot.send_message(message.chat.id, "Список товаров в корзине:")
        self.user_states[chat_id]["show_cart_message_id"] = msg.message_id

        for item in user.get_cart_items():
            self.send_cart_item(chat_id, item)
        total_sum = user.calculate_total_sum()
        text = f"Итого: {total_sum} ₽"
        msg = self.bot.send_message(
            chat_id, text, reply_markup=keyboards.generate_cart_keyboard()
        )
        self.user_states[chat_id]["show_cart_sum_message_id"] = msg.message_id
        self.delete_catalog_messages(chat_id)

    def get_open_orders(self, chat_id):
        """
        Возвращает список открытых заказов
        """
        return [
            order
            for order in get_orders(customer_id=chat_id)
            if order.status != OrderStatus.RECEIVED.value
        ]

    def get_order_by_id(self, chat_id, order_id):
        """
        Возвращает заказ по его номеру

        :param order_id: номер заказа
        """
        orders = get_orders(customer_id=chat_id)
        for order in orders:
            if order.id == order_id:
                return order  # Возвращаем заказ
        return None

    def get_received_orders(self, chat_id):
        """
        Возвращает полученные заказы
        """
        return [
            order
            for order in get_orders(customer_id=chat_id)
            if order.status == OrderStatus.RECEIVED.value
        ]

    def send_order_info(self, order, chat_id):
        """
        Выводит в чат информацию о заказе
        """
        order_items = get_order_items(order.id)
        if order_items:
            items_str = ""
            for i, item in enumerate(order_items):
                product_name = escape(item.name)  # экранируем от html атак
                product_price = item.price
                quantity = item.quantity
                total_item_price = product_price * quantity
                items_str += f"{i+1}. <b>{product_name}</b>\n{product_price} ₽ x {quantity} = {total_item_price} ₽\n"
        text = f"""Номер заказа: <b>{order.id}</b>
Статус: <b>{order.status}</b>
Дата и время: {order.order_datetime.strftime('%d.%m.%y %H:%M')}
Способ получения: <b>{order.delivery_type}</b>\n
Состав заказа:
{items_str}
Итого: {order.total_sum} ₽"""
        if order.delivery_type == DeliveryType.DELIVERY.value:
            text += f"\n\nАдрес доставки: {order.delivery_address}"
        else:
            text += f"\n\nАдрес пункта самовывоза: {order.delivery_address}"
        self.bot.send_message(
            chat_id,
            text,
            parse_mode="html",
            reply_markup=keyboards.generate_watch_products_keyboard(order),
        )

    def show_open_orders(self, message):
        """
        Выводит в чат открытые заказы
        """
        chat_id = message.chat.id
        open_orders = self.get_open_orders(chat_id)
        if open_orders:
            self.bot.send_message(chat_id, "Список открытых заказов:")
            for order in open_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "У Вас нет открытых заказов")

    def show_received_orders(self, message):
        """
        Выводит в чат полученные заказы
        """
        chat_id = message.chat.id
        received_orders = self.get_received_orders(chat_id)
        if received_orders:
            self.bot.send_message(chat_id, "Список полученных заказов:")
            for order in received_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "У Вас пока нет полученных заказов")

    def delete_buttons(self, chat_id):
        """
        Удаляет кнопки под сообщениями корзины
        """
        if "cart_message_ids" in self.user_states[chat_id]:
            for product_id, message_id in self.user_states[chat_id][
                "cart_message_ids"
            ].items():
                product = next((p for p in self.products if p.id == product_id), None)
                if not product.is_active:
                    text = f"Товар <b>{product.name}</b> снят с продажи"
                    try:
                        self.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=text,
                            parse_mode="HTML",
                        )
                    except telebot.apihelper.ApiTelegramException as e:
                        print(
                            f"delete_buttons: Ошибка редактирования сообщения товара корзины с ID {message_id}: {e}"
                        )
                try:
                    self.bot.edit_message_reply_markup(
                        chat_id=chat_id, message_id=message_id, reply_markup=None
                    )
                    print(
                        f"delete_buttons: Кнопки под сообщением товара  корзины с ID {message_id} были удалены."
                    )
                except telebot.apihelper.ApiTelegramException as e:
                    print(
                        f"delete_buttons: Ошибка удаления кнопок у сообщения товара корзины с ID {message_id}: {e}"
                    )
        if "show_cart_sum_message_id" in self.user_states[chat_id]:
            user = self.users.get(chat_id)
            total_sum = user.calculate_total_sum()
            message_id = self.user_states[chat_id]["show_cart_sum_message_id"]
            try:
                self.bot.edit_message_text(
                    chat_id=chat_id, message_id=message_id, text=f"Итого: {total_sum} ₽"
                )
            except telebot.apihelper.ApiTelegramException as e:
                print(
                    f"delete_buttons: Ошибка обновления сообщения с суммой корзины с ID {message_id}: {e}"
                )
            try:
                self.bot.edit_message_reply_markup(
                    chat_id=chat_id, message_id=message_id, reply_markup=None
                )
                print(
                    f"delete_buttons: Кнопка под сообщением суммы корзины с ID {message_id} были удалены."
                )
            except telebot.apihelper.ApiTelegramException as e:
                print(
                    f"delete_buttons: Ошибка удаления кнопки у сообщения с суммой корзины: {message_id}: {e}"
                )
        return total_sum

    def show_delivery_options(self, chat_id):
        """
        Выводит в чат сообщение с клавиатурой для выбора способа получения заказа
        """
        total_sum = self.delete_buttons(chat_id)
        if total_sum > 0:
            msg = self.bot.send_message(
                chat_id,
                "Выберите способ получения заказа:",
                reply_markup=keyboards.generate_delivery_type_keyboard(),
            )
            self.user_states[chat_id]["chat_message_ids"] = []
            self.user_states[chat_id]["chat_message_ids"].append(msg.message_id)
        else:
            self.bot.send_message(
                chat_id, f"Сумма заказа = {total_sum}, оформить заказ невозможно!"
            )

    def handle_delivery_address(self, message):
        """
        Обрабатывает выбор пользователем доставки как способа получения заказа
        """
        chat_id = message.chat.id
        delivery_address = message.text
        self.user_states[chat_id] = self.user_states.get(chat_id, {})
        self.user_states[chat_id]["delivery_address"] = delivery_address
        print(
            f"handle_delivery_address called for chat_id: {chat_id}, address: {delivery_address}"
        )
        self.show_payment_options(message, DeliveryType.DELIVERY)

    def show_payment_options(self, message, delivery_type):
        """
        Выводит в чат сообщение с клавиатурой для выбора способа оплаты

        :param delivery_type: Description
        :type delivery_type: constant
        """
        chat_id = message.chat.id
        msg = self.bot.send_message(
            chat_id,
            "Выберите способ оплаты:",
            reply_markup=keyboards.generate_payment_type_keyboard(delivery_type),
        )
        self.user_states[chat_id]["chat_message_ids"].append(msg.message_id)

    def create_order(self, chat_id, delivery_type, delivery_address):
        """
        Создает заказ и записывает его в базу

        :param delivery_type: способ получения заказа
        :param delivery_address: адрес доставки или выбранного пункта выдачи
        """
        if not delivery_type or not delivery_address:
            self.bot.send_message(
                chat_id,
                "Параметры delivery_type и delivery_address были сброшены, произведите оформление заказа, заново открыв корзину",
            )
            self.logger.warning(
                f"Delivery parameters are missing or empty for user: {chat_id}"
            )
            return
        try:
            user = self.users.get(chat_id)
            if not user:
                self.logger.error(f"User not found for chat_id: {chat_id}")
                self.bot.send_message(
                    chat_id, "Произошла ошибка. Пожалуйста, попробуйте позже."
                )
                return
            new_order = user.create_order(delivery_type, delivery_address)
            self.logger.info(
                f"Order created for user {chat_id}, Order ID: {new_order.id}"
            )
            print(f"Заказ №{new_order.id} оформлен")
            self.bot.send_message(
                chat_id,
                f"Заказ №{new_order.id} оформлен! Спасибо за покупку!\nПосмотреть подробности можно в разделе 'Открытые заказы'",
                reply_markup=keyboards.generate_user_keyboard(),
            )
            self.delete_cart_messages_and_cart_is_empty(chat_id)
        except Exception as e:
            self.logger.exception(f"Error creating order for user {chat_id}: {e}")
            self.bot.send_message(
                chat_id,
                "Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.",
            )
            return

    def checkout_payment(self, query):
        """
        Обрабатывает запрос на подтверждение предварительной проверки оплаты.
        Принимает запрос от Telegram API и подтверждает его успешность,
        позволяя пользователю завершить процесс оплаты.

        :param query: Объект запроса на предварительную проверку оплаты.
        :type query: telegram.PreCheckoutQuery
        """
        self.bot.answer_pre_checkout_query(query.id, ok=True)

    def got_payment(self, message):
        """
        Обрабатывает сообщение о результате платежа.
        Проверяет, был ли платеж успешным, и уведомляет пользователя о результате.
        В случае успешной оплаты, вызывает метод для создания заказа.
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id, {})
        delivery_address = state_data.get("delivery_address")
        delivery_type = state_data.get("delivery_type")
        if message.successful_payment:
            self.logger.info(
                f"Successful payment received from user {chat_id}. Payload: {message.successful_payment.invoice_payload}"
            )
            print(message.successful_payment.invoice_payload)
            self.bot.send_message(chat_id, "Оплата произведена успешно!")
            if not delivery_type or not delivery_address:
                self.bot.send_message(
                    chat_id,
                    "Параметры delivery_type и delivery_address были сброшены, заказ не может быть оформлен, обратитесь к продавцу",
                )
                self.logger.warning(
                    f"Delivery parameters are missing or empty for user: {chat_id}"
                )
                return
            self.create_order(chat_id, delivery_type.value, delivery_address)
        else:
            print("Получено сообщение не типа 'successful_payment' (оплата не удалась)")
            self.logger.warning(f"Unsuccessful payment received from user {chat_id}")
            self.bot.send_message(
                chat_id,
                "К сожалению, оплата не прошла. Пожалуйста, попробуйте еще раз",
                reply_markup=keyboards.generate_payment_type_keyboard(delivery_type),
            )

    def making_a_payment(self, chat_id, prices, text):
        """
        Инициирует процесс оплаты для пользователя, отправляя счет.
        Отправляет пользователю счет на оплату через Telegram Payments API.

        :param prices: Список объектов цен (стоимостей) для оплаты.
        :type prices: list[telegram.LabeledPrice]
        :param text: Описание заказа, которое будет показано пользователю в счете на оплату.
        :type text: str
        """
        token = payment_token
        user = self.users.get(chat_id)
        state_data = self.user_states.get(chat_id, {})
        delivery_address = state_data.get("delivery_address")
        delivery_type = state_data.get("delivery_type")
        if not delivery_type or not delivery_address:
            self.bot.send_message(
                chat_id,
                "Параметры delivery_type и delivery_address были сброшены, произведите оформление заказа, заново открыв корзину",
            )
            self.logger.warning(
                f"Delivery parameters are missing or empty for user: {chat_id}"
            )
            return
        try:
            msg = self.bot.send_invoice(
                chat_id,
                title="Заказ",
                description=text,
                provider_token=token,
                currency="rub",
                prices=prices,
                invoice_payload=f"Платёж для пользователя {user.id} на сумму {user.calculate_total_sum()} ₽ проведен",
            )
            self.user_states[chat_id]["chat_message_ids"].append(
                msg.message_id
            )  # Добавляем в список сообщений
            self.logger.info(
                f"Successfully sent invoice to user {chat_id}. Message ID: {msg.message_id}"
            )
        except ApiException as e:  # Используем ApiException
            self.logger.error(f"Error sending invoice to user {chat_id}: {e}")
            self.bot.send_message(
                chat_id, "Произошла ошибка при формировании счета. Попробуйте позже."
            )
        except Exception as e:  # Ловим все остальные исключения
            self.logger.exception(
                f"Unexpected error in making_a_payment for user {chat_id}: {e}"
            )
            self.bot.send_message(
                chat_id,
                "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.",
            )

    def handle_callback(self, call):
        """
        Обрабатывает callback-запросы от Telegram при нажатии инлайн-кнопок.

        Разбирает callback-данные и выполняет соответствующие действия,
        связанные с добавлением, удалением и изменением товаров в корзине,
        а также переходом в корзину.

        :param call: Объект callback-запроса Telegram.
        :type call: telegram.CallbackQuery
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        message_id = call.message.message_id
        state_data = self.user_states.get(chat_id, {})
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(f"handle_callback called for chat_id: {chat_id}, state: {state_data}")
        data = callback_data.split(":")
        if data[1] == "add":
            print(
                f"handle_callback (add) called for chat_id: {chat_id}, state: {state_data}"
            )
            product_id = data[2]
            product = next((p for p in self.products if p.id == product_id), None)
            if product.is_active:
                user = self.users.get(chat_id)
                if user is None:
                    # Новый пользователь
                    user = User(chat_id)
                    print(f"Создали User {chat_id}")
                    self.users[chat_id] = user
                user.add_to_cart(product_id)
                print(f"Добавили товар {product_id} в корзину")
                self.bot.answer_callback_query(
                    call.id, text="Товар добавлен в корзину!"
                )
                # Создаем новые кнопки
                try:
                    self.bot.edit_message_reply_markup(
                        reply_markup=keyboards.generate_go_to_cart_keyboard(
                            product_id, 1
                        ),
                        chat_id=chat_id,
                        message_id=message_id,
                    )
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка редактирования сообщения товара в каталоге: {e}")
            else:
                self.bot.answer_callback_query(call.id, text="Товар снят с продажи")
        elif data[1] == "decrease":
            print(
                f"handle_callback (decrease) called for chat_id: {chat_id}, state: {state_data}"
            )
            product_id = data[2]
            user = self.users.get(chat_id)
            user.decrease_from_cart(product_id)
            number = user.cart[product_id]
            if number == 0:
                user.remove_from_cart(product_id)
                self.bot.edit_message_reply_markup(
                    reply_markup=keyboards.generate_add_to_cart_keyboard(product_id),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )
            else:
                self.bot.edit_message_reply_markup(
                    reply_markup=keyboards.generate_go_to_cart_keyboard(
                        product_id, number
                    ),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )
        elif data[1] == "increase":
            print(
                f"handle_callback (increase) called for chat_id: {chat_id}, state: {state_data}"
            )
            product_id = data[2]
            user = self.users.get(chat_id)
            user.add_to_cart(product_id)
            number = user.cart[product_id]
            self.bot.edit_message_reply_markup(
                reply_markup=keyboards.generate_go_to_cart_keyboard(product_id, number),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
        elif data[1] == "go_to_cart":
            print(
                f"handle_callback (cart) called for chat_id: {chat_id}, state: {state_data}"
            )
            self.show_cart(call.message, call)

    def handle_cart_callback(self, call):
        """
        Обрабатывает callback-запросы от Telegram при нажатии инлайн-кнопок под сообщениями с товарами корзины.

        Разбирает callback-данные и выполняет соответствующие действия,
        связанные с увеличением, уменьшением и удалением товаров из корзины,
        а также оформлением заказа и очисткой корзины.

        :param call: Объект callback-запроса Telegram.
        :type call: telegram.CallbackQuery
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        user = self.users.get(chat_id)
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_cart_callback called for chat_id: {chat_id}, state: {state_data}"
        )
        data = callback_data.split(":")
        if data[1] == "decrease":
            if sum(user.cart.values()) > 1:
                print(
                    f"handle_cart_callback (decrease) called for chat_id: {chat_id}, state: {state_data}"
                )
                product_id = data[2]
                user.decrease_from_cart(product_id)
                number = user.cart[product_id]
                if number > 0:
                    self.update_cart_item_message(call, product_id, number)
                else:
                    user.remove_from_cart(product_id)
                    message_id = self.user_states[chat_id]["cart_message_ids"].pop(
                        product_id, None
                    )
                    if message_id:
                        try:
                            self.bot.delete_message(call.message.chat.id, message_id)
                        except telebot.apihelper.ApiTelegramException as e:
                            print(f"Ошибка удаления сообщения: {e}")
                self.update_cart_sum_message(chat_id)
            else:
                user.cart = {}
                self.delete_cart_messages_and_cart_is_empty(chat_id)
        elif data[1] == "increase":
            print(
                f"handle_cart_callback (increase) called for chat_id: {chat_id}, state: {state_data}"
            )
            product_id = data[2]
            user.add_to_cart(product_id)
            number = user.cart[product_id]
            self.update_cart_item_message(call, product_id, number)
            self.update_cart_sum_message(chat_id)
        elif data[1] == "remove":
            if len(user.cart) > 1:
                print(
                    f"handle_cart_callback (remove) called for chat_id: {chat_id}, state: {state_data}"
                )
                product_id = data[2]
                user.remove_from_cart(product_id)
                message_id = self.user_states[chat_id]["cart_message_ids"].pop(
                    product_id, None
                )
                if message_id:
                    try:
                        self.bot.delete_message(call.message.chat.id, message_id)
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"Ошибка удаления сообщения: {e}")
                self.update_cart_sum_message(chat_id)
            else:
                user.cart = {}
                self.delete_cart_messages_and_cart_is_empty(chat_id)
        elif data[1] == "clear":
            print(
                f"handle_cart_callback (clear) called for chat_id: {chat_id}, state: {state_data}"
            )
            user.cart = {}
            self.delete_cart_messages_and_cart_is_empty(chat_id)
        elif data[1] == "add":
            print(
                f"handle_cart_callback (add) called for chat_id: {chat_id}, state: {state_data}"
            )
            self.show_delivery_options(chat_id)

    def handle_delivery_callback(self, call):
        """
        Обрабатывает выбор пользователем способа получения заказа, предлагая выбрать пункт выдачи из списка или написать адрес доставки
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_delivery_callback called for chat_id: {chat_id}, state: {state_data}"
        )
        data = callback_data.split(":")
        if data[1] == "pickup":
            message_text = "Выберите пункт выдачи:\n\n"
            for point in pickup_points:
                message_text += (
                    f"<b>{point['name']}</b>\n"
                    f"Адрес: {point['address']}\n"
                    f"Время работы: {point['working_hours']}\n\n"
                )
            msg = self.bot.send_message(
                chat_id,
                message_text,
                parse_mode="html",
                reply_markup=keyboards.generate_pickup_points_keyboard(pickup_points),
            )
        elif data[1] == "delivery":
            msg = self.bot.send_message(chat_id, "Введите адрес доставки:")
            self.bot.register_next_step_handler(
                call.message, self.handle_delivery_address
            )
        self.user_states[chat_id]["chat_message_ids"].append(msg.message_id)

    def handle_payment_callback(self, call):
        """
        Обрабатывает выбор пользователем способа оплаты, вызывая функцию создания заказа или функцию проведения онлайн-оплаты
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_payment_callback called for chat_id: {chat_id}, state: {state_data}"
        )
        data = callback_data.split(":")
        delivery_type_str = data[2]
        delivery_type = DeliveryType(delivery_type_str)
        self.user_states[chat_id]["delivery_type"] = delivery_type
        delivery_address = state_data.get("delivery_address")
        if data[1] == "on_delivery":
            if not delivery_type or not delivery_address:
                self.bot.send_message(
                    chat_id,
                    "Параметры delivery_type и delivery_address были сброшены, произведите оформление заказа, заново открыв корзину",
                )
                self.logger.warning(
                    f"Delivery parameters are missing or empty for user: {chat_id}"
                )
                return
            self.create_order(chat_id, delivery_type.value, delivery_address)
        elif data[1] == "online":
            user = self.users.get(chat_id)
            cart_items = user.get_cart_items()
            prices = []
            for item in cart_items:
                product = item["product"]
                quantity = item["quantity"]
                price_for_item = int(product.price * quantity * 100)  # Цена в копейках
                prices.append(
                    types.LabeledPrice(
                        label=f"{product.name} x {quantity}",  # Название товара и количество
                        amount=price_for_item,  # Цена для данной позиции
                    )
                )
            text = f"Способ получения: {delivery_type_str}, "
            if delivery_type == DeliveryType.DELIVERY:
                text += f"адрес доставки: {delivery_address}"
            else:
                text += f"адрес пункта самовывоза: {delivery_address}"
            self.making_a_payment(chat_id, prices, text)

    def handle_pickup_point_callback(self, call):
        """
        Обрабатывает выбор пользователем пункта выдачи, вызывая функцию выбора способа оплаты
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_pickup_point_callback called for chat_id: {chat_id}, state: {state_data}"
        )
        data = callback_data.split(":")
        pickup_point_id = data[1]
        pickup_point = next(
            (point for point in pickup_points if point["id"] == pickup_point_id), None
        )
        if not pickup_point:
            self.bot.send_message(chat_id, "Ошибка выбора пункта выдачи")
            return
        print(f"выбран пункт выдачи:{pickup_point["name"]}")
        self.user_states[chat_id]["delivery_address"] = pickup_point["address"]
        self.show_payment_options(call.message, DeliveryType.PICKUP)

    def handle_watch_products_callback(self, call):
        """
        Выводит товары заказа
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id, {})
        print(
            f"Callback query received from USER: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_watch_products_callback called for chat_id: {chat_id}, state: {state_data}"
        )
        data = callback_data.split(":")
        order_id = data[1]
        chat_id = call.message.chat.id
        order = self.get_order_by_id(chat_id, order_id)
        if order:
            items = get_order_items(order_id)  # Получаем товары по ID заказа
            if items:
                self.delete_catalog_messages(chat_id)
                self.delete_cart_messages_and_cart_is_not_empty(chat_id)
                for item in items:
                    product = next(
                        (p for p in self.products if p.id == item.product_id), None
                    )
                    if product:
                        self.send_product_info(chat_id, product)
                    else:
                        self.bot.send_message(
                            chat_id, f"Товар {item.name} не найден в базе!"
                        )
        else:
            print(f"Ошибка: Заказ с id {order_id} не найден для пользователя {chat_id}")
