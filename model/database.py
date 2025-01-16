from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os,sys
import sqlite3

# Создается базовая модель для записи данных в базу sql
Base = declarative_base()

#Подлежит комментированию, написано для создания документации

def get_engine():
  # Путь к БД - переменная окружения или файл в data
  db_path = os.getenv("DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shop.db')))
  return create_engine(f'sqlite:///{db_path}')


# Запускается база
#Подлежит комментированию
engine = get_engine()
#Подлежит раскомментированию
# engine = create_engine('sqlite:///model/shop.db')
# Активируется сессия для взаимодействия с базой
Session = sessionmaker(bind=engine)
session = Session()




class Users(Base):
    """
    Модель для записи данных пользователя в базу sql, созданная с помощью sqlalchemy.

    :ivar __tablename__: Название таблицы.
    :vartype __tablename__: str
    :ivar id: Идентификатор пользователя.
    :vartype id: Column[int]
    :ivar chat_id: Идентификатор чата пользователя.
    :vartype chat_id: Column[str]
    :ivar role: Роль пользователя (Admin/User).
    :vartype role: Column[str]
    :ivar user_orders: Поле для связи таблицы пользователей с таблицей заказов.
    :vartype user_orders: _RelationshipDeclared
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    role = Column(String, unique=False, nullable=False)

    user_orders = relationship('Orders', back_populates='users')


class User:
    """
    Класс для работы с таблицей данных пользователя.
    """

    def __init__(self):
        """
        Конструктор класса.
        """

        self.Base = Base

    def _add_admin(self, chat_id):
        """
        Меняет роль пользователя в базе на Admin.
        """

        user = session.query(Users).filter_by(chat_id=chat_id).first()
        session.delete(user)
        session.commit()
        user = Users(chat_id=chat_id, role = 'Admin')
        session.add(user)
        session.commit()
    
    def add_new(self, chat_id):
        """
        Добавляет новго пользователя в базу.
        """

        user = Users(chat_id=chat_id, role = 'User')
        session.add(user)
        session.commit()

    def is_new(self, chat_id):
        """
        Проверяет есть ли в базе пользоваетель с данным идентификатором чата.

        :return: True если в базе нет пользователя с данным идентификатором чата, False в любом другом случае.
        :rtype: bool
        """

        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user == None:
            return True
        else:
            return False

    def is_admin(self, chat_id):
        """
        Проверяет является ли данный пользоваетель администратором.

        :return: True если в базе у пользователя с данным идентификатором чата роль Admin, False в любом другом случае.
        :rtype: bool
        """

        user = session.query(Users).filter_by(chat_id=chat_id).first()
        if user.role == 'Admin':
            return True
        else:
            return False


class Products(Base):
    """
    Модель для записи продуктов в базу sql, созданная с помощью sqlalchemy.

    :ivar __tablename__: Название таблицы.
    :vartype __tablename__: str
    :ivar id: Порядковый номер товара.
    :vartype id: Column[int]
    :ivar product_id: Идентификатор товара.
    :vartype product_id: Column[str]
    :ivar name: Название товара.
    :vartype name: Column[str]
    :ivar price: Цена товара.
    :vartype price: Column[int]
    :ivar description: Описание товара.
    :vartype description: Column[str]
    :ivar stock_quantity: Количество товара.
    :vartype stock_quantity: Column[int]
    :ivar image: Путь к изображению товара.
    :vartype image: Column[str]
    :ivar is_active: Параметр наличия товара на складе (True если товар, есть, False иначе).
    :vartype is_active: Column[bool]
    :ivar orders: Поле для связи таблицы товаров с таблицей заказов.
    :vartype orders: _RelationshipDeclared
    """

    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True, nullable=False) # добавление id предмета
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # связи
    orders = relationship('Basket', back_populates='items')


class Basket(Base):
    """
    Модель для записи набора продуктов для созданного заказа в базу sql, созданная с помощью sqlalchemy.

    :ivar tablename: Название таблицы.
    :vartype tablename: str
    :ivar id: Порядковый номер продукта.
    :vartype id: Column[int]
    :ivar order_id: Идентификатор заказа.
    :vartype order_id: Column[str]
    :ivar item_id: Идентификатор товара.
    :vartype item_id: Column[str]
    :ivar item_name: Название товара.
    :vartype item_name: Column[str]
    :ivar price: Цена товара.
    :vartype price: Column[int]
    :ivar quantity: Количество товара.
    :vartype quantity: Column[int]
    :ivar orders: Поле для связи таблицы наборов товаров с таблицей заказов.
    :vartype orders: _RelationshipDeclared
    :ivar items: Поле для связи таблицы наборов товаров с таблицей товаров.
    :vartype items: _RelationshipDeclared
    """
    __tablename__ = 'basket'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.number_order'), nullable=False)
    item_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    #связи
    orders = relationship('Orders', back_populates='items')
    items = relationship('Products', back_populates='orders')


# база данных заказов
class Orders(Base):
    """
    Модель для записи заказов в базу sql, созданная с помощью sqlalchemy.

    :ivar __tablename__: Название таблицы.
    :vartype __tablename__: str
    :ivar id: Порядковый номер заказа.
    :vartype id: Column[int]
    :ivar user_id: Идентификатор пользователя.
    :vartype user_id: Column[str]
    :ivar number_order: Идентификатор заказа.
    :vartype number_order: Column[int]
    :ivar status: Статус заказа.
    :vartype status: Column[str]
    :ivar total_sum: Сумма заказа.
    :vartype total_sum: Column[int]
    :ivar datetime: Дата заказа.
    :vartype datetime: Column[datetime]
    :ivar delivery_type: Тип доставки.
    :vartype delivery_type: Column[str]
    :ivar delivery_address: Адрес доставки.
    :vartype delivery_address: Column[str]
    :ivar users: Поле для связи таблицы заказов с таблицей пользователей.
    :vartype users: _RelationshipDeclared
    :ivar items: Поле для связи таблицы заказов с таблицей наборов товаров.
    :vartype items: _RelationshipDeclared
    """

    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.chat_id'), nullable=False)
    number_order = Column(Integer, unique=True, nullable=False)
    status = Column(String, nullable=False)
    total_sum = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    delivery_type = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False, default=None)
    
    # связи
    users = relationship('Users', back_populates='user_orders')
    items = relationship('Basket', back_populates='orders')


class PickUpPoints(Base):
    """
    Модель для записи пунктов выдачи заказов в базу sql, созданная с помощью sqlalchemy.

    :ivar __tablename__: Название таблицы.
    :vartype __tablename__: str
    :ivar id: Идентификатор пункта.
    :vartype id: Column[int]
    :ivar name: Название пунктра.
    :vartype name: Column[str]
    :ivar address: Адрес пункта.
    :vartype address: Column[str]
    :ivar working_hours: Часы работы.
    :vartype working_hours: Column[str]
    """
    
    __tablename__ = 'points'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    working_hours= Column(String, nullable=False)

# Создает все модели данных
Base.metadata.create_all(engine)

# функция добавления товара
def addItem(item_id, item_name, item_price, item_description, item_quantity, item_image):
    """
    Добавляет товар в базу sql.
    """

    item = Products(
        product_id = item_id,
        name=item_name,
        price=item_price,
        description=item_description,
        stock_quantity=item_quantity,
        image=item_image,
        is_active = True
        )
    session.add(item)
    session.commit()

# функция удаление товара
def deleteItem(item_id):
    """
    Удаляет товар из базы sql.
    """

    item = session.query(Products).filter_by(product_id = item_id).first()
    session.delete(item)
    session.commit()

# деактивация товара (для отображения в заказах)
def disactivateItem(item_id):
    """
    В базе sql делает товар недоступным (в поле is_active записывается False).
    """

    item = session.query(Products).filter_by(product_id = item_id).first()
    item.is_active = False
    session.commit()

# функция изменения атрибута товара
def updateItemAttribute(item_id, item_attribute, item_value):
    """
    Меняет в базе sql выбранный атрибут.
    """

    item = session.query(Products).filter_by(product_id = item_id).first()
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
def addOrder(user_id, order_id, order_status, order_sum, delivery_type, order_datetime, delivery_address):
    """
    Добавляет заказ в базу sql.
    """

    order = Orders(
        user_id=user_id,
        number_order=order_id,
        status=order_status,
        total_sum=order_sum,
        datetime=order_datetime,
        delivery_type=delivery_type, 
        delivery_address = delivery_address
        )
    session.add(order)
    session.commit()

# функция добавления в класс Basket
def addBasket(order_id, item_id, item_name, quantity, price):
    """
    Добавляет набор товаров для созданного заказа в базу sql.
    """

    basket = Basket(order_id=order_id, item_id=item_id, item_name=item_name, quantity=quantity, price=price)
    session.add(basket)
    session.commit()

# функция вывода данных из класса Basket
def get_basket():
    """
    Возвращает наборы товаров для всех созданных заказов из базы sql.

    :return: Список словарей наборов товаров для всех заказов из базы sql.
    :rtype: list
    """
    
    basket_db = session.query(Basket).all()
    basket_list = []
    for basket in basket_db:
        basket_list.append({
            'order_id': basket.order_id,
            'product_id': basket.item_id,
            'name': basket.item_name,
            'quantity': basket.quantity,
            'price': basket.price})
    return basket_list

# вывод данных из базы товаров в виде списка
def get_products():
    """
    Возвращает все продукты из базы sql.

    :return: Список словарей продуктов из базы sql.
    :rtype: list
    """

    products_db = session.query(Products).all()
    products_list = []
    for item in products_db:
        products_list.append({
            'id': item.product_id,
            "name": item.name,
            "price": item.price,
            "description": item.description,
            "stock_quantity": item.stock_quantity,
            'image': item.image,
            "is_active": item.is_active
            })
    # print(products_list)
    return products_list

# функция изменения статуса заказа
def change_status(number_order, order_status):
    """
    Меняет статус заказа в базе sql.
    """

    order = session.query(Orders).filter_by(number_order=number_order).first()
    order.status = order_status
    session.commit()
