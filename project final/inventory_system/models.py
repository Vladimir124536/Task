import json
import os
from .exceptions import ValidationError, ProductNotFoundError


class Product:
    def __init__(self, sku: str, name: str, category: str, quantity: int, price: float):
        if not sku or not isinstance(sku, str):
            raise ValidationError("SKU должно быть непустой строкой.")
        if not name:
            raise ValidationError("Имя товара не может быть пустым.")
        if not isinstance(category, str):
            raise ValidationError("Категория должна быть строкой.")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValidationError("Количество должно быть целым числом ≥ 0.")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValidationError("Цена должна быть числом ≥ 0.")

        self.sku = sku
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = float(price)

    def __repr__(self):
        return f"Product(sku='{self.sku}', name='{self.name}', qty={self.quantity}, price={self.price:.2f})"

    def to_dict(self):
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
        }

    @staticmethod
    def from_dict(data: dict):
        return Product(
            data["sku"],
            data["name"],
            data["category"],
            int(data["quantity"]),
            float(data["price"]),
        )


class Warehouse:
    def __init__(self, filepath="data.json"):
        self.products = {}
        self.filepath = filepath
        self.load_from_file()

    # --- CRUD операции ---
    def add_product(self, product: Product):
        if product.sku in self.products:
            raise ValidationError(f"Товар с SKU {product.sku} уже существует.")
        self.products[product.sku] = product
        self.save_to_file()

    def remove_product(self, sku: str):
        if sku not in self.products:
            raise ProductNotFoundError(f"Товар с SKU {sku} не найден.")
        del self.products[sku]
        self.save_to_file()

    def update_quantity(self, sku: str, delta: int):
        if sku not in self.products:
            raise ProductNotFoundError(f"Товар с SKU {sku} не найден.")
        new_qty = self.products[sku].quantity + delta
        if new_qty < 0:
            raise ValidationError("Количество не может стать отрицательным.")
        self.products[sku].quantity = new_qty
        self.save_to_file()

    def set_quantity(self, sku: str, new_qty: int):
        if sku not in self.products:
            raise ProductNotFoundError(f"Товар с SKU {sku} не найден.")
        if new_qty < 0:
            raise ValidationError("Количество не может быть отрицательным.")
        self.products[sku].quantity = new_qty
        self.save_to_file()

    def update_price(self, sku: str, new_price: float):
        if sku not in self.products:
            raise ProductNotFoundError(f"Товар с SKU {sku} не найден.")
        if new_price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        self.products[sku].price = new_price
        self.save_to_file()

    # --- Поиск и отчёты ---
    def find_by_name(self, name: str):
        return [p for p in self.products.values() if name.lower() in p.name.lower()]

    def filter_by_category(self, category: str):
        return [p for p in self.products.values() if p.category.lower() == category.lower()]

    def list_all(self, sort_by=None, reverse=False):
        products = list(self.products.values())
        if sort_by and hasattr(Product, sort_by):
            products.sort(key=lambda p: getattr(p, sort_by), reverse=reverse)
        return products

    def total_value(self):
        return sum(p.price * p.quantity for p in self.products.values())

    def low_stock(self, threshold: int):
        return [p for p in self.products.values() if p.quantity <= threshold]

    # --- Сохранение и загрузка ---
    def save_to_file(self):
        data = [p.to_dict() for p in self.products.values()]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_file(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                product = Product.from_dict(item)
                self.products[product.sku] = product
