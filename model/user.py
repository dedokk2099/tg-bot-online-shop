from model.orders import add_new_order
from model.products import get_products


class User:
    """
    Представляет пользователя бота.

    Содержит информацию о пользователе, включая его идентификатор
    и корзину, а также методы для управления корзиной и создания
    заказа.

    :ivar id: Уникальный идентификатор пользователя
    :vartype id: int
    :ivar cart: Корзина пользователя, хранящая идентификаторы товаров и их количество
    :vartype cart: dict[str, int]
    """

    def __init__(self, user_id):
        self.id = user_id
        self.cart = (
            {}
        )  # {product_id: quantity} - Корзина пользователя, хранит ID товара и количество

    def add_to_cart(self, product_id):
        """
        Добавляет товар в корзину или увеличивает его количество

        :param product_id: Идентификатор товара
        :type product_id: str
        """
        self.cart[product_id] = (
            self.cart.get(product_id, 0) + 1
        )  # Добавляет товар в корзину или увеличивает количество

    def decrease_from_cart(self, product_id):
        """
        Уменьшает количество товара в корзине на 1

        :param product_id: Идентификатор товара
        :type product_id: str
        """
        if product_id in self.cart:
            self.cart[product_id] -= 1

    def remove_from_cart(self, product_id):
        """
        Удаляет товар из корзины

        :param product_id: Идентификатор товара
        :type product_id: str
        """
        if product_id in self.cart:
            del self.cart[product_id]

    def get_cart_items(self):
        """
        Возвращает список товаров в корзине.

        Получает все товары из корзины пользователя в виде списка
        словарей, каждый из которых содержит объект `Product` и его
        количество.

        :return: Список товаров в корзине
        :rtype: list[dict]
        """
        items = []
        products = [product for product in get_products() if product.is_active]
        for product_id, quantity in self.cart.items():
            product = next(
                (p for p in products if p.id == product_id), None
            )  # Находим продукт по ID
            if product:
                items.append(
                    {"product": product, "quantity": quantity}
                )  # Добавляем товар в список для заказа
        return items

    def calculate_total_sum(self):
        """
        Вычисляет общую сумму товаров в корзине

        :return: Общая сумма товаров в корзине
        :rtype: int
        """
        return sum(
            item["product"].price * item["quantity"] for item in self.get_cart_items()
        )

    def create_order(self, delivery_type, delivery_address):
        """
        Возвращает заказ, сформированный из корзины и очищает корзину

        :param delivery_type: Тип доставки.
        :type delivery_type: str
        :param delivery_address: Адрес доставки.
        :type delivery_address: str
        :return: Объект созданного заказа или `None`, если корзина пуста
        :rtype: Order or None
        """
        items = self.get_cart_items()
        if items:
            order = add_new_order(self.id, items, delivery_type, delivery_address)
            self.cart = {}  # Очищаем корзину после оформления заказа
            return order
        else:
            return None  # Корзина пуста
