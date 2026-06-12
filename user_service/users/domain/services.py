VALID_ROLES = {"admin", "staff", "customer"}


def validate_role(role: str) -> None:
    if role not in VALID_ROLES:
        raise ValueError("Invalid role.")

