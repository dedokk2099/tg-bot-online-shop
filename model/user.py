from model.orders import add_new_order
from model.products import get_products

class User:
    def __init__(self, user_id):
        self.id = user_id
        self.cart = {}  # {product_id: quantity} - Корзина пользователя, хранит ID товара и количество

    def add_to_cart(self, product_id):
        self.cart[product_id] = self.cart.get(product_id, 0) + 1 # Добавляет товар в корзину или увеличивает количество

    def decrease_from_cart(self, product_id):
        if product_id in self.cart:
            self.cart[product_id] -= 1
    
    def remove_from_cart(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]

    def get_cart_items(self):
        items = []
        products = [product for product in get_products() if product.is_active]
        for product_id, quantity in self.cart.items():
            product = next((p for p in products if p.id == product_id), None) # Находим продукт по ID
            if product:
                items.append({'product': product, 'quantity': quantity}) # Добавляем товар в список для заказа
        return items
    
    def calculate_total_sum(self):
        return sum(item['product'].price * item['quantity'] for item in self.get_cart_items())

    def create_order(self, delivery_type, delivery_address):
        items = self.get_cart_items()
        if items:
            order = add_new_order(self.id, items, delivery_type, delivery_address)
            self.cart = {}  # Очищаем корзину после оформления заказа
            return order
        else:
            return None # Корзина пуста
