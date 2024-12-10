class Product:
    def __init__(self, id, name, price, description, stock_quantity, image):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.stock_quantity = stock_quantity
        self.image = image

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"

#Позднее нужно будет переименовать в products_data
products = [
    {'id': '1', "name": "Банан", "price": 100, "description": "Банан из Африки, жёлтый", "stock_quantity": 50, 'image': 'https://avatars.mds.yandex.net/i?id=45760c598fc7066e3b979e0574d1f5c504e023c6-10414509-images-thumbs&n=13'},
    {'id': '2', "name": "Хлеб", "price": 200, "description": "Местный, свежий", "stock_quantity": 20, 'image':  'https://cdn-img.perekrestok.ru/i/800x800-fit/xdelivery/files/5f/0c/6c03e02b315c21a6d1daca6bb029.jpg'},
    {'id': '3', "name": "Телефон", "price": 300, "description": "Импортный, на Android", "stock_quantity": 10, 'image':  'https://avatars.mds.yandex.net/i?id=5920a940a44bbefcb98868342436b832_l-4292261-images-thumbs&n=13'},
    ]
    # Добавьте сюда больше товаров

#Позднее нужно будет переименовать в products
products_as_class = [Product(**data) for data in products]