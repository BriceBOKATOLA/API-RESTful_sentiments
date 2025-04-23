from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str

class ProductOut(ProductCreate):
    id: int
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    product_id: int
    user_name: str | None = None
    comment_text: str

class ReviewOut(ReviewCreate):
    id: int
    timestamp: datetime
    sentiment_compound_score: float
    class Config:
        from_attributes = True