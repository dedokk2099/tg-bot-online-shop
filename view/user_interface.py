import telebot
from telebot import types
from PIL import Image
import io
import requests
import os
import uuid

import model.products as products

PHOTO_FOLDER = 'product_photos'


class UserInterface:
    def __init__(self, bot):
        self.bot = bot
        self.register_handlers()
        self.products = products.products
        self.user_states = {}

    def setup_commands(self):
        self.bot.set_my_commands([
            telebot.BotCommand("/catalog", "Открыть каталог"),
            telebot.BotCommand("/my_orders", "Посмотреть заказы"),
            telebot.BotCommand("/cart", "Открыть корзину"),
        ])

    def generate_main_keyboard(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_catalog = types.KeyboardButton("Товары")
        button_my_orders = types.KeyboardButton("Мои заказы")
        button_cart = types.KeyboardButton("Корзина")
        markup.add(button_catalog, button_my_orders, button_cart)
        return markup

    def reset_user_state(self, chat_id):
        if chat_id in self.user_states:
            self.user_states[chat_id] = {}
            print(f"State reset for chat_id: {chat_id}")

    def handle_catalog(self, message):
        self.bot.send_message(message.chat.id, "Список товаров в каталоге:")

    def handle_my_orders(self, message):
        self.bot.send_message(message.chat.id, "Список заказов:")

    def handle_cart(self, message):
        self.bot.send_message(message.chat.id, "Список товаров в корзине:")

    def handle_unknown(self, message):
        self.bot.send_message(message.chat.id, "Неизвестная команда")

        
    def register_handlers(self):
        @self.bot.message_handler(commands=['catalog'])
        def handle_catalog_command(message):
            self.handle_catalog(message)

        @self.bot.message_handler(commands=['my_orders'])
        def handle_new_orders_command(message):
            self.handle_my_orders(message)

        @self.bot.message_handler(commands=['cart'])
        def handle_in_progress_command(message):
            self.handle_cart(message)

        @self.bot.message_handler(func=lambda message: message.text in ["Товары", "Мои заказы", "Корзина"])
        def handle_default(message):
            if message.text == "Товары":
                self.handle_catalog(message)
            elif message.text == "Мои заказы":
                self.handle_my_orders(message)
            elif message.text == "Корзина":
                self.handle_cart(message)
            else:
                self.handle_unknown(message)
