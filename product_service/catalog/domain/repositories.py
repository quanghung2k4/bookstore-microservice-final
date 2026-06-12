from typing import Protocol


class ProductRepository(Protocol):
    def create(self, data):
        ...

    def update(self, product, data):
        ...
