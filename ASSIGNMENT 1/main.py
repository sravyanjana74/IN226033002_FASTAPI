from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

@app.get("/")
def home():
    return {"message": "FastAPI is working!"}

products = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "price": 800, "in_stock": True},
    {"id": 2, "name": "Headphones", "category": "Electronics", "price": 150, "in_stock": True},
    {"id": 3, "name": "Coffee Mug", "category": "Home", "price": 20, "in_stock": False},
    {"id": 4, "name": "Notebook", "category": "Stationery", "price": 5, "in_stock": True}
]

feedback = []

# Q1: Updated to include min_price
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = Query(None), 
    min_price: Optional[int] = Query(None)
):
    result = products
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]
    if min_price:
        result = [p for p in result if p["price"] >= min_price]
    return result

# Q2: Get Name & Price Only
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}

# Q3: Customer Feedback
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {"message": "Feedback submitted successfully", "total": len(feedback)}

# Q4: Dashboard Summary
@app.get("/products/summary")
def get_summary():
    return {
        "total_products": len(products),
        "in_stock_count": len([p for p in products if p["in_stock"]]),
        "most_expensive": max(products, key=lambda p: p["price"]),
        "categories": list(set(p["category"] for p in products))
    }

# Q5: Bulk Orders
class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, total = [], [], 0
    for item in order.items:
        p = next((x for x in products if x["id"] == item.product_id), None)
        if p and p["in_stock"]:
            sub = p["price"] * item.quantity
            total += sub
            confirmed.append({"name": p["name"], "subtotal": sub})
        else:
            failed.append({"id": item.product_id, "reason": "Unavailable"})
    return {"confirmed": confirmed, "failed": failed, "grand_total": total}
