import telebot
from telebot import types
from PIL import Image
import io
import requests
import os
import uuid

import products

PHOTO_FOLDER = 'product_photos'

# Создаем папку для хранения фото, если ее нет
if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

class AdminInterface:
    def __init__(self, bot):
        self.bot = bot
        self.register_handlers()
        self.products = products.products
        self.user_states = {}

    def setup_commands(self):
        self.bot.set_my_commands([
            telebot.BotCommand("/catalog", "Открыть каталог"),
            telebot.BotCommand("/new_orders", "Посмотреть новые аказы"),
            telebot.BotCommand("/in_progress", "Посмотреть заказы в работе"),
            telebot.BotCommand("/history", "Просмотреть историю заказов"),
        ])

    def generate_main_keyboard(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_catalog = types.KeyboardButton("Каталог")
        button_new_orders = types.KeyboardButton("Новые заказы")
        button_in_progress = types.KeyboardButton("В работе")
        button_history = types.KeyboardButton("История")
        markup.add(button_catalog, button_new_orders)
        markup.add(button_in_progress, button_history)
        return markup

    def reset_user_state(self, chat_id):
        if chat_id in self.user_states:
            self.user_states[chat_id] = {}
            print(f"State reset for chat_id: {chat_id}")

    def handle_catalog(self, message):
        # chat_id = message.chat.id
        # self.reset_user_state(chat_id)
        self.show_catalog(message)

    def handle_new_orders(self, message):
        self.bot.send_message(message.chat.id, "Список новых заказов:")

    def handle_in_progress(self, message):
        self.bot.send_message(message.chat.id, "Список заказов в работе:")

    def handle_history(self, message):
        self.bot.send_message(message.chat.id, "Список выполненных заказов:")

    def handle_unknown(self, message):
        self.bot.send_message(message.chat.id, "Неизвестная команда")

        
    def register_handlers(self):
        @self.bot.message_handler(commands=['catalog'])
        def handle_catalog_command(message):
            self.handle_catalog(message)

        @self.bot.message_handler(commands=['new_orders'])
        def handle_new_orders_command(message):
            self.handle_new_orders(message)

        @self.bot.message_handler(commands=['in_progress'])
        def handle_in_progress_command(message):
            self.handle_in_progress(message)

        @self.bot.message_handler(commands=['history'])
        def handle_history_command(message):
            self.handle_history(message)

        @self.bot.message_handler(func=lambda message: message.text in ["Каталог", "Новые заказы", "В работе", "История"])
        def handle_default(message):
            if message.text == "Каталог":
                self.handle_catalog(message)
            elif message.text == "Новые заказы":
                self.handle_new_orders(message)
            elif message.text == "В работе":
                self.handle_in_progress(message)
            elif message.text == "История":
                self.handle_history(message)
            else:
                self.handle_unknown(message)

        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            self.handle_photo_upload(message)


        #Пригодится позже

        # @self.bot.message_handler(func=lambda message: True)
        # def handle_all_messages(message):
        #     chat_id = message.chat.id

        #     if message.text == "Отказаться":
        #         bot_handler.handle_cancel(message)

        #     elif message.text == "Добавить без фото":
        #         bot_handler.handle_add_without_photo(message)

        #     elif message.text == "Загрузить фото":
        #         bot_handler.handle_photo_upload(message)

        #     elif message.text == "Назад":
        #         bot_handler.handle_cancel(message)

        #     else:
        #         if bot_handler.user_states.get(chat_id, {}).get("state") == 2:  # Состояние добавления товара
        #             bot_handler.handle_product_details(message)
        #         elif bot_handler.user_states.get(chat_id, {}).get("state") == 6:  # Состояние фото
        #             # Если пользователь выбрал фото или без фото
        #             if message.text == "Добавить без фото":
        #                 bot_handler.handle_add_without_photo(message)
        #             elif message.text == "Загрузить фото":
        #                 bot_handler.handle_photo_upload(message)
        #         elif bot_handler.user_states.get(chat_id, {}).get("state") == 7:  # Состояние загрузки фото
        #             bot_handler.handle_photo(message)

    #Пригодится позже
        
    def generate_edit_keyboard(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Название", "Цена", "Описание", "Количество", "Изображение", "Выход")
        return markup

    #Отображение каталога
    def show_catalog(self, message):
        chat_id = message.chat.id
        print(f"show_catalog called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        if not self.products:
            self.bot.send_message(chat_id, "Каталог пуст.")
            return

        # if message.chat.id not in self.user_states:
        self.user_states[message.chat.id] = {"state": 0}  # Начальное состояние
        if self.user_states[message.chat.id].get('state') == 0:
            for i, product in enumerate(self.products):
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton(f"Редактировать", callback_data=f"edit:{i}"),
                    types.InlineKeyboardButton(f"Удалить", callback_data=f"delete:{i}"),
                )
                text = f"<b>{product['name']}</b>\nСтоимость: {product['price']} ₽\nОписание: {product['description']}\nКоличество на складе: {product['quantity']}"
                
                try:
                    if product.get('image'):
                        # Проверяем, является ли image URL или локальным путем
                        if product['image'].startswith(('http://', 'https://')):
                            # Если это URL, загружаем изображение по ссылке
                            response = requests.get(product['image'], stream=True)
                            response.raise_for_status()  # Проверяем, что запрос успешен
                            image = Image.open(io.BytesIO(response.content))
                        else:
                            # Если это локальный файл, открываем его
                            with open(product['image'], 'rb') as file:
                                image = Image.open(file)
                                # Копируем изображение в буфер памяти
                                image_io = io.BytesIO()
                                image.save(image_io, format='JPEG')
                                image_io.seek(0)

                        # Уменьшаем размер изображения для экономии трафика
                        image.thumbnail((200, 200))
                        image_io = io.BytesIO()
                        image.save(image_io, format='JPEG')
                        image_io.seek(0)
                        self.bot.send_photo(chat_id, image_io, caption=text, parse_mode="HTML", reply_markup=markup)
                    else:
                        self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
                except requests.exceptions.RequestException as e:
                    self.bot.send_message(chat_id, f"Ошибка загрузки изображения для товара {product['name']}: {e}")
                    self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
                except Exception as e:
                    self.bot.send_message(chat_id, f"Ошибка при обработке изображения для товара {product['name']}: {e}")
                    self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

            # Кнопка "Добавить товар" после всех товаров
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
            self.bot.send_message(message.chat.id, "Добавить новый товар?", reply_markup=markup)
            return

    def translate_attribute(self, attribute_ru):
        translation = {
            'Название': 'name',
            'Цена': 'price',
            'Описание': 'description',
            'Количество': 'quantity'
        }
        return translation.get(attribute_ru)

    def handle_attribute_value(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            product_index = state_data.get('product_index')
            attribute_ru = state_data.get('attribute') 
            if product_index is not None and attribute_ru is not None:
                try:
                    attribute_en = self.translate_attribute(attribute_ru)
                    new_value = message.text
                    self.products[product_index][attribute_en] = new_value
                    self.bot.send_message(chat_id, "Атрибут изменён. Что ещё изменить?", reply_markup=self.generate_edit_keyboard())
                    self.bot.register_next_step_handler(message, self.handle_next_edit)
                    if 'attribute' in state_data:
                        del state_data['attribute']
                except (KeyError, IndexError, AttributeError) as e:
                    self.bot.send_message(chat_id, f"Ошибка при обновлении товара: {e}")
                    self.user_states.pop(chat_id, None)  # Очищаем состояние при ошибке
            else:
                self.bot.send_message(chat_id, "Ошибка: Недостаточно данных.")
        else:
            self.bot.send_message(chat_id, "Ошибка: Нет текущего состояния редактирования.")

    def handle_edit_attribute(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            product_index = state_data.get('product_index')
            if product_index is None:
                self.bot.send_message(chat_id, "Ошибка: Товар не выбран")
                return
            attribute_ru = message.text
            if attribute_ru in ['Название', 'Цена', 'Описание','Количество']:
                self.user_states[chat_id]['attribute'] = attribute_ru
                product_name = self.products[product_index].get('name')
                self.bot.send_message(chat_id, f"Введите новое значение {attribute_ru} для товара {product_name}:")
                self.bot.register_next_step_handler(message, self.handle_attribute_value)
            else:
                self.bot.send_message(chat_id, "Некорректный атрибут")
    
    def handle_next_edit(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            if message.text == "Выход":
                if 'product_index' in state_data:
                    product_name = self.products[state_data.get('product_index')].get('name')
                    del state_data['product_index']
                if 'attribute' in state_data:
                    del state_data['attribute']
                self.bot.send_message(chat_id, f"Редактирование товара {product_name} завершено", reply_markup=self.generate_main_keyboard())
                self.show_catalog(message)
            else:
                self.handle_edit_attribute(message)
        else:
            self.bot.send_message(chat_id, "Ошибка: Нет текущего состояния редактирования.")

    def handle_add_product(self, message):
        chat_id = message.chat.id
        print(f"add_product called for chat_id: {chat_id}, state: {self.user_states.get(chat_id, {}).get('state')}")
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {}
        if 'name' not in self.user_states[chat_id]:
            self.user_states[chat_id]['name'] = message.text
            self.bot.send_message(chat_id, "Введите цену:")
            self.bot.register_next_step_handler(message, self.handle_add_product) # Рекурсивный вызов для следующего шага
        elif 'price' not in self.user_states[chat_id]:
            try:
                price = float(message.text)  # Проверка на число
                self.user_states[chat_id]['price'] = message.text
                self.bot.send_message(chat_id, "Введите описание:")
                self.bot.register_next_step_handler(message, self.handle_add_product) # Рекурсивный вызов
            except ValueError:
                self.bot.send_message(chat_id, "Некорректный формат цены. Пожалуйста, введите число.")
                self.bot.register_next_step_handler(message, self.handle_add_product) # Рекурсивный вызов
        elif 'description' not in self.user_states[chat_id]:
                self.user_states[chat_id]['description'] = message.text
                self.bot.send_message(chat_id, "Введите количество товара на складе:")
                self.bot.register_next_step_handler(message, self.handle_add_product)
        elif 'quantity' not in self.user_states[chat_id]:
            try:
                quantity = float(message.text)  # Проверка на число
                self.user_states[chat_id]['quantity'] = message.text
                self.bot.send_message(chat_id, "Теперь отправьте фото товара")
                print(f"фото отправится сейчас for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
                self.user_states[chat_id]['state'] = 3  # Переходим к шагу загрузки изображения
                print(f"состояние изменено for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            except ValueError:
                self.bot.send_message(chat_id, "Некорректный формат количества. Пожалуйста, введите число.")
                self.bot.register_next_step_handler(message, self.handle_add_product)  # Рекурсивный вызов

    def handle_photo_upload(self, message):
        chat_id = message.chat.id
        # Получаем состояние пользователя
        user_state = self.user_states.get(chat_id)
        if not user_state or user_state.get('state') != 3:  # Проверяем состояние
            self.bot.send_message(chat_id, "Фото не требуется на этом шаге.")
            return

        try:
            # Скачиваем фото
            photo = message.photo[-1]
            file_info = self.bot.get_file(photo.file_id)  # Получаем информацию о файле
            photo_path = os.path.join(PHOTO_FOLDER, f"{uuid.uuid4().hex}.jpg")

            # Загружаем файл и сохраняем его
            downloaded_file = self.bot.download_file(file_info.file_path)
            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Добавляем фото к новому товару
            new_product = {
                'name': user_state['name'],
                'price': user_state['price'],
                'description': user_state['description'],
                'quantity': user_state['quantity'],
                'image': photo_path,  # Добавляем фото
            }

            self.products.append(new_product)
            self.bot.send_message(chat_id, "Товар успешно добавлен!")
            self.bot.send_message(chat_id, "Обновляю каталог...", reply_markup=types.ReplyKeyboardRemove())
            self.user_states[chat_id] = {'state': 0}
            self.show_catalog(message)
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при загрузке фото: {e}")

                
    def handle_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        state_data = self.user_states.get(chat_id)
        print(f"Callback query received: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        # if chat_id in self.user_states:
        #     self.user_states[chat_id] = {}  # Сбрасываем состояние
        #     # self.bot.send_message(chat_id, "Текущее действие прервано.")
        if chat_id not in self.user_states: #Проверка состояния
            return #Выход, если состояние не задано
        
        data = callback_data.split(":")

        if data[0] == "edit":
            product_index = int(data[1])
            self.user_states[chat_id] = {"state": 1, "product_index": product_index}
            print(f"handle_callback (edit) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            msg = self.bot.send_message(chat_id, "Что изменить?", reply_markup=self.generate_edit_keyboard())
            self.bot.register_next_step_handler(msg, self.handle_edit_attribute)
        elif data[0] == "delete":
            product_index = int(data[1])
            del self.products[product_index]
            self.bot.edit_message_text(f"Товар удален!", chat_id, call.message.message_id)  # Обновляем сообщение
        elif data[0] == "add":
            self.user_states[chat_id] = {"state": 2}  # Состояние добавления
            self.bot.send_message(chat_id, "Введите название товара:")
            self.bot.register_next_step_handler(call.message, self.handle_add_product)
    
        
    # Понадобится позже

    # def product_menu_keyboard(self):
    #     # Клавиатура для загрузки фото или добавления без фото
    #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     markup.add(
    #         types.KeyboardButton("Загрузить фото"),
    #         types.KeyboardButton("Добавить без фото")
    #     )
    #     return markup






    