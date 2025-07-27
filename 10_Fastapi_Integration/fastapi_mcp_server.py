from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from pydantic import BaseModel

app = FastAPI(title="Product API")
_products: dict[int, dict] = {}


class Product(BaseModel):
    name: str
    price: float


@app.get("/products")
def list_products():
    """List all products"""
    return list(_products.values())


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """Get a product by its ID"""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    return _products[product_id]


@app.post("/products")
def create_product(p: Product):
    """Create a new product"""
    new_id = len(_products) + 1
    _products[new_id] = {"id": new_id, **p.model_dump()}
    return _products[new_id]


mcp = FastMCP.from_fastapi(app=app, name="ProductMCP")

# 添加 MCP Resource，URI 任意定义约定
@mcp.resource("resource://products/all", description="所有产品列表")
def all_products_resource() -> dict:
    """返回当前所有产品的数据列表"""
    return list_products()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)
