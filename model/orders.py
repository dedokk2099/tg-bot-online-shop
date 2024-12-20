import datetime
import enum
from model.products import products
from model.items import Item, all_items


class OrderStatus(enum.Enum):
    PROCESSING = 'в обработке'
    ASSEMBLING = 'собирается'
    SHIPPED = 'передан в доставку'
    ARRIVED_PICKUP = 'прибыл в пункт выдачи'
    RECEIVED = 'получен'

class DeliveryType(enum.Enum):
    PICKUP = 'самовывоз'
    DELIVERY = 'доставка'

class Order:
    def __init__(self, customer_id, delivery_type, delivery_address):
        self.id = f"{customer_id}_{Order.generate_order_id(customer_id, orders_by_customer)}"
        self.status = OrderStatus.PROCESSING
        self.order_datetime = datetime.datetime.now()
        self.delivery_type = delivery_type
        self.delivery_address = delivery_address
        self.total_sum = self.calculate_total()
        self.customer_id = customer_id

    @staticmethod
    def generate_order_id(customer_id, orders_by_customer):
        return len(orders_by_customer.get(customer_id, [])) + 1

    def calculate_total(self):
        total = 0
        for item in all_items:
            if item.order_id == self.id:
                total += item.price * item.quantity
        return total

    def __repr__(self):
        return f"Order(id={self.id}, status={self.status}, total={self.total_sum})"

# Используем словарь для хранения заказов, индексированный по customer_id
orders_by_customer = {}

def add_new_order(customer_id, items, delivery_type, delivery_address):
    new_order = Order(customer_id, delivery_type, delivery_address)
    item_objects = []
    for item_data in items:
        product = item_data['product']
        quantity = item_data['quantity']
        item = Item(new_order.id, product.id, product.name, product.price, quantity) # Передаём order_id в Item
        item_objects.append(item)
        all_items.append(item)
    new_order.total_sum = new_order.calculate_total()
    if customer_id not in orders_by_customer:
        orders_by_customer[customer_id] = []
    orders_by_customer[customer_id].append(new_order)
    return new_order

def get_orders(customer_id=None, status=None):
    """Возвращает список заказов, отфильтрованный по customer_id и/или status."""
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

def get_order_items(order_id):
    order_items = [item for item in all_items if item.order_id == order_id]
    return order_items

#Пример использования
order_items1 = [
    {'product': products[0], 'quantity': 3}, 
    {'product': products[1], 'quantity': 2}
    ]
order_items2 = [{'product': products[0], 'quantity': 1}]
order_items3 = [{'product': products[2], 'quantity': 2}]
order_items4 = [
    {'product': products[1], 'quantity': 3}, 
    {'product': products[2], 'quantity': 2}
    ]

add_new_order('user123', order_items1, DeliveryType.PICKUP, "город Энск, на центральной площади")
add_new_order('user123', order_items2, DeliveryType.DELIVERY, "улица Пушкина, дом Колотушкина")
add_new_order('user456', order_items3, DeliveryType.PICKUP, "Мадагаскар, под пальмой")
add_new_order('user456', order_items4, DeliveryType.DELIVERY, "Антарктида, станция Мирный")

