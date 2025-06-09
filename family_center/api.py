from fastapi import FastAPI, HTTPException
from .grocery import GroceryItem, GroceryList

app = FastAPI(title="Family Command Center")

grocery_list = GroceryList()

@app.get("/")
def read_root():
    return {"message": "Family Command Center API"}

# Grocery Endpoints
@app.get("/grocery/items", response_model=list[GroceryItem])
def get_items():
    return grocery_list.list_items()

@app.post("/grocery/items", response_model=GroceryItem)
def add_item(item: GroceryItem):
    return grocery_list.add_item(item)

@app.put("/grocery/items/{item_id}")
def update_item(item_id: int, item: GroceryItem):
    if not grocery_list.update_item(item_id, item):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "updated"}

@app.delete("/grocery/items/{item_id}")
def delete_item(item_id: int):
    if not grocery_list.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}

@app.get("/grocery/instacart_link")
def instacart_link():
    link = grocery_list.generate_instacart_link()
    return {"url": link}
