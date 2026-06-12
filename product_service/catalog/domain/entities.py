from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List


@dataclass(frozen=True)
class ProductSnapshot:
    id: int
    name: str
    sku: str
    price: Decimal
    stock: int
    category: str
    brand: str
    product_type: str
    attributes: Dict[str, str] = field(default_factory=dict)
    variants: List[dict] = field(default_factory=list)
