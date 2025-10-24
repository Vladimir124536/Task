class InventoryError(Exception):
    """Базовое исключение для системы инвентаризации."""
    pass


class ValidationError(InventoryError):
    """Ошибка валидации данных."""
    pass


class ProductNotFoundError(InventoryError):
    """Товар не найден по SKU."""
    pass
