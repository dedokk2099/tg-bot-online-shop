from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import sqlite3

Base = declarative_base()
engine = create_engine('sqlite:///shop.db')
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


# Пример добавления
#number = session.query(Users).filter_by(chat_id="2023435947").first()
# session.delete(number)
# session.commit()

# item = session.query(Users).filter_by(chat_id="2023435947").first()
# print(item.chat_id, item.role)
# print(item)