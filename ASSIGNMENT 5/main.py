from fastapi import FastAPI, Query

app = FastAPI()

# --- SAMPLE DATA ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []  # To be populated via POST /orders

# --- Q1, Q2, Q3: CORE ENDPOINTS ---

@app.get("/products/search")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    is_reverse = (order == "desc")
    sorted_items = sorted(products, key=lambda p: p[sort_by], reverse=is_reverse)
    return {"sort_by": sort_by, "order": order, "products": sorted_items}

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    paged_products = products[start : start + limit]
    total_pages = -(-len(products) // limit)
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": paged_products
    }

# --- Q4, Q5, Q6: ASSIGNMENT TASKS ---

# Q4: Search Orders
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders 
        if customer_name.lower() in o["customer_name"].lower()
    ]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {
        "customer_name": customer_name, 
        "total_found": len(results), 
        "orders": results
    }

# Q5: Sort by Category then Price
@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))
    return {"products": result, "total": len(result)}

# Q6: Combined Browse (Flat Response Format)
@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):
    # Filter
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Sort
    if sort_by in ["price", "name"]:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))

    # Paginate
    total = len(result)
    start = (page - 1) * limit
    paged = result[start : start + limit]

    # CLEAN FLAT RESPONSE
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }

# --- UTILITY ENDPOINTS ---

@app.post("/orders")
def create_order(order: dict):
    order["order_id"] = len(orders) + 1
    orders.append(order)
    return {"message": "Order placed", "order": order}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return {"error": "Product not found"}
