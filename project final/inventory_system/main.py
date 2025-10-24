from .models import Product, Warehouse
from .exceptions import InventoryError


def print_menu():
    print("\n=== Система учёта товаров ===")
    print("1. Добавить товар")
    print("2. Удалить товар")
    print("3. Изменить количество")
    print("4. Изменить цену")
    print("5. Показать все товары")
    print("6. Поиск по имени")
    print("7. Фильтр по категории")
    print("8. Товары с низким остатком")
    print("9. Общая стоимость")
    print("0. Выход")


def main():
    warehouse = Warehouse()

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                sku = input("SKU: ")
                name = input("Название: ")
                category = input("Категория: ")
                quantity = int(input("Количество: "))
                price = float(input("Цена: "))
                product = Product(sku, name, category, quantity, price)
                warehouse.add_product(product)
                print("✅ Товар добавлен.")

            elif choice == "2":
                sku = input("SKU для удаления: ")
                warehouse.remove_product(sku)
                print("🗑️ Товар удалён.")

            elif choice == "3":
                sku = input("SKU: ")
                delta = int(input("Изменение количества (+/-): "))
                warehouse.update_quantity(sku, delta)
                print("✅ Количество обновлено.")

            elif choice == "4":
                sku = input("SKU: ")
                new_price = float(input("Новая цена: "))
                warehouse.update_price(sku, new_price)
                print("✅ Цена обновлена.")

            elif choice == "5":
                sort_by = input("Сортировать по (name/price/quantity/category) или Enter: ").strip() or None
                reverse = input("Обратный порядок? (y/n): ").lower() == "y"
                for p in warehouse.list_all(sort_by, reverse):
                    print(p)

            elif choice == "6":
                name = input("Введите часть имени: ")
                for p in warehouse.find_by_name(name):
                    print(p)

            elif choice == "7":
                category = input("Категория: ")
                for p in warehouse.filter_by_category(category):
                    print(p)

            elif choice == "8":
                threshold = int(input("Порог низкого остатка: "))
                for p in warehouse.low_stock(threshold):
                    print(p)

            elif choice == "9":
                print(f"💰 Общая стоимость товаров: {warehouse.total_value():.2f} Тенге.")

            elif choice == "0":
                print("👋 Выход из программы.")
                break

            else:
                print("Неверный выбор. Повторите попытку.")

        except InventoryError as e:
            print(f"Ошибка: {e}")
        except ValueError:
            print("Ошибка ввода. Проверьте данные.")
