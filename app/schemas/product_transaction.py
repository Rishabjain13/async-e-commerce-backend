from pydantic import BaseModel
from typing import List, Dict, Optional

class VariantSchema(BaseModel):
    sku: str
    attributes: Dict[str, str]   # size, color
    quantity: int

class ProductTransactionSchema(BaseModel):
    name: str
    description: str | None = None
    price: float
    variants: list[VariantSchema]
    rating: float | None = None