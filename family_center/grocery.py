from typing import List
from pydantic import BaseModel

class GroceryItem(BaseModel):
    id: int | None = None
    name: str
    quantity: int = 1
    notes: str | None = None


class GroceryList:
    def __init__(self):
        self.items: List[GroceryItem] = []
        self._counter = 0

    def add_item(self, item: GroceryItem) -> GroceryItem:
        self._counter += 1
        item.id = self._counter
        self.items.append(item)
        return item

    def list_items(self) -> List[GroceryItem]:
        return self.items

    def delete_item(self, item_id: int) -> bool:
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                return True
        return False

    def update_item(self, item_id: int, new_item: GroceryItem) -> bool:
        for i, item in enumerate(self.items):
            if item.id == item_id:
                updated = item.copy(update=new_item.dict(exclude_unset=True))
                updated.id = item_id
                self.items[i] = updated
                return True
        return False

    def generate_instacart_link(self) -> str:
        if not self.items:
            return ""
        item_names = [item.name for item in self.items]
        search_query = ','.join(item_names)
        return f"https://www.instacart.com/store/items?search={search_query}"
