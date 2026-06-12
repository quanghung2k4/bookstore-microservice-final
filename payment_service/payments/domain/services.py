import uuid


def generate_transaction_id() -> str:
    return f"PAY-{uuid.uuid4().hex[:12].upper()}"

