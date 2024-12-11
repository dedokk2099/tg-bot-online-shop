from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, se
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os,sys
import sqlite3

sys.path.insert(1, '/path/to/model')

import products as products
import orders as orders

Base = declarative_base()
engine = create_engine('sqlite:///model/shop.db')
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)

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
    product_id = Column(String, nullable=False) # добавление id предмета
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)

# база данных заказов
class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    number_order = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    total_sum = Column(Integer, nullable=False)
    datetime = Column(String, nullable=False)
    
    # связи
    users = relationship('Users', back_populates='user_orders')

# Base.metadata.create_all(engine)

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
        item.stock_quantityy = item_value
    elif item_attribute == 'image':
        item.image = item_value

    #session.add(item)
    session.commit()

# функция добавления заказа
def addOrder(order_user, order_id, order_status, order_sum, order_datetime):
    order = Orders(users=order_user, number_order=order_id, status=order_status, total_sum=order_sum, datetime=order_datetime, )
    session.add(order)
    session.commit()

# добавление товаров из products.py
# for i in range(len(products.products)):
#    addItem(products.products[i]['id'], products.products[i]['name'], products.products[i]['price'], products.products[i]# ['description'], products.products[i]['stock_quantity'], products.products[i]['image'])


# вывод данных из базы товаров в виде списка
def get_products():
    products_list = session.query(Shop).all()
    print(product_list)

# вывод данных из базы заказов в виде списка
def get_orders():
    orders_list = session.query(Orders).all()
    print(orders_list)

get_products()

# Пример добавления (с удалением по id, если пользователь уже в базе)

#id = 'xxx' #вставьте необходимый
# user = session.query(Users).filter_by(chat_id=id).first()
# session.delete(user)
# session.commit()

# new_admin = Users(chat_id=id, role = 'Admin')
# session.add(number)
# session.commit()