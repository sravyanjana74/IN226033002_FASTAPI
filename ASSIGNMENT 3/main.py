from fastapi import FastAPI, Response, status, Query
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# --- Data Model ---
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# --- Database Mockup (Initial State) ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

# --- Helper Function ---
def find_product(p_id: int):
    for p in products:
        if p['id'] == p_id:
            return p
    return None

# --- API ENDPOINTS ---

@app.get('/products')
def get_all_products():
    """Returns all products and the total count."""
    return {"products": products, "total": len(products)}

# ── Q5: INVENTORY AUDIT (Must be above /{product_id}) ──
@app.get('/products/audit')
def product_audit():
    in_stock_list = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    
    # Total value: Sum of (price * 10 units) for in-stock items
    stock_value = sum(p['price'] * 10 for p in in_stock_list)
    
    # Identify most expensive product
    priciest = max(products, key=lambda p: p['price']) if products else None
    
    return {
        'total_products': len(products),
        'in_stock_count': len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value': stock_value,
        'most_expensive': {'name': priciest['name'], 'price': priciest['price']} if priciest else None,
    }

# ── BONUS: BULK DISCOUNT (Must be above /{product_id}) ──
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(..., description='Category to apply discount to'),
    discount_percent: int = Query(..., ge=1, le=99, description='Percentage to cut (1-99)'),
):
    updated_items = []
    for p in products:
        if p['category'].lower() == category.lower():
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated_items.append(p)
            
    if not updated_items:
        return {'message': f'No products found in category: {category}'}
        
    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated_items),
        'updated_products': updated_items,
    }

@app.get('/products/{product_id}')
def get_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    return product

@app.post('/products', status_code=status.HTTP_201_CREATED)
def add_product(new_p: NewProduct, response: Response):
    # Check for duplicates (Case-insensitive)
    for p in products:
        if p['name'].lower() == new_p.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": f"Product '{new_p.name}' already exists"}
            
    # Auto-generate ID (Max ID + 1)
    next_id = max(p['id'] for p in products) + 1 if products else 1
    
    product_dict = new_p.model_dump()
    product_dict['id'] = next_id
    products.append(product_dict)
    
    return {"message": "Product added", "product": product_dict}

@app.put('/products/{product_id}')
def update_product(
    product_id: int, 
    response: Response,
    price: Optional[int] = None, 
    in_stock: Optional[bool] = None
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    
    # Update only if parameters are provided
    if price is not None:
        product['price'] = price
    if in_stock is not None:
        product['in_stock'] = in_stock
        
    return {"message": "Product updated", "product": product}

@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
        
    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted"}