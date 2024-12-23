import uuid
import model.database as database

class Product:
    def __init__(self, name, price, description, stock_quantity, image, is_active = None, id = None):
        if id == None:
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
        
        if is_active == None:
            self.is_active = True
        else:
            self.is_active = is_active

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"

class DuplicateProductIdError(Exception): # исключение при дублировании ID
    pass

# products_data = [
#     {"name": "Банан", "price": 100, "description": "Банан из Африки, жёлтый", "stock_quantity": 50, 'image': 'https://avatars.mds.yandex.net/i?id=45760c598fc7066e3b979e0574d1f5c504e023c6-10414509-images-thumbs&n=13'},
#     {"name": "Хлеб", "price": 200, "description": "Местный, свежий", "stock_quantity": 20, 'image':  'https://cdn-img.perekrestok.ru/i/800x800-fit/xdelivery/files/5f/0c/6c03e02b315c21a6d1daca6bb029.jpg'},
#     {"name": "Телефон", "price": 300, "description": "Импортный, на Android", "stock_quantity": 10, 'image':  'https://avatars.mds.yandex.net/i?id=5920a940a44bbefcb98868342436b832_l-4292261-images-thumbs&n=13'},
#     ]
products = []

def get_products():
    products.clear()
    base_products = database.get_products()
    for item in base_products:
        products.append(Product(**item))
    #products = [Product(**data) for data in base_products]
    return products

def add_new_product(name, price, description, stock_quantity, image):
    new_product = Product(name, price, description, stock_quantity, image)
    database.addItem(
        new_product.id,
        new_product.name,
        new_product.price,
        new_product.description,
        new_product.stock_quantity,
        new_product.image
        )

    for existing_product in products:
        if existing_product.id == new_product.id:
            raise DuplicateProductIdError(f"Продукт с ID '{existing_product.id}' уже существует, и это невероятно, ведь мы используем UUID!")
    products.append(new_product)
    print(products)
    return new_product