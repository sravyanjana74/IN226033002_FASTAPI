from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- Data Models ---
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# --- In-Memory Database ---
# Initializing with the products mentioned in your assignment
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 599, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

cart = []
orders = []

# --- Endpoints ---

@app.get("/products")
def get_products():
    """List all available products"""
    return {"products": products}

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    """Q1, Q3, & Q4: Add items, handle stock, and update existing quantities"""
    # 1. Check if product exists (Q3 - 404 Case)
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 2. Check if product is in stock (Q3 - 400 Case)
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # 3. Check if product already in cart (Q4 - Update Logic)
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    # 4. If new item, add to cart (Q1 logic)
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

@app.get("/cart")
def view_cart():
    """Q2: View cart with grand total and item count"""
    if not cart:
        return {"message": "Cart is empty", "items": [], "grand_total": 0}
    
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart), # Unique products count
        "grand_total": grand_total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    """Q5 & Q6: Remove specific item from cart"""
    global cart
    item_exists = any(item for item in cart if item["product_id"] == product_id)
    
    if not item_exists:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart = [item for item in cart if item["product_id"] != product_id]
    return {"message": "Item removed from cart"}

@app.post("/cart/checkout")
def checkout(details: CheckoutRequest):
    """Q5, Q6, & Bonus: Move cart to orders and clear cart"""
    # 1. Bonus: Empty cart check
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    # 2. Move items to orders (Q6 expects one order entry per product)
    items_to_checkout = len(cart)
    for item in cart:
        new_order = {
            "order_id": len(orders) + 1,
            "customer_name": details.customer_name,
            "delivery_address": details.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(new_order)

    # 3. Clear the cart
    cart.clear()
    
    return {
        "message": "Order placed successfully",
        "orders_placed": items_to_checkout,
        "status": "Success"
    }

@app.get("/orders")
def get_orders():
    """Q5 & Q6: View all historical orders"""
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
