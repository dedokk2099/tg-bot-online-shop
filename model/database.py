from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os,sys
import sqlite3

# sys.path.insert(1, '/path/to/model')
#import model.products as products
#import model.orders as orders
from model.products import Product
#from orders import Order

Base = declarative_base()
engine = create_engine('sqlite:///model/shop.db')
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)
    #cart = Column(JSON, default={}) # Храним корзину как JSON

    # связи
    # order_id = Column(Integer, ForeignKey('orders.id'))
    user_orders = relationship('Orders', back_populates='users')

class User:
    def __init__(self):
        self.Base = Base

    def _add_admin(self, chat_id):
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        session.delete(user)
        session.commit()
        user = Users(chat_id=chat_id, role = 'Admin')
        session.add(user)
        session.commit()
    
    def add_new(self, chat_id):
        user = Users(chat_id=chat_id, role = 'User')
        session.add(user)
        session.commit()

    def is_new(self, chat_id):
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user == None:
            return True
        else:
            return False

    def is_admin(self, chat_id):
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user.role == 'Admin':
            return True
        else:
            return False

class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, nullable=False) # добавление id предмета
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)

    # связи
    orders = relationship('Basket', back_populates='items')

class Basket(Base):
    __tablename__ = 'basket'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.number_order'), nullable=False)
    item_id = Column(Integer, ForeignKey('shop.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    #связи
    orders = relationship('Orders', back_populates='items')
    items = relationship('Shop', back_populates='orders')

# база данных заказов
class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.chat_id'), nullable=False)
    number_order = Column(Integer, unique=True, nullable=False)
    status = Column(String, nullable=False)
    total_sum = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    delivery_type = Column(String, nullable=False)
    
    # связи
    users = relationship('Users', back_populates='user_orders')
    items = relationship('Basket', back_populates='orders')

# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# функция добавления товара
def addItem(item_id, item_name, item_price, item_description, item_quantity, item_image):
    item = Shop(product_id = item_id, name=item_name, price=item_price, description=item_description, stock_quantity=item_quantity, image=item_image)
    session.add(item)
    session.commit()

# функция удаление товара
def deleteItem(item_id):
    item = session.query(Shop).filter_by(product_id = item_id).first()
    session.delete(item)
    session.commit()

# функция изменения названия товара
def updateItemAttribute(item_id, item_attribute, item_value):
    item = session.query(Shop).filter_by(product_id = item_id).first()
    if item_attribute == 'name':
        item.name = item_value
    elif item_attribute == 'price':
        item.price = item_value
    elif item_attribute =='description':
        item.description = item_value
    elif item_attribute == 'quantity':
        item.stock_quantity = item_value
    elif item_attribute == 'image':
        item.image = item_value

    #session.add(item)
    session.commit()

# функция добавления заказа
def addOrder(user_id, order_id, order_status, order_sum, delivery_type, order_datetime):
    order = Orders(user_id=user_id, number_order=order_id, status=order_status, total_sum=order_sum, datetime=order_datetime, delivery_type=delivery_type)
    session.add(order)
    session.commit()

# функция добавления в класс Basket
def addBasket(order_id, item_id, quantity, price):
    basket = Basket(order_id=order_id, item_id=item_id, quantity=quantity, price=price)
    session.add(basket)
    session.commit()

# функция вывода данных из класса Basket
def get_basket():
    basket_db = session.query(Basket).all()
    basket_list = []
    for basket in basket_db:
        basket_list.append({'id': basket.id, 'order_id': basket.order_id, 'item_id': basket.item_id, 'quantity': basket.quantity, 'price': basket.price})
    return basket_list
    # print(basket_list)

# функция вывода данных из класса Basket
# def get_products_by_order_number(order_number):
#     basket = session.query(Basket).filter(Basket.order_id == order_number).all()
#     products = session.query(Shop).join(Basket).filter(Basket.order_id == order_number).all()
#     products_list=[]
#     for item in products:
#         products_list.append({'id': item.product_id, "name": item.name, "price": item.price, "description": item.description, "stock_quantity": item.stock_quantity, 'image': item.image})
    
#     products_as_class = [Product(**data) for data in products_list]
#     items = []
#     i = 0
#     for item in products_as_class:       
#         items.append({'product': item, 'quantity':basket[i].quantity})
#         i = i + 1

#     return items

def get_products_by_order_number(order_number):
    items = []
    basket_items = session.query(Basket).filter(Basket.order_id==order_number).all()
    products = []
    for basket_item in basket_items:
        product = session.query(Shop).filter(Shop.product_id == basket_item.item_id).first()

        if product:
            items.append({
              'id': product.product_id,
              "name": product.name,
              "price": basket_item.price,
              "description": product.description,
              "stock_quantity": product.stock_quantity,
              'image': product.image
           })
        products.append({'product': Product(**items[-1]), 'quantity': basket_item.quantity})
    return products

# вывод данных из базы товаров в виде списка
def get_products():
    products_db = session.query(Shop).all()
    products_list = []
    for item in products_db:
        products_list.append({'id': item.product_id, "name": item.name, "price": item.price, "description": item.description, "stock_quantity": item.stock_quantity, 'image': item.image})
    # print(products_list)
    return products_list

# вывод данных из базы заказов в виде списка
# def get_orders():
#     orders_db = session.query(Orders).all()
#     orders_list = []
#     for order in orders_db:
#         items = get_products_by_order_number(order.number_order)
#         exist_order = Order(order.user_id, items, order.delivery_type, order.number_order)
#         orders_list.append(exist_order)
#     # print(orders_list)
#     return orders_list

# функция изменения статуса заказа
def change_status(number_order, order_status):
    order = session.query(Orders).filter_by(number_order=number_order).first()
    order.status = order_status
    session.commit()

# функция вывода заказов конкретного пользователя
def get_user_orders(user_id):
    #all_user_order = session.query(Orders, Users).join(Users).all()
    user_orders = session.query(Orders).filter_by(user_id=user_id).all()
    user_orders_list = []
    for order in user_orders:
        user_orders_list.append({'id': order.id, 'number_order': order.number_order, 'status': order.status, 'total_sum': order.total_sum, 'datetime': order.datetime})
    # print(user_orders_list)
    return user_orders_list

# функция вывода заказов конкретного пользователя по заданному статусу
def get_user_status_orders(user_id, order_status):
    user_orders = session.query(Orders).filter_by(user_id=user_id, status=order_status).all()
    user_orders_list = []
    for order in user_orders:
        user_orders_list.append({'id': order.id, 'number_order': order.number_order, 'total_sum': order.total_sum, 'datetime': order.datetime})
    # print(user_orders_list)
    return user_orders_list

# функция вывода заказов конкретного пользователя кроме конкретного статуса
def get_user_except_orders(user_id, order_status):
    user_orders = session.query(Orders).filter(Orders.user_id == user_id, Orders.status != order_status).all()
    user_orders_list = []
    for order in user_orders:
        user_orders_list.append({'id': order.id, 'number_order': order.number_order, 'total_sum': order.total_sum, 'datetime': order.datetime})
    # print(user_orders_list)
    return user_orders_list


# id = '2023435947' #вставьте необходимый
# user = session.query(Users).filter_by(chat_id=id).first()
# session.delete(user)
# session.commit()

# user = session.query(Shop).first()
# session.delete(user)
# session.commit()

# new_admin = Users(chat_id='884454010', role = 'Admin')
# session.add(new_admin)
# session.commit()

# addOrder(user, 113424, 'efefв', 1323, '3141432')
# addOrder(2023435948, 13451234, 'XFafwq', 35623, '1432')
# addOrder(user, 15675624, 'r fwwfe', 245324, '3141')

# addItem(122, 'Хлеб', 100, 'Свежий хлеб', 30, '')
# addItem(345, 'Молоко', 160, 'Птичье молоко', 7, '')
# addItem(555, 'Телефон', 1000, 'Айфон на андроид', 1, '')

# products = get_products()
# products_as_class = [Product(**data) for data in products]

# items = [
#     {'product': products_as_class[0], 'quantity': 3},
#     {'product': products_as_class[2], 'quantity': 1}
#     ]

# order = Order('2023435947', items, 'самовывоз')
# addOrder(order.customer_id, order.id, order.status.value, order.total_sum, order.delivery_type, order.order_datetime)
# addBasket(order.id, order.items[0]['product'].id, order.items[0]['quantity'], order.items[0]['product'].price)
# addBasket(order.id, order.items[1]['product'].id, order.items[1]['quantity'], order.items[1]['product'].price)
# addBasket(order.id, order.items[2]['product'].id, order.items[2]['quantity'], order.items[2]['product'].price)

# order = session.query(Orders).filter_by(number_order=113424).first()
# item = session.query(Shop).filter_by(product_id=555).first()
# basket = Basket(orders=order, items=item)
# session.add(basket)
# session.commit()

# basket = Basket(order_id=113424, item_id=345)
# session.add(basket)
# session.commit()
# basket = Basket(113424, 122)
# session.add(basket)
# session.commit()

# updateItemAttribute(122, 'image', 'https://avatars.mds.yandex.net/i?id=45760c598fc7066e3b979e0574d1f5c504e023c6-10414509-images-thumbs&n=13')
# updateItemAttribute(345, 'image', 'https://cdn-img.perekrestok.ru/i/800x800-fit/xdelivery/files/5f/0c/6c03e02b315c21a6d1daca6bb029.jpg')
# updateItemAttribute(555, 'image', 'https://avatars.mds.yandex.net/i?id=5920a940a44bbefcb98868342436b832_l-4292261-images-thumbs&n=13')
