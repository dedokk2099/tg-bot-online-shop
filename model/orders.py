import datetime
import enum
from model.items import Item, all_items
from model import database


class OrderStatus(enum.Enum):
    """
    Представляет возможные статусы заказа.
    Каждый статус является строковым значением, описывающим текущее
    состояние заказа
    """

    PROCESSING = "в обработке"
    ASSEMBLING = "собирается"
    SHIPPED = "передан в доставку"
    ARRIVED_PICKUP = "прибыл в пункт выдачи"
    RECEIVED = "получен"


class DeliveryType(enum.Enum):
    """
    Представляет возможные типы доставки.
    Каждый тип доставки является строковым значением, описывающим
    способ доставки заказа.
    """

    PICKUP = "самовывоз"
    DELIVERY = "доставка"


class Order:
    """
    Используется для хранения данных о заказе во время работы бота

    :ivar id: Идентификатор заказа
    :vartype id: str
    :ivar status: Статус заказа
    :vartype status: str
    :ivar order_datetime: Дата и время создания заказа
    :vartype order_datetime: datetime.datetime
    :ivar total_sum: Общая сумма заказа
    :vartype total_sum: int
    :ivar delivery_address: Адрес доставки или пункта выдачи
    :vartype delivery_address: str
    :ivar delivery_type: Тип получения заказа
    :vartype delivery_type: str
    :ivar customer_id: Идентификатор пользователя, сделавшего заказ
    :vartype customer_id: int
    """

    def __init__(
        self,
        customer_id,
        delivery_type,
        delivery_address,
        order_number=None,
        status=None,
        date_time=None,
        total_sum=None,
    ):
        """
        Инициализирует новый объект Order. Записывает атрибуты заказа в поля класса.
        При создании нового заказа часть атрибутов генерируются при помощи методов.
        """
        if order_number is None:
            self.id = f"{customer_id}_{Order.generate_order_id(customer_id, orders_by_customer)}"
        else:
            self.id = order_number

        if status is None:
            self.status = OrderStatus.PROCESSING.value
        else:
            self.status = status

        if date_time is None:
            self.order_datetime = datetime.datetime.now()
        else:
            self.order_datetime = date_time

        if total_sum is None:
            self.total_sum = self.calculate_total()
        else:
            self.total_sum = total_sum

        self.delivery_address = delivery_address
        self.delivery_type = delivery_type
        self.customer_id = customer_id

    @staticmethod
    def generate_order_id(customer_id, orders_by_customer):
        """
        Генерирует порядковую часть номера заказа

        :param customer_id: Идентификатор пользователя
        :type customer_id:
        :param orders_by_customer: Словарь заказов, сгруппированных по идентификатору пользователя
        :type orders_by_customer:
        :return: Порядковая часть номера заказа
        :rtype: int
        """
        return len(orders_by_customer.get(customer_id, [])) + 1

    def calculate_total(self):
        """
        Вычисляет сумму заказа

        :return: Общая стоимость заказа
        :rtype: int
        """
        total = 0
        for item in all_items:
            if item.order_id == self.id:
                total += item.price * item.quantity
        return total

    def __repr__(self):
        return f"Order(id={self.id}, status={self.status}, total={self.total_sum})"


# Используем словарь для хранения заказов, индексированный по customer_id
orders_by_customer = {}
"""
Словарь для хранения заказов, индексированный по идентификатору пользователя

:type: dict[int, list[Order]]
"""


def fill_orders_by_customer():
    """
    Заполняет orders_by_customer заказами из базы
    """
    orders = get_base_orders()
    for order in orders:
        if order.customer_id not in orders_by_customer:
            orders_by_customer[order.customer_id] = []
        orders_by_customer[order.customer_id].append(order)


def fill_all_items():
    """
    Заполняет список all_items товарами из базы
    """
    items = database.get_basket()
    if items is not None:
        for item in items:
            all_items.append(Item(**item))


def add_new_order(customer_id, items, delivery_type, delivery_address):
    """
    Создает новый заказ на основе предоставленных данных, добавляет товары
    в заказ, а также обновляет базу данных

    :param customer_id: Идентификатор пользователя, делающего заказ
    :type customer_id: int
    :param items: Список словарей, каждый из которых содержит информацию о товаре ('product' и 'quantity')
    :type items: list[dict]
    :param delivery_type: Тип получения заказа
    :type delivery_type: str
    :param delivery_address: Адрес доставки или пункта выдачи
    :type delivery_address: str
    :return: Объект созданного заказа
    :rtype: Order
    """
    new_order = Order(customer_id, delivery_type, delivery_address)

    item_objects = []
    for item_data in items:
        product = item_data["product"]
        quantity = item_data["quantity"]
        item = Item(
            new_order.id, product.id, product.name, product.price, quantity
        )  # Передаём order_id в Item
        database.addBasket(
            new_order.id, product.id, product.name, quantity, product.price
        )
        item_objects.append(item)
        all_items.append(item)
    new_order.total_sum = new_order.calculate_total()
    database.addOrder(
        new_order.customer_id,
        new_order.id,
        new_order.status,
        new_order.total_sum,
        new_order.delivery_type,
        new_order.order_datetime,
        new_order.delivery_address,
    )
    if customer_id not in orders_by_customer:
        orders_by_customer[customer_id] = []
    orders_by_customer[customer_id].append(new_order)
    return new_order


def get_orders(customer_id=None, status=None):
    """
    Возвращает список заказов, отфильтрованный по customer_id и/или status.

    Возвращает список объектов Order, отфильтрованный по идентификатору пользователя
    и/или статусу заказа, если они предоставлены. Возвращает все заказы, если
    параметры фильтрации не указаны.

    :param customer_id: Идентификатор пользователя для фильтрации заказов (опционально)
    :type customer_id: int, optional
    :param status: Статус заказа для фильтрации (опционально)
    :type status: str, optional
    :return: Список отфильтрованных заказов
    :rtype: list[Order]
    """
    orders = []
    for customer_orders in orders_by_customer.values():
        for order in customer_orders:
            if customer_id is not None and order.customer_id != customer_id:
                continue
            if status is not None and order.status != status:
                continue
            orders.append(order)
    orders.sort(key=lambda order: order.order_datetime, reverse=True)
    return orders


def get_base_orders():
    """
    Возвращает список заказов из базы данных

    Запрашивает все заказы из базы данных и преобразует их
    в объекты `Order`, которые затем добавляются в список.
    Список заказов затем возвращается.

    :return: Список объектов `Order` из базы данных
    :rtype: list[Order]
    """
    orders_db = database.session.query(database.Orders).all()
    orders_list = []
    for order in orders_db:
        exist_order = Order(
            order.user_id,
            order.delivery_type,
            order.delivery_address,
            order.number_order,
            order.status,
            order.datetime,
            order.total_sum,
        )
        orders_list.append(exist_order)
    # print(orders_list)
    return orders_list


def get_order_items(order_id):
    """
    Возвращает список товаров конкретного заказа

    Извлекает из общего списка `all_items` все товары,
    которые принадлежат заказу с указанным идентификатором.

    :param order_id: Идентификатор заказа
    :type order_id: str
    :return: Список товаров, принадлежащих заказу
    :rtype: list[Item]
    """
    order_items = [item for item in all_items if item.order_id == order_id]
    return order_items
