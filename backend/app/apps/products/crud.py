from apps.core.base_crud import BaseCRUDManager
from apps.products.models import Category, Product


class ProductCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Product


class CategoryCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Category


product_manager = ProductCRUDManager()
category_manager = CategoryCRUDManager()
