from users.domain.services import validate_role


class UserService:
    def __init__(self, repository):
        self.repository = repository

    def create_user(self, data):
        # Set default role if not provided
        if "role" not in data:
            data["role"] = "customer"
        validate_role(data["role"])
        return self.repository.create(data)

    def login(self, username, password):
        return self.repository.authenticate(username, password)
