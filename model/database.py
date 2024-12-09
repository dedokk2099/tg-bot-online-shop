from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import sqlite3

import model.products as products

Base = declarative_base()
engine = create_engine('sqlite:///model/shop.db')
Session = sessionmaker(bind=engine)
session = Session()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)

Base.metadata.create_all(engine) 

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

def get_products():
    return products.products

# Пример добавления (с удалением по id, если пользователь уже в базе)

#id = 'xxx' #вставьте необходимый
# user = session.query(Users).filter_by(chat_id=id).first()
# session.delete(user)
# session.commit()

# new_admin = Users(chat_id=id, role = 'Admin')
# session.add(number)
# session.commit()
