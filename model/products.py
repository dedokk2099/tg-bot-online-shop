import uuid
import logging

from model import database


class Product:
    """
    Используется для хранения данных о товаре во время работы бота

    :ivar id: Уникальный идентификатор товара.
    :vartype id: str
    :ivar name: Наименование товара.
    :vartype name: str
    :ivar price: Цена товара.
    :vartype price: int
    :ivar description: Описание товара.
    :vartype description: str
    :ivar stock_quantity: Количество товара на складе.
    :vartype stock_quantity: int
    :ivar image: Ссылка на изображение товара.
    :vartype image: str
    :ivar is_active: Статус активности товара (True - активен, False - неактивен).
    :vartype is_active: bool
    """

    def __init__(
        self, name, price, description, stock_quantity, image, is_active=None, id=None
    ):
        """
        Инициализирует новый объект Product. Записывает атрибуты товара в поля класса.
        При создании нового товара часть атрибутов принимают стандартное значение и генерируется уникальный идентификатор.
        """
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.name = name
        try:
            self.price = int(price)
        except ValueError:
            self.price = 0
        self.description = description
        try:
            self.stock_quantity = int(stock_quantity)
        except ValueError:
            self.stock_quantity = 0
        self.image = image

        if is_active is None:
            self.is_active = True
        else:
            self.is_active = is_active

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"


class DuplicateProductIdError(Exception):  # исключение при дублировании ID
    """
    Исключение, возникающее при дублировании ID товара.

    Используется для обработки ситуаций, когда при создании нового
    товара его идентификатор уже существует в базе данных.
    """

    pass


products = []
"""
Список хранит все существующие товары в виде экземпляров класса Product

:type: list[Product]
"""
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def get_products():
    """
    Получает и возвращает список товаров.

    Очищает текущий список товаров, получает список товаров
    из базы данных и создает объекты `Product`, добавляя их
    в список, который затем возвращается.

    :return: Список объектов `Product`
    :rtype: list[Product]
    """
    products.clear()
    base_products = database.get_products()
    for item in base_products:
        products.append(Product(**item))
    # products = [Product(**data) for data in base_products]
    return products


def add_new_product(name, price, description, stock_quantity, image, chat_id):
    """
    Добавляет новый товар.

    Создает новый объект `Product` на основе входных данных,
    добавляет его в базу данных и проверяет на наличие дубликатов,
    после чего добавляет товар в список и возвращает его.

    :param name: Наименование товара
    :type name: str
    :param price: Цена товара
    :type price: int or str
    :param description: Описание товара
    :type description: str
    :param stock_quantity: Количество товара на складе.
    :type stock_quantity: int or str
    :param image: Ссылка на изображение товара
    :type image: str
    :raises DuplicateProductIdError: Если товар с таким ID уже существует
    :return: Объект созданного товара
    :rtype: Product
    """
    new_product = Product(name, price, description, stock_quantity, image)
    database.addItem(
        new_product.id,
        new_product.name,
        new_product.price,
        new_product.description,
        new_product.stock_quantity,
        new_product.image,
    )

    for existing_product in products:
        if existing_product.id == new_product.id:
            raise DuplicateProductIdError(
                f"Продукт с ID '{existing_product.id}' уже существует, и это невероятно, ведь мы используем UUID!"
            )
    products.append(new_product)
    logger.info(
        f"Added product: {name} (ID: {new_product.id}) by admin: {chat_id}"
    )
    print(products)
    return new_product
