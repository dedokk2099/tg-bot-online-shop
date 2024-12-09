import view.keyboards as keyboards
import model.database as database
import telebot
from telebot import types
from PIL import Image
import io
import requests
import os
import uuid

PHOTO_FOLDER = 'product_photos'

class AdminController:
    def __init__(self, bot):
        self.bot = bot
        self.products = database.get_products()
        self.user_states = {}

    def generate_unique_id(self):
        while True:  # Гарантируем уникальность (хотя коллизия крайне маловероятна)
            new_id = str(uuid.uuid4())
            if new_id not in [product['id'] for product in self.products]:
                return new_id

    def show_catalog(self, message):
        chat_id = message.chat.id
        print(f"show_catalog called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        if not self.products:
            self.bot.send_message(chat_id, "Каталог пуст")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
            self.bot.send_message(message.chat.id, "Добавить новый товар?", reply_markup=markup)
            return

        # if message.chat.id not in self.user_states:
        self.user_states[message.chat.id] = {"state": 0}  # Начальное состояние
        if self.user_states[message.chat.id].get('state') == 0:
            for product in self.products:
                self.send_product_info(chat_id, product)
            # Кнопка "Добавить товар" после всех товаров
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
            self.bot.send_message(message.chat.id, "Добавить новый товар?", reply_markup=markup)
            return
        
    def send_product_info(self, chat_id, product):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit:{product['id']}"),
            telebot.types.InlineKeyboardButton(text="Удалить", callback_data=f"delete:{product['id']}"),
        )
        text = f"<b>{product['name']}</b>\nСтоимость: {product['price']} ₽\nОписание: {product['description']}\nКоличество на складе: {product['quantity']}"

        try:
            if product.get('image'):
                image_url_or_path = product['image']
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
                self.bot.send_photo(chat_id, image_io, caption=text, parse_mode="HTML", reply_markup=markup)
            else:
                self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        except requests.exceptions.RequestException as e:
            self.bot.send_message(chat_id, f"Ошибка загрузки изображения для товара {product['name']}: {e}")
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при обработке изображения для товара {product['name']}: {e}")
            self.bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    
    def translate_attribute(self, attribute_ru):
        translation = {
            'Название': 'name',
            'Цена': 'price',
            'Описание': 'description',
            'Количество': 'quantity',
            'Изображение': 'image'
        }
        return translation.get(attribute_ru)
    
    def handle_new_image(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            product_id = state_data.get('product_id')
            attribute_ru = state_data.get('attribute')
            if product_id is not None and attribute_ru is not None:
                try:
                    if message.photo:
                        # Обновляем информацию о товаре
                        product = next((p for p in self.products if p['id'] == product_id), None)
                        if product is None:
                            self.bot.send_message(chat_id, "Ошибка: Товар не найден.")
                            # self.user_states.pop(chat_id, None)
                            return
                        attribute_en = self.translate_attribute(attribute_ru)
                        file_id = message.photo[-1].file_id # получаем ID последней фотографии
                        file_info = self.bot.get_file(file_id)  # Получаем информацию о файле
                        file_path = file_info.file_path
                        image_bytes = self.bot.download_file(file_path)
                        filename = os.path.join(PHOTO_FOLDER, f"{uuid.uuid4().hex}.jpg")
                        with open(filename, 'wb') as new_image:
                            new_image.write(image_bytes)
                        product[attribute_en] = filename
                        self.bot.send_message(chat_id, "Изображение изменено! Что ещё изменить?", reply_markup=keyboards.generate_edit_keyboard())
                        self.bot.register_next_step_handler(message, self.handle_next_edit)
                        if 'attribute' in state_data:
                            del state_data['attribute']
                    else:
                        self.bot.send_message(chat_id, "Пожалуйста, отправьте изображение")
                        self.bot.register_next_step_handler(message, self.handle_new_image)  # Рекурсивный вызов
                except (KeyError, IndexError, AttributeError) as e:
                    self.bot.send_message(chat_id, f"Ошибка при обновлении товара: {e}")
                    # self.user_states.pop(chat_id, None) # Очищаем state
            else:
                self.bot.send_message(chat_id, "Ошибка: Товар не выбран")

    def handle_attribute_value(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            product_id = state_data.get('product_id')
            attribute_ru = state_data.get('attribute') 
            if product_id is not None and attribute_ru is not None:
                try:
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    if product is None:
                        self.bot.send_message(chat_id, "Ошибка: Товар не найден.")
                        # self.user_states.pop(chat_id, None)
                        return
                    attribute_en = self.translate_attribute(attribute_ru)
                    if attribute_en in ['price', 'quantity']:
                        float(message.text)
                    new_value = message.text
                    product[attribute_en] = new_value
                    self.bot.send_message(chat_id, f"Атрибут '{attribute_ru}' изменён. Что ещё изменить?", reply_markup=keyboards.generate_edit_keyboard())
                    self.bot.register_next_step_handler(message, self.handle_next_edit)
                    if 'attribute' in state_data:
                        del state_data['attribute']
                except ValueError:
                            self.bot.send_message(chat_id, "Некорректный формат. Пожалуйста, введите число")
                            self.bot.register_next_step_handler(message, self.handle_attribute_value) # Рекурсивный вызов
                except (KeyError, IndexError, AttributeError) as e:
                    self.bot.send_message(chat_id, f"Ошибка при обновлении товара: {e}")
                    # self.user_states.pop(chat_id, None)  # Очищаем состояние при ошибке
            else:
                self.bot.send_message(chat_id, "Ошибка: Недостаточно данных.")
        else:
            self.bot.send_message(chat_id, "Ошибка: Нет текущего состояния редактирования.")

    def handle_edit_attribute(self, message):
        chat_id = message.chat.id
        print(f"handle_edit_attribute called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            if message.text == "Выход":
                if 'product_id' in state_data:
                    product_id = state_data.get('product_id')
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    del state_data['product_id']
                if 'attribute' in state_data:
                    del state_data['attribute']
                self.bot.send_message(chat_id, f"Редактирование товара {product['name']} отменено", reply_markup=keyboards.generate_main_keyboard())
            else:
                product_id = state_data.get('product_id')
                if product_id is None:
                    self.bot.send_message(chat_id, "Ошибка: Товар не выбран")
                    return
                try:
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    if product is None:
                        self.bot.send_message(chat_id, "Ошибка: Товар не найден.")
                        # self.user_states.pop(chat_id, None) #Очищаем состояние при ошибке
                        return

                    attribute_ru = message.text
                    if attribute_ru in ['Название', 'Цена', 'Описание', 'Количество']:
                        self.user_states[chat_id]['attribute'] = attribute_ru
                        self.bot.send_message(chat_id, f"Введите новое значение '{attribute_ru}' для товара '{product['name']}':")
                        self.bot.register_next_step_handler(message, self.handle_attribute_value)
                    elif attribute_ru == "Изображение":
                        self.user_states[chat_id]['attribute'] = attribute_ru
                        self.bot.send_message(message.chat.id, f"Отправьте новое изображение для товара '{product['name']}':")
                        self.bot.register_next_step_handler(message, self.handle_new_image) # вызов функции обработки изображения
                    else:
                        self.bot.send_message(chat_id, "Некорректный атрибут.")
                        self.bot.register_next_step_handler(message, self.handle_edit_attribute)

                except Exception as e:
                    self.bot.send_message(chat_id, f"Ошибка: {e}")
                    # self.user_states.pop(chat_id, None) #Очищаем состояние при ошибке

    def handle_next_edit(self, message):
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get('state') == 1:
            if message.text == "Выход":
                if 'product_id' in state_data:
                    product_id = state_data.get('product_id')
                    product = next((p for p in self.products if p['id'] == product_id), None)
                    # product_name = self.products[state_data.get('product_id)].get('name')
                    del state_data['product_id']
                if 'attribute' in state_data:
                    del state_data['attribute']
                self.bot.send_message(chat_id, f"Редактирование товара {product['name']} завершено")
                self.bot.send_message(chat_id, "Обновляю каталог...", reply_markup=keyboards.generate_main_keyboard())
                self.show_catalog(message)
            else:
                self.handle_edit_attribute(message)
        else:
            self.bot.send_message(chat_id, "Ошибка: Нет текущего состояния редактирования.")

    def handle_add_product(self, message):
        chat_id = message.chat.id
        print(f"handle_add_product called for chat_id: {chat_id}, state: {self.user_states.get(chat_id, {}).get('state')}")
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
        print(f"handle_photo_upload called for chat_id: {chat_id}, state: {self.user_states.get(chat_id, {}).get('state')}")
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
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при загрузке фото: {e}")
        try:
            # Добавляем фото к новому товару
            new_product_id = self.generate_unique_id()
            new_product = {
                'id': new_product_id,
                'name': user_state['name'],
                'price': user_state['price'],
                'description': user_state['description'],
                'quantity': user_state['quantity'],
                'image': photo_path,  # Добавляем фото
            }

            self.products.append(new_product)
            self.bot.send_message(chat_id, "Товар успешно добавлен:")
            self.send_product_info(chat_id, next((p for p in self.products if p['id'] == new_product_id), None))
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
            markup.add(types.InlineKeyboardButton("Обновить каталог", callback_data="catalog"))
            self.bot.send_message(message.chat.id, "Добавить новый товар или обновить каталог?", reply_markup=markup)
            self.user_states[chat_id] = {'state': 0}
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при добавлении товара: {e}")

    def handle_callback(self, call):
        chat_id = call.message.chat.id
        callback_data = call.data
        # state_data = self.user_states.get(chat_id)
        state_data = self.user_states.get(chat_id, {})
        print(f"Callback query received: Chat ID: {chat_id} Callback Data: {callback_data}")
        print(f"handle_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")

        # if chat_id in self.user_states:
        #     self.user_states[chat_id] = {}  # Сбрасываем состояние
        #     # self.bot.send_message(chat_id, "Текущее действие прервано.")
        # if chat_id not in self.user_states: #Проверка состояния
        #     return #Выход, если состояние не задано
        


        data = callback_data.split(":")
    
        if data[0] == "edit":
            print(f"handle_callback (edit) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            # product_index = int(data[1])
            product_id = data[1]
            product_to_edit = next((p for p in self.products if p['id'] == product_id), None)
            self.user_states[chat_id] = {"state": 1, "product_id": product_id}
            print(f"изменили состояние chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            msg = self.bot.send_message(chat_id, f"Редактируем товар {product_to_edit['name']}\nСтоимость: {product_to_edit['price']} ₽\nОписание: {product_to_edit['description']}\nКоличество на складе: {product_to_edit['quantity']}\n\nЧто изменить?", reply_markup=keyboards.generate_edit_keyboard())
            self.bot.register_next_step_handler(msg, self.handle_edit_attribute)
        elif data[0] == "delete":
            print(f"handle_callback (delete) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}")
            try:
                product_id = data[1]
                product_to_delete = next((p for p in self.products if p['id'] == product_id), None)
                if product_to_delete is None:
                    self.bot.answer_callback_query(call.id, text="Товар не найден!")
                    return

                product_name = product_to_delete.get('name')
                self.products.remove(product_to_delete)  # Удаляем по значению
                print(f"Товар {product_name} удален!")

                try:
                    self.bot.delete_message(chat_id, call.message.message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Ошибка при удалении сообщения: {e}")
                    self.bot.answer_callback_query(call.id, text="Не удалось удалить сообщение.")
                    return

                self.bot.send_message(chat_id, f"Товар {product_name} удален!")
                self.bot.answer_callback_query(call.id, text="Товар удален!")

            except Exception as e:
                print(f"Ошибка при удалении товара: {e}")
                self.bot.answer_callback_query(call.id, text="Ошибка при удалении товара.")

        elif data[0] == "add":
            self.user_states[chat_id] = {"state": 2}  # Состояние добавления
            self.bot.send_message(chat_id, "Введите название товара:")
            self.bot.register_next_step_handler(call.message, self.handle_add_product)
        elif data[0] == "catalog":
            self.bot.send_message(chat_id, "Обновляю каталог...")
            self.show_catalog(call.message)

