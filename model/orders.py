import datetime
import enum, sys
#sys.path.insert(1, '/path/to/model')
#from model.products import products_as_class
import model.database as database

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
    def __init__(self, customer_id, items, delivery_type, order_number = None, status = None, date_time = None):
        if order_number == None:
            self.id = f"{customer_id}_{Order.generate_order_id(customer_id, orders_by_customer)}"
        else:
            self.id = order_number
        
        if status == None:
            self.status = OrderStatus.PROCESSING.value
        else:
            self.status = status
        
        if date_time == None:
            self.order_datetime = datetime.datetime.now()
        else:
            self.order_datetime = date_time

        self.delivery_type = delivery_type
        self.items = items
        self.total_sum = self.calculate_total()
        self.customer_id = customer_id

    # def __init__(self, customer_id, items, delivery_type, order_number):
    #     self.id = order_number
    #     self.status = OrderStatus.PROCESSING
    #     self.order_datetime = datetime.datetime.now()
    #     self.delivery_type = delivery_type
    #     self.items = items
    #     self.total_sum = self.calculate_total()
    #     self.customer_id = customer_id

    @staticmethod
    def generate_order_id(customer_id, orders_by_customer):
        return len(orders_by_customer.get(customer_id, [])) + 1

    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item['quantity'] * item['product'].price
        return total

    def __repr__(self):
        return f"Order(id={self.id}, status={self.status}, total={self.total_sum})"

# Используем словарь для хранения заказов, индексированный по customer_id
orders_by_customer = {}

def fill_orders_by_customer():
    orders = get_base_orders()
    for order in orders:
        if order.customer_id not in orders_by_customer:
            orders_by_customer[order.customer_id] = []
        orders_by_customer[order.customer_id].append(order)

def add_new_order(customer_id, items, delivery_type):
    
    new_order = Order(customer_id, items, delivery_type)
    #database.addOrder(customer_id, new_order.id, new_order.status, new_order.total_sum, delivery_type,new_order.order_datetime)
    #for item in range(len(items)):
    #    database.addBasket(new_order.id, items[item]['item_id'], items[item]['quantity'], items[item]['price'])
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

def get_base_orders():
    orders_db = database.session.query(database.Orders).all()
    orders_list = []
    for order in orders_db:
        items = database.get_products_by_order_number(order.number_order)
        exist_order = Order(order.user_id, items, order.delivery_type, order.number_order, order.status, order.datetime)
        orders_list.append(exist_order)
    print(orders_list)
    return orders_list

#Пример использования
# order_items1 = [
#     {'product': products_as_class[0], 'quantity': 3}, 
#     {'product': products_as_class[1], 'quantity': 2}
#     ]
# order_items2 = [{'product': products_as_class[0], 'quantity': 1}]
# order_items3 = [{'product': products_as_class[2], 'quantity': 2}]
# order_items4 = [
#     {'product': products_as_class[1], 'quantity': 3}, 
#     {'product': products_as_class[2], 'quantity': 2}
#     ]


#add_new_order('user123', order_items1, DeliveryType.PICKUP)
#add_new_order('user123', order_items2, DeliveryType.DELIVERY)
#add_new_order('user456', order_items3, DeliveryType.PICKUP)
#add_new_order('user456', order_items4, DeliveryType.DELIVERY)

# for customer_id, orders in orders_by_customer.items():
#     print(f"Заказы клиента {customer_id}:")
#     for order in orders:
#         print(f"  - ID: {order.id}, Статус: {order.status.value}, Сумма: {order.total_sum}")
#     print()

# fill_orders_by_customer()
# ord = get_orders()
# print(ord)

#order = database.session.query(database.Orders).filter_by(user_id='2023435947').first()

# products = database.get_products()
# products_as_class = [database.Product(**data) for data in products]

# items = [
#     {'product': products_as_class[2], 'quantity': 2},
#     {'product': products_as_class[1], 'quantity': 2},
#     {'product': products_as_class[0], 'quantity': 5}
#     ]

# order = Order('884454010', items, 'самовывоз')
# database.addOrder(order.customer_id, order.id, order.status, order.total_sum, order.delivery_type, order.order_datetime)
# database.addBasket(order.id, order.items[0]['product'].id, order.items[0]['quantity'], order.items[0]['product'].price)
# database.addBasket(order.id, order.items[1]['product'].id, order.items[1]['quantity'], order.items[1]['product'].price)
# database.addBasket(order.id, order.items[2]['product'].id, order.items[2]['quantity'], order.items[2]['product'].price)