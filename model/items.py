class Item:
    def __init__(self, order_id, product_id, name, price, quantity):
        self.order_id = order_id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

        def __repr__(self):
            return f"Item(order_id={self.order_id}, product_id={self.product_id}, name='{self.name}', price={self.price}, quantity={self.quantity})"

all_items = []