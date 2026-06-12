def validate_stock(stock: int) -> None:
    if stock < 0:
        raise ValueError("Stock cannot be negative.")
