from telebot import types

# Клавиатуры админа


def generate_admin_keyboard():
    """
    Генерирует клавиатуру для администратора.

    Создает клавиатуру с кнопками для навигации по админ-панели,
    включая кнопки для каталога, новых заказов, заказов в работе
    и истории.

    :return: Основная клавиатура администратора
    :rtype: telebot.types.ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_catalog = types.KeyboardButton("Каталог")
    button_new_orders = types.KeyboardButton("Новые заказы")
    button_in_progress = types.KeyboardButton("В работе")
    button_history = types.KeyboardButton("История")
    markup.add(button_catalog, button_new_orders)
    markup.add(button_in_progress, button_history)
    return markup


def generate_edit_keyboard():
    """
    Генерирует клавиатуру для редактирования товара.

    Создает клавиатуру с кнопками для редактирования полей товара:
    название, цена, описание, количество и изображение, а также кнопкой
    "Выход".

    :return: Клавиатура для редактирования товара
    :rtype: telebot.types.ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Название", "Цена", "Описание", "Количество", "Изображение", "Выход")
    return markup


def generate_add_keyboard():
    """
    Генерирует клавиатуру с инлайн-кнопкой для добавления товара.

    Создает инлайн-клавиатуру с одной кнопкой "Добавить товар",
    которая при нажатии вызывает callback-запрос.

    :return: Клавиатура добавления товара
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
    return markup


def generate_add_or_update_keyboard():
    """
    Генерирует клавиатуру с кнопками для добавления или обновления каталога.

    Создает инлайн-клавиатуру с двумя кнопками: "Добавить товар"
    и "Обновить каталог", которые при нажатии вызывают callback-запрос.

    :return: Клавиатура для добавления или обновления каталога
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Добавить товар", callback_data="add"))
    markup.add(types.InlineKeyboardButton("Обновить каталог", callback_data="catalog"))
    return markup


def generate_product_keyboard(product):
    """
    Генерирует клавиатуру для управления товаром.

    Создает инлайн-клавиатуру с кнопками "Редактировать" и "Удалить",
    которые при нажатии вызывают callback-запросы, содержащие идентификатор
    товара.

    :param product: Объект товара, для которого создается клавиатура
    :type product: model.product.Product
    :return: Клавиатуру для редактирования или удаления товара
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="Редактировать", callback_data=f"edit:{product.id}"
        ),
        types.InlineKeyboardButton(
            text="Удалить", callback_data=f"delete:{product.id}"
        ),
    )
    return markup


def generate_delete_keyboard(product_id):
    """
    Генерирует клавиатуру подтверждения удаления товара.

    Создает инлайн-клавиатуру с кнопками "Да" и "Нет" для подтверждения
    или отмены удаления товара, которые при нажатии вызывают callback-запросы,
    содержащие идентификатор товара или команду отмены.

    :param product_id: Идентификатор товара, для которого создается клавиатура
    :type product_id: str
    :return: Клавиатура подтверждения удаления товара
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Да", callback_data=f"confirm_delete:{product_id}"),
        types.InlineKeyboardButton("Нет", callback_data="cancel_delete"),
    )
    return markup


def generate_change_status_keyboard(order):
    """
    Генерирует клавиатуру для изменения статуса заказа.

    Создает инлайн-клавиатуру с кнопкой "Изменить статус",
    которая при нажатии вызывает callback-запрос, содержащий
    идентификатор заказа.

    :param order: Объект заказа, для которого создается клавиатура
    :type order: model.order.Order
    :return: Клавиатура для изменения статуса заказа
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Изменить статус", callback_data=f"change_status:{order.id}"
        )
    )
    return markup


def generate_status_keyboard(OrderStatus, order_id, order_status):
    """
    Генерирует клавиатуру выбора нового статуса заказа.

    Создает инлайн-клавиатуру с кнопками для каждого возможного
    статуса заказа, кроме текущего. Каждая кнопка вызывает
    callback-запрос, содержащий имя статуса и идентификатор
    заказа.

    :param order_id: Идентификатор заказа
    :type order_id: str
    :param order_status: Текущий статус заказа
    :type order_status: OrderStatus
    :return: Клавиатура выбора нового статуса заказа
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    for status in OrderStatus:
        if status == order_status:
            continue
        button = types.InlineKeyboardButton(
            text=status.value, callback_data=f"status:{status.name}:{order_id}"
        )
        markup.add(button)
    return markup


# Клавиатуры юзера


def generate_user_keyboard():
    """
    Генерирует клавиатуру для пользователя.

    Создает клавиатуру с кнопками для навигации по функционалу пользователя,
    включая кнопки для каталога, корзины, открытых заказов и истории заказов.

    :return: Основную клавиатуру пользователя
    :rtype: telebot.types.ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_catalog = types.KeyboardButton("Товары")
    button_cart = types.KeyboardButton("Корзина")
    button_open_orders = types.KeyboardButton("Открытые заказы")
    button_history = types.KeyboardButton("История заказов")
    markup.add(button_catalog, button_cart)
    markup.add(button_open_orders, button_history)
    return markup


def generate_add_to_cart_keyboard(product_id):
    """
    Генерирует клавиатуру для добавления товара в корзину.

    Создает инлайн-клавиатуру с одной кнопкой "Добавить в корзину",
    которая при нажатии вызывает callback-запрос, содержащий
    идентификатор товара.

    :param product_id: Идентификатор товара, для которого создается клавиатура.
    :type product_id: str
    :return: Клавиатура для добавления товара в корзину
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Добавить в корзину", callback_data=f"user:add:{product_id}"
        )
    )
    return markup


def generate_go_to_cart_keyboard(product_id, number):
    """
    Генерирует клавиатуру для управления товаром в каталоге.

    Создает инлайн-клавиатуру с кнопками "-" и "+" для уменьшения и
    увеличения количества товара, а также кнопкой "Перейти в корзину".
    Количество товара отображается между кнопками +/-.

    :param product_id: Идентификатор товара.
    :type product_id: str
    :param number: Текущее количество товара в корзине.
    :type number: int
    :return: Клавиатура для управления товаром в каталоге
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3  # Указываем ширину ряда в 3 кнопки
    markup.add(
        types.InlineKeyboardButton("-", callback_data=f"user:decrease:{product_id}"),
        types.InlineKeyboardButton(f"{number} шт.", callback_data="number"),
        types.InlineKeyboardButton("+", callback_data=f"user:increase:{product_id}"),
    )
    markup.add(
        types.InlineKeyboardButton("Перейти в корзину", callback_data="user:go_to_cart")
    )
    return markup


def generate_cart_item_keyboard(product_id, number):
    """
    Генерирует клавиатуру для управления товаром в корзине.

    Создает инлайн-клавиатуру с кнопками "-" и "+" для уменьшения и
    увеличения количества товара, а также кнопкой "Удалить из корзины".
    Количество товара отображается между кнопками +/-.

    :param product_id: Идентификатор товара.
    :type product_id: str
    :param number: Текущее количество товара в корзине.
    :type number: int
    :return: Клавиатура для управления товаром в корзине
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        types.InlineKeyboardButton("-", callback_data=f"cart:decrease:{product_id}"),
        types.InlineKeyboardButton(f"{number} шт.", callback_data="number"),
        types.InlineKeyboardButton("+", callback_data=f"cart:increase:{product_id}"),
    )
    markup.add(
        types.InlineKeyboardButton(
            "Удалить из корзины", callback_data=f"cart:remove:{product_id}"
        )
    )
    return markup


def generate_cart_keyboard():
    """
    Генерирует клавиатуру для управления корзиной.

    Создает инлайн-клавиатуру с кнопками "Очистить корзину"
    и "Оформить заказ", которые при нажатии вызывают callback-запросы.

    :return: Клавиатура для управления корзиной
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Очистить корзину", callback_data="cart:clear")
    )
    markup.add(types.InlineKeyboardButton("Оформить заказ", callback_data="cart:add"))
    return markup


def generate_watch_products_keyboard(order):
    """
    Генерирует клавиатуру для просмотра товаров в заказе.

    Создает инлайн-клавиатуру с кнопкой "Посмотреть товары",
    которая при нажатии вызывает callback-запрос, содержащий
    идентификатор заказа.

    :param order: Объект заказа, для которого создается клавиатура.
    :type order: model.order.Order
    :return: Клавиатуру для просмотра товаров в заказе
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Посмотреть товары", callback_data=f"watch:{order.id}"
        )
    )
    return markup


def generate_delivery_type_keyboard():
    """
    Генерирует клавиатуру выбора типа доставки.

    Создает инлайн-клавиатуру с кнопками "Самовывоз" и "Доставка",
    которые при нажатии вызывают callback-запросы.
    :return: Клавиатуру выбора типа доставки
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Самовывоз", callback_data="delivery:pickup"))
    markup.add(
        types.InlineKeyboardButton("Доставка", callback_data="delivery:delivery")
    )
    return markup


def generate_payment_type_keyboard(delivery_type):
    """
    Генерирует клавиатуру выбора способа оплаты.

    Создает инлайн-клавиатуру с кнопками "Онлайн" и "При получении",
    которые при нажатии вызывают callback-запросы, содержащие
    информацию о способе оплаты и типе доставки.

    :param delivery_type: Тип доставки, выбранный пользователем.
    :type delivery_type: model.order.DeliveryType
    :return: Клавиатуру выбора способа оплаты
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Онлайн", callback_data=f"payment:online:{delivery_type.value}"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "При получении", callback_data=f"payment:on_delivery:{delivery_type.value}"
        )
    )
    return markup


def generate_pickup_points_keyboard(pickup_points):
    """
    Генерирует клавиатуру для выбора пункта самовывоза.

    Создает инлайн-клавиатуру с кнопками для каждого пункта
    самовывоза, которые при нажатии вызывают callback-запросы,
    содержащие идентификатор пункта.

    :param pickup_points: Список словарей с информацией о пунктах самовывоза.
    :type pickup_points: list[dict]
    :return: Клавиатуру выбора пункта самовывоза
    :rtype: telebot.types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup()
    for point in pickup_points:
        markup.add(
            types.InlineKeyboardButton(
                point["name"], callback_data=f"pickup_point:{point['id']}"
            )
        )
    return markup
