def validate_quantity(quantity: int) -> None:
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

