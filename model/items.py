class Item:
    """
    Представляет собой товар в заказе.

    :ivar order_id: Идентификатор заказа, к которому относится товар.
    :vartype order_id: int
    :ivar product_id: Идентификатор товара
    :vartype product_id: str
    :ivar name: Наименование товара
    :vartype name: str
    :ivar price: Цена товара за единицу
    :vartype price: int
    :ivar quantity: Количество товара в заказе
    :vartype quantity: int
    """
    def __init__(self, order_id, product_id, name, price, quantity):
        self.order_id = order_id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

        def __repr__(self):
            return f"Item(order_id={self.order_id}, product_id={self.product_id}, name='{self.name}', price={self.price}, quantity={self.quantity})"

all_items = []
"""
Список словарей наборов товаров для всех созданных заказов

:type: list[Item]
"""