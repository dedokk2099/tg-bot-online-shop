from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import sqlite3

import products

Base = declarative_base()
engine = create_engine('sqlite:///shop.db')
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)

class User:
    def __init__(self):
        self.Base = Base

    def _add_admin(self, chat_id):
        user = session.query(Users).filter_by(chat_id=chat_id).first()
        session.delete(user)
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
    quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)
 

# функция добавления товара
def addItem(item_id, item_name, item_price, item_description, item_quantity, item_image):
    item = Shop(product_id = item_id, name=item_name, price=item_price, description=item_description, quantity=item_quantity, image=item_image)
    session.add(item)
    session.commit()

# функция удаление товара
def deleteItem(item_id):
    item = session.query(Shop).filter_by(product_id = item_id).first()
    session.delete(item)
    session.commit()

# добавление товаров из products.py
#for i in range(len(products.products)):
#    addItem(products.products[i]['id'], products.products[i]['name'], products.products[i]['price'], products.products[i]#['description'], products.products[i]['quantity'], products.products[i]['image'])


# таблица ассоциаций
association_table = Table('order_user_association', Base.metadata, 
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('shop_id', Integer, ForeignKey('shop.id')),
    Column('order_id', Integer, ForeignKey('orders.id')),
)


# база данных заказов
class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    number_order = Column(Integer, nullable=False) # может и не понадобится
    status = Column(String, nullable=False) # new, in work, done    

    # ассоциации
    users = relationship('Users', secondary=association_table, back_populates='orders')
    shops = relationship('Shop', secondary=association_table, back_populates='orders')


# база данных истории заказов
class OrderHistory(Base):
    __tablename__ = 'order_history'
    id = Column(Integer, primary_key=True)

    # ассоциации
    users = relationship('Users', secondary=association_table, back_populates='order_history')
    orders = relationship('Orders', secondary=association_table, back_populates='order_history')
    shops = relationship('Shop', secondary=association_table, back_populates='order_history')


Base.metadata.create_all(engine)


# Пример добавления
#number = session.query(Users).filter_by(chat_id="2023435947").first()
# session.delete(number)
# session.commit()

# item = session.query(Users).filter_by(chat_id="2023435947").first()
# print(item.chat_id, item.role)
# print(item)