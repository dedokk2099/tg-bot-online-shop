import io
import logging
import os
import uuid

# для экранирования html символов
from html import escape

import requests
import telebot
from PIL import Image

from model import database
from model.orders import DeliveryType, OrderStatus, get_order_items, get_orders
from model.products import add_new_product, get_products
from view import keyboards

PHOTO_FOLDER = "model/product_photos"
# Создаем папку для хранения фото, если ее нет
if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)


class AdminController:
    """
    Отвечает за работу бота в части администратора
    """

    def __init__(self, bot):
        """
        Инициализирует бот, состояния сообщения, заполняет соответствующие списки товаров и заказов из базы
        """
        self.bot = bot
        self.products = get_products()
        self.user_states = {}
        self.order_message_map = {}
        self.product_message_map = {}
        self.all_orders = get_orders()
        self.confirmation_message_id = None
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            encoding="utf-8",
        )

    # Функции для работы с каталогом

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
            self.bot.send_message(
                message.chat.id,
                "Добавить новый товар?",
                reply_markup=keyboards.generate_add_keyboard(),
            )
            return

        # if not self.products:
        #     self.bot.send_message(chat_id, "Каталог пуст")
        #     self.bot.send_message(message.chat.id, "Добавить новый товар?", reply_markup=keyboards.generate_add_keyboard())
        #     return

        # if message.chat.id not in self.user_states:
        self.user_states[message.chat.id] = {"state": 0}  # Начальное состояние
        if self.user_states[message.chat.id].get("state") == 0:
            for product in active_products:
                self.send_product_info(chat_id, product)
            self.bot.send_message(
                message.chat.id,
                "Добавить новый товар?",
                reply_markup=keyboards.generate_add_keyboard(),
            )
            return

    def send_product_info(self, chat_id, product):
        """ "
        Вызывает отображение информации о товаре в чате
        """
        if not product.is_active:
            # написать клавиатуру и функцию для возврата в активное состояние
            self.bot.send_message(
                chat_id,
                f"Название: {product.name}\nОписание: {product.description}\nПоследняя цена: {product.price} ₽\n\nТовар снят с продажи",
            )
            return

        text = f"<b>{product.name}</b>\nСтоимость: {product.price} ₽\nОписание: {product.description}\nКоличество на складе: {product.stock_quantity}"
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
                    reply_markup=keyboards.generate_product_keyboard(product),
                )
            else:
                msg = self.bot.send_message(
                    chat_id,
                    text,
                    parse_mode="HTML",
                    reply_markup=keyboards.generate_product_keyboard(product),
                )
            self.product_message_map[product.id] = msg.message_id
        except requests.exceptions.RequestException as e:
            self.bot.send_message(
                chat_id, f"Ошибка загрузки изображения для товара {product.name}: {e}"
            )
            self.bot.send_message(
                chat_id,
                text,
                parse_mode="HTML",
                reply_markup=keyboards.generate_product_keyboard(product),
            )
        except Exception as e:
            self.bot.send_message(
                chat_id,
                f"Ошибка при обработке изображения для товара {product.name}: {e}",
            )
            self.bot.send_message(
                chat_id,
                text,
                parse_mode="HTML",
                reply_markup=keyboards.generate_product_keyboard(product),
            )

    def translate_attribute(self, attribute_ru):
        """
        Возвращает имя переменной класса, соответствующее имени атрибута товара
        """
        translation = {
            "Название": "name",
            "Цена": "price",
            "Описание": "description",
            "Количество": "stock_quantity",
            "Изображение": "image",
        }
        return translation.get(attribute_ru)

    def update_attribute_value(self, message, product_id, attribute_ru, new_value):
        """ "
        Меняет значение атрибута товара в чате и в базе
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        product = next((p for p in self.products if p.id == product_id), None)
        if product is None:
            self.bot.send_message(chat_id, "Ошибка: Товар не найден.")
            return
        attribute_en = self.translate_attribute(attribute_ru)
        value = getattr(product, attribute_en)
        try:
            setattr(product, attribute_en, new_value)
        except AttributeError:
            print(f"Атрибут '{attribute_en}' не найден у продукта '{product.name}'")
            return
        if "attribute" in state_data:
            del state_data["attribute"]
        self.bot.send_message(
            chat_id,
            f"Атрибут '{attribute_ru}' изменён. Что ещё изменить?",
            reply_markup=keyboards.generate_edit_keyboard(),
        )

        # изменение атрибута товара в базе данных его названию и id
        database.updateItemAttribute(product_id, attribute_en, new_value)
        self.logger.info(
            f"Атрибут '{attribute_en}' товара '{product.name}' (ID: {product_id}) обновлен со значения {value} на значениe '{new_value}' by admin: {chat_id}"
        )
        self.bot.register_next_step_handler(message, self.handle_next_edit)

    def handle_cancel(self, message):
        """
        Обрабатывает команду отмены действия пользователя.

        Отправляет пользователю соответствующее сообщение в зависимости от текущего состояния.
        Если состояние равно 1 (редактирование атрибута), предлагает продолжить редактирование с помощью handle_edit_attribute.
        Если состояние равно 3 (добавление товара), отменяет добавление товара и сбрасывает состояние в 0.
        В остальных случаях отправляет общее сообщение об отмене действия.
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get("state") == 1:
            self.bot.send_message(chat_id, "Действие отменено. Что ещё изменить?")
            self.bot.register_next_step_handler(message, self.handle_edit_attribute)
        elif state_data and state_data.get("state") == 3:
            self.user_states[chat_id]["state"] = 0  # Reset state
            self.bot.send_message(chat_id, "Добавление товара отменено")
        else:
            self.bot.send_message(chat_id, "Дейсвие отменено")

    def handle_new_image(self, message):
        """
        Обрабатывает загрузку фото
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get("state") == 1:
            product_id = state_data.get("product_id")
            attribute_ru = state_data.get("attribute")
            if product_id is not None and attribute_ru is not None:
                try:
                    if message.photo:
                        file_id = message.photo[
                            -1
                        ].file_id  # получаем ID последней фотографии
                        file_info = self.bot.get_file(
                            file_id
                        )  # Получаем информацию о файле
                        file_path = file_info.file_path
                        image_bytes = self.bot.download_file(file_path)
                        filename = os.path.join(PHOTO_FOLDER, f"{uuid.uuid4().hex}.jpg")
                        with open(filename, "wb") as new_image:
                            new_image.write(image_bytes)
                        self.update_attribute_value(
                            message, product_id, attribute_ru, filename
                        )
                    elif message.text in ["/cancel", "Выход"]:
                        self.handle_cancel(message)
                    else:
                        self.bot.send_message(
                            chat_id,
                            "Пожалуйста, отправьте изображение.  Или нажмите /cancel для отмены.",
                        )
                        self.bot.register_next_step_handler(
                            message, self.handle_new_image
                        )  # Рекурсивный вызов
                except (KeyError, IndexError, AttributeError) as e:
                    self.bot.send_message(chat_id, f"Ошибка при обновлении товара: {e}")
            else:
                self.bot.send_message(chat_id, "Ошибка: Товар не выбран")

    def handle_attribute_value(self, message):
        """
        Обрабатывает входное значение для атрибута товара
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get("state") == 1:
            product_id = state_data.get("product_id")
            attribute_ru = state_data.get("attribute")
            if product_id is not None and attribute_ru is not None:
                if message.text in ["/cancel", "Выход"]:
                    self.handle_cancel(message)
                else:
                    try:
                        if attribute_ru in ["Цена", "Количество"]:
                            new_value = int(message.text)
                        else:
                            new_value = message.text
                        self.update_attribute_value(
                            message, product_id, attribute_ru, new_value
                        )
                    except ValueError:
                        self.bot.send_message(
                            chat_id, "Некорректный формат. Пожалуйста, введите число"
                        )
                        self.bot.register_next_step_handler(
                            message, self.handle_attribute_value
                        )  # Рекурсивный вызов
                    except (KeyError, IndexError, AttributeError) as e:
                        self.bot.send_message(
                            chat_id, f"Ошибка при обновлении товара: {e}"
                        )
            else:
                self.bot.send_message(chat_id, "Ошибка: Недостаточно данных.")
        else:
            self.bot.send_message(
                chat_id, "Ошибка: Нет текущего состояния редактирования."
            )

    def handle_edit_attribute(self, message):
        """
        Обрабатывает изменение атрибута товара
        """
        chat_id = message.chat.id
        print(
            f"handle_edit_attribute called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
        )
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get("state") == 1:
            if message.text == "Выход":
                if "product_id" in state_data:
                    product_id = state_data.get("product_id")
                    product = next(
                        (p for p in self.products if p.id == product_id), None
                    )
                    del state_data["product_id"]
                if "attribute" in state_data:
                    del state_data["attribute"]
                self.bot.send_message(
                    chat_id,
                    f"Редактирование товара {product.name} отменено",
                    reply_markup=keyboards.generate_admin_keyboard(),
                )
            else:
                product_id = state_data.get("product_id")
                if product_id is None:
                    self.bot.send_message(chat_id, "Ошибка: Товар не выбран")
                    return
                try:
                    product = next(
                        (p for p in self.products if p.id == product_id), None
                    )
                    if product is None:
                        self.bot.send_message(chat_id, "Ошибка: Товар не найден.")
                        return

                    attribute_ru = message.text
                    if attribute_ru in ["Название", "Цена", "Описание", "Количество"]:
                        self.user_states[chat_id]["attribute"] = attribute_ru
                        self.bot.send_message(
                            chat_id,
                            f"Введите новое значение '{attribute_ru}' для товара '{product.name}':",
                        )
                        self.bot.register_next_step_handler(
                            message, self.handle_attribute_value
                        )
                    elif attribute_ru == "Изображение":
                        self.user_states[chat_id]["attribute"] = attribute_ru
                        self.bot.send_message(
                            message.chat.id,
                            f"Отправьте новое изображение для товара '{product.name}':",
                        )
                        self.bot.register_next_step_handler(
                            message, self.handle_new_image
                        )  # вызов функции обработки изображения
                    else:
                        self.bot.send_message(chat_id, "Некорректный атрибут.")
                        self.bot.register_next_step_handler(
                            message, self.handle_edit_attribute
                        )

                except Exception as e:
                    self.bot.send_message(chat_id, f"Ошибка: {e}")
                    # self.user_states.pop(chat_id, None) #Очищаем состояние при ошибке

    def handle_next_edit(self, message):
        """
        Обрабатывает выбор администратора продолжать или выйти из редактирования товара
        """
        chat_id = message.chat.id
        state_data = self.user_states.get(chat_id)
        if state_data and state_data.get("state") == 1:
            try:
                if message.text == "Выход":
                    if "product_id" in state_data:
                        product_id = state_data.get("product_id")
                        product = next(
                            (p for p in self.products if p.id == product_id), None
                        )
                        del state_data["product_id"]
                    if "attribute" in state_data:
                        del state_data["attribute"]
                    self.bot.send_message(
                        chat_id, f"Редактирование товара {product.name} завершено"
                    )
                    self.bot.send_message(
                        chat_id,
                        "Обновляю каталог...",
                        reply_markup=keyboards.generate_admin_keyboard(),
                    )
                    self.show_catalog(message)
                else:
                    self.handle_edit_attribute(message)
            except Exception as e:
                self.bot.send_message(chat_id, f"Ошибка: {e}")
        else:
            self.bot.send_message(
                chat_id, "Ошибка: Нет текущего состояния редактирования."
            )

    def handle_add_product(self, message):
        """ "
        Обрабатывает ввод информации для нового товара
        """
        chat_id = message.chat.id
        print(
            f"handle_add_product called for chat_id: {chat_id}, state: {self.user_states.get(chat_id, {}).get('state')}"
        )
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {}
        if "name" not in self.user_states[chat_id]:
            self.user_states[chat_id]["name"] = message.text
            self.bot.send_message(chat_id, "Введите цену:")
            self.bot.register_next_step_handler(
                message, self.handle_add_product
            )  # Рекурсивный вызов для следующего шага
        elif "price" not in self.user_states[chat_id]:
            try:
                price = int(message.text)  # Проверка на число
                self.user_states[chat_id]["price"] = message.text
                self.bot.send_message(chat_id, "Введите описание:")
                self.bot.register_next_step_handler(
                    message, self.handle_add_product
                )  # Рекурсивный вызов
            except ValueError:
                self.bot.send_message(
                    chat_id,
                    "Некорректный формат цены. Пожалуйста, введите целое число.",
                )
                self.bot.register_next_step_handler(
                    message, self.handle_add_product
                )  # Рекурсивный вызов
        elif "description" not in self.user_states[chat_id]:
            self.user_states[chat_id]["description"] = message.text
            self.bot.send_message(chat_id, "Введите количество товара на складе:")
            self.bot.register_next_step_handler(message, self.handle_add_product)
        elif "stock_quantity" not in self.user_states[chat_id]:
            try:
                stock_quantity = int(message.text)  # Проверка на число
                self.user_states[chat_id]["stock_quantity"] = message.text
                self.bot.send_message(chat_id, "Теперь отправьте фото товара")
                print(
                    f"фото отправится сейчас for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
                )
                self.user_states[chat_id][
                    "state"
                ] = 3  # Переходим к шагу загрузки изображения
                print(
                    f"состояние изменено for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
                )
                self.bot.register_next_step_handler(message, self.handle_photo_upload)
            except ValueError:
                self.bot.send_message(
                    chat_id,
                    "Некорректный формат количества. Пожалуйста, введите целое число.",
                )
                self.bot.register_next_step_handler(
                    message, self.handle_add_product
                )  # Рекурсивный вызов

    def handle_photo_upload(self, message):
        """
        Обрабатывает отправку администратором фотографии.

        Если происходит добавление товара, записывает новый товар с полученным фото в базу,
        в противном случае сообщает об отсутствии необходимости в фото на данном шаге.
        """
        chat_id = message.chat.id
        print(
            f"handle_photo_upload called for chat_id: {chat_id}, state: {self.user_states.get(chat_id, {}).get('state')}"
        )
        # Получаем состояние пользователя
        user_state = self.user_states.get(chat_id)
        if not user_state or user_state.get("state") != 3:  # Проверяем состояние
            self.bot.send_message(chat_id, "Фото не требуется на этом шаге.")
            return
        try:
            if message.photo:
                # Скачиваем фото
                photo = message.photo[-1]
                file_info = self.bot.get_file(
                    photo.file_id
                )  # Получаем информацию о файле
                photo_path = os.path.join(PHOTO_FOLDER, f"{uuid.uuid4().hex}.jpg")

                # Загружаем файл и сохраняем его
                downloaded_file = self.bot.download_file(file_info.file_path)
                with open(photo_path, "wb") as new_file:
                    new_file.write(downloaded_file)
                try:
                    # Добавляем фото к новому товару
                    new_product = add_new_product(
                        user_state["name"],
                        user_state["price"],
                        user_state["description"],
                        user_state["stock_quantity"],
                        photo_path,
                        chat_id,
                    )
                    self.bot.send_message(chat_id, "Товар успешно добавлен:")
                    self.send_product_info(
                        chat_id,
                        next(
                            (p for p in self.products if p.id == new_product.id), None
                        ),
                    )
                    self.bot.send_message(
                        message.chat.id,
                        "Добавить новый товар или обновить каталог?",
                        reply_markup=keyboards.generate_add_or_update_keyboard(),
                    )
                    self.user_states[chat_id] = {"state": 0}
                except Exception as e:
                    self.bot.send_message(chat_id, f"Ошибка при добавлении товара: {e}")
            elif message.text == "/cancel":
                self.handle_cancel(message)
            else:
                self.bot.send_message(
                    chat_id,
                    "Пожалуйста, отправьте изображение.  Или нажмите /cancel для отмены.",
                )
                self.bot.register_next_step_handler(
                    message, self.handle_photo_upload
                )  # Рекурсивный вызов
        except Exception as e:
            self.bot.send_message(chat_id, f"Ошибка при загрузке фото: {e}")

    def handle_callback(self, call):
        """
        Обрабатывает callback-запросы от Telegram при нажатии инлайн-кнопок.

        Разбирает callback-данные и выполняет соответствующие действия,
        связанные с добавлением, удалением и изменением товаров в каталоге,
        изменением статуса заказа, а также переходом в каталог.

        :param call: Объект callback-запроса Telegram.
        :type call: telegram.CallbackQuery
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        print(
            f"Callback query received: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_callback called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
        )

        data = callback_data.split(":")

        if data[0] == "edit":
            print(
                f"handle_callback (edit) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            product_id = data[1]
            product_to_edit = next(
                (p for p in self.products if p.id == product_id), None
            )
            self.user_states[chat_id] = {"state": 1, "product_id": product_id}
            print(
                f"изменили состояние chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            msg = self.bot.send_message(
                chat_id,
                f"Редактируем товар {product_to_edit.name}\nСтоимость: {product_to_edit.price} ₽\nОписание: {product_to_edit.description}\nКоличество на складе: {product_to_edit.stock_quantity}\n\nЧто изменить?",
                reply_markup=keyboards.generate_edit_keyboard(),
            )
            self.bot.register_next_step_handler(msg, self.handle_edit_attribute)
        elif data[0] == "delete":
            print(
                f"handle_callback (delete) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            try:
                product_id = data[1]
                product_to_delete = next(
                    (p for p in self.products if p.id == product_id), None
                )
                if product_to_delete is None:
                    self.bot.answer_callback_query(call.id, text="Товар не найден!")
                    return
                product_name = product_to_delete.name
                msg = self.bot.send_message(
                    chat_id,
                    f"Вы подтверждаете удаление товара <b>{product_name}</b>?",
                    parse_mode="HTML",
                    reply_markup=keyboards.generate_delete_keyboard(product_id),
                )
                self.confirmation_message_id = msg.message_id
            except Exception as e:
                print(f"Ошибка при удалении товара: {e}")
                self.bot.answer_callback_query(
                    call.id, text="Ошибка при удалении товара."
                )
        elif data[0] == "confirm_delete":
            print(
                f"handle_callback (confirm_delet) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            product_id = data[1]
            product_to_delete = next(
                (p for p in self.products if p.id == product_id), None
            )
            if product_to_delete is None:
                self.bot.answer_callback_query(call.id, text="Товар не найден!")
                return
            product_name = product_to_delete.name
            product_to_delete.is_active = False
            # Деактивация товара в базе
            database.disactivateItem(product_id)
            self.logger.info(
                f"Deactivating product: {product_name} (ID: {product_id}) by admin: {chat_id}"
            )

            self.bot.edit_message_text(
                f"Товар {product_name} удален!", chat_id, self.confirmation_message_id
            )  # Редактируем сообщение с подтверждением
            self.bot.answer_callback_query(call.id, text="Товар удален!")
            try:
                message_id_to_delete = self.product_message_map.get(product_id)
                if message_id_to_delete is None:
                    self.bot.answer_callback_query(
                        call.id, text="Сообщение с товаром не найдено!"
                    )
                    return
                self.bot.delete_message(chat_id, message_id_to_delete)
                del self.product_message_map[product_id]
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Ошибка при удалении сообщения: {e}")
        elif data[0] == "cancel_delete":
            print(
                f"handle_callback (cancel_delete) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            self.bot.answer_callback_query(call.id, text="Удаление отменено")
            self.bot.edit_message_text(
                "Удаление отменено", chat_id, self.confirmation_message_id
            )  # Редактируем сообщение с подтверждением
        elif data[0] == "add":
            print(
                f"handle_callback (add) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            self.user_states[chat_id] = {"state": 2}  # Состояние добавления
            self.bot.send_message(chat_id, "Введите название товара:")
            self.bot.register_next_step_handler(call.message, self.handle_add_product)
        elif data[0] == "catalog":
            print(
                f"handle_callback (catalog) called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
            )
            self.bot.send_message(chat_id, "Обновляю каталог...")
            self.show_catalog(call.message)
        elif data[0] == "change_status":
            print(f"handle_callback (change_status) called for chat_id: {chat_id}")
            order_id = data[1]
            order = self.find_order_by_id(order_id)
            if order:
                text = f"Вы хотите изменить статус заказа <b>{order_id}</b>\nТекущий статус: <b>{order.status}</b>\nВыберите новый статус:"
                self.bot.send_message(
                    chat_id,
                    text,
                    parse_mode="html",
                    reply_markup=keyboards.generate_status_keyboard(
                        OrderStatus, order_id, order.status
                    ),
                )
            else:
                self.bot.answer_callback_query(
                    call.id, f"Заказ с ID {order_id} не найден", show_alert=True
                )

    # Функции для работы с заказами

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
            msg = self.bot.send_message(
                chat_id,
                text,
                parse_mode="html",
                reply_markup=keyboards.generate_change_status_keyboard(order),
            )
            self.order_message_map[order.id] = msg.message_id

    def show_new_orders(self, message):
        """
        Вызывает отображение новых заказов в чате
        """
        chat_id = message.chat.id
        new_orders = get_orders(status=OrderStatus.PROCESSING.value)
        if new_orders:
            for order in new_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "Нет новых заказов")

    def show_in_progress_orders(self, message):
        """
        Вызывает отображение  в чате заказов, принятых в работу
        """
        chat_id = message.chat.id
        self.all_orders = get_orders()
        in_progress_orders = [
            order
            for order in self.all_orders
            if order.status
            not in (OrderStatus.PROCESSING.value, OrderStatus.RECEIVED.value)
        ]
        if in_progress_orders:
            for order in in_progress_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "Нет заказов в работе")

    def show_completed_orders(self, message):
        """
        Вызывает отображение выполненных заказов в чате
        """
        chat_id = message.chat.id
        completed_orders = get_orders(status=OrderStatus.RECEIVED.value)
        if completed_orders:
            for order in completed_orders:
                self.send_order_info(order, chat_id)
        else:
            self.bot.send_message(chat_id, "Нет выполненных заказов")

    def find_order_by_id(self, order_id):
        """
        Производит поиск заказа по его номеру
        """
        self.all_orders = get_orders()
        for order in self.all_orders:
            if order.id == order_id:
                return order
        return None

    def handle_change_status(self, call):
        """
        Изменяет статус заказа в чате и в базе
        """
        chat_id = call.message.chat.id
        callback_data = call.data
        print(
            f"Callback query received: Chat ID: {chat_id} Callback Data: {callback_data}"
        )
        print(
            f"handle_change_status called for chat_id: {chat_id}, state: {self.user_states.get(chat_id)}"
        )
        try:
            new_status_name, order_id = call.data.split(":")[1:]
            new_status = OrderStatus[new_status_name]
            order = self.find_order_by_id(order_id)
            if order:
                order.status = new_status.value  # Обновление статуса заказа

                # вызов функции изменения статуса заказа
                database.change_status(order_id, new_status.value)
                self.logger.info(
                    f"Changing status of order {order_id} to {new_status.value} by admin: {chat_id}"
                )
                self.bot.send_message(
                    chat_id, f"Статус заказа {order_id} изменён на '{new_status.value}'"
                )
                user_id = order.customer_id
                if user_id:
                    # Отправляем уведомление пользователю
                    self.bot.send_message(
                        user_id,
                        f"Статус Вашего заказа {order_id} изменён на '{new_status.value}'",
                    )
                message_id_to_delete = self.order_message_map.get(
                    order_id
                )  # Извлекаем message_id из словаря по order_id
                if message_id_to_delete:
                    self.bot.delete_message(chat_id, message_id_to_delete)
                    self.bot.delete_message(chat_id, call.message.message_id)
            else:
                self.logger.warning(
                    f"Order with ID {order_id} not found for hanging status by admin: {chat_id}"
                )
                self.bot.answer_callback_query(
                    call.id, f"Заказ с ID {order_id} не найден", show_alert=True
                )
        except (IndexError, KeyError, ValueError) as e:
            self.logger.exception(f"Error handling callback while changing status: {e}")
            self.bot.answer_callback_query(call.id, f"Ошибка: {e}", show_alert=True)
