from apps.core.base_crud import BaseCRUDManager
from apps.products.models import Category


class CategoryCRUDManager(BaseCRUDManager):
    def __init__(self):
        self.model = Category


category_manager = CategoryCRUDManager()
