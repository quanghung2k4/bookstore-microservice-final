from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfile:
    id: int
    username: str
    email: str
    role: str

