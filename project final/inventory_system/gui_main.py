import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .models import Product, Warehouse
from .exceptions import InventoryError


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта товаров")
        self.root.geometry("950x600")

        self.warehouse = Warehouse()
        self.sort_reverse = False
        self.sort_column = None

        # === Верхняя панель ===
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Поиск:").grid(row=0, column=0)
        self.search_entry = tk.Entry(control_frame, width=20)
        self.search_entry.grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="🔍 Искать", command=self.search_products).grid(row=0, column=2)
        tk.Button(control_frame, text="Сбросить", command=self.refresh_table).grid(row=0, column=3, padx=10)

        tk.Label(control_frame, text="SKU:").grid(row=1, column=0)
        self.sku_entry = tk.Entry(control_frame, width=10)
        self.sku_entry.grid(row=1, column=1)

        tk.Label(control_frame, text="Название:").grid(row=1, column=2)
        self.name_entry = tk.Entry(control_frame, width=15)
        self.name_entry.grid(row=1, column=3)

        tk.Label(control_frame, text="Категория:").grid(row=1, column=4)
        self.category_entry = tk.Entry(control_frame, width=15)
        self.category_entry.grid(row=1, column=5)

        tk.Label(control_frame, text="Кол-во:").grid(row=2, column=0)
        self.qty_entry = tk.Entry(control_frame, width=10)
        self.qty_entry.grid(row=2, column=1)

        tk.Label(control_frame, text="Цена:").grid(row=2, column=2)
        self.price_entry = tk.Entry(control_frame, width=10)
        self.price_entry.grid(row=2, column=3)

        tk.Button(control_frame, text="Добавить", command=self.add_product).grid(row=2, column=4, padx=5)
        tk.Button(control_frame, text="Удалить", command=self.remove_product).grid(row=2, column=5)
        tk.Button(control_frame, text="Обновить", command=self.refresh_table).grid(row=2, column=6, padx=5)

        # === Таблица ===
        columns = ("sku", "name", "category", "quantity", "price")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, anchor="center", width=150)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_product)

        # === Нижняя панель ===
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)
        tk.Button(bottom_frame, text="Низкий остаток", command=self.show_low_stock).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Общая стоимость", command=self.show_total_value).pack(side="left", padx=10)

        self.refresh_table()

    # --- Методы управления ---
    def add_product(self):
        try:
            sku = self.sku_entry.get().strip()
            name = self.name_entry.get().strip()
            category = self.category_entry.get().strip()
            quantity = int(self.qty_entry.get())
            price = float(self.price_entry.get())

            product = Product(sku, name, category, quantity, price)
            self.warehouse.add_product(product)
            self.refresh_table()
            self.clear_entries()
            messagebox.showinfo("Успех", f"Товар '{name}' добавлен!")

        except InventoryError as e:
            messagebox.showerror("Ошибка", str(e))
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте введённые данные!")

    def remove_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления!")
            return
        sku = self.tree.item(selected[0], "values")[0]
        try:
            self.warehouse.remove_product(sku)
            self.refresh_table()
            messagebox.showinfo("Удалено", f"Товар {sku} удалён.")
        except InventoryError as e:
            messagebox.showerror("Ошибка", str(e))

    def edit_product(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        sku = self.tree.item(selected[0], "values")[0]
        product = self.warehouse.products.get(sku)
        if not product:
            return

        new_name = simpledialog.askstring("Редактировать", "Новое имя:", initialvalue=product.name)
        if new_name is None:
            return
        new_category = simpledialog.askstring("Редактировать", "Новая категория:", initialvalue=product.category)
        if new_category is None:
            return
        try:
            new_qty = int(simpledialog.askstring("Редактировать", "Новое количество:", initialvalue=product.quantity))
            new_price = float(simpledialog.askstring("Редактировать", "Новая цена:", initialvalue=product.price))
        except (ValueError, TypeError):
            messagebox.showerror("Ошибка", "Неверные данные!")
            return

        product.name = new_name
        product.category = new_category
        product.quantity = new_qty
        product.price = new_price
        self.warehouse.save_to_file()
        self.refresh_table()

    def refresh_table(self, products=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        products = products or self.warehouse.list_all()
        for p in products:
            self.tree.insert("", "end", values=(p.sku, p.name, p.category, p.quantity, f"{p.price:.2f}"))

    def search_products(self):
        text = self.search_entry.get().strip().lower()
        if not text:
            self.refresh_table()
            return
        results = [p for p in self.warehouse.products.values()
                   if text in p.name.lower() or text in p.category.lower()]
        self.refresh_table(results)

    def sort_by_column(self, col):
        reverse = not self.sort_reverse if self.sort_column == col else False
        self.sort_reverse = reverse
        self.sort_column = col
        sorted_products = sorted(
            self.warehouse.products.values(),
            key=lambda p: getattr(p, col),
            reverse=reverse
        )
        self.refresh_table(sorted_products)

    def show_low_stock(self):
        low_items = self.warehouse.low_stock(5)
        if not low_items:
            messagebox.showinfo("Остатки", "Все товары в норме!")
        else:
            msg = "\n".join([f"{p.name} — {p.quantity} шт." for p in low_items])
            messagebox.showwarning("Малый остаток", msg)

    def show_total_value(self):
        total = self.warehouse.total_value()
        messagebox.showinfo("Общая стоимость", f"💰 {total:.2f} тге.")

    def clear_entries(self):
        for entry in [self.sku_entry, self.name_entry, self.category_entry, self.qty_entry, self.price_entry]:
            entry.delete(0, tk.END)


def main():
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
