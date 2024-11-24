from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import sqlite3

Base = declarative_base()
engine = create_engine('sqlite:///shop.db')
Session = sessionmaker(bind=engine)
session = Session()

class PhoneNumber(Base):
    __tablename__ = 'phone_number'
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=False, nullable=False)
    role = Column(String, unique=False, nullable=False)

Base.metadata.create_all(engine) 

# Пример добавления
# number = PhoneNumber(number='+79648589204', role = 'Admin')
# session.add(number)
# session.commit()

# item = session.query(PhoneNumber).filter_by(number="+79648589204").first()
# print(item.number, item.role)