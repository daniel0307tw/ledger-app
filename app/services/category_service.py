from sqlalchemy.orm import Session

from app.models.category import Category, CategoryType
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, session: Session):
        self.repository = CategoryRepository(session)

    def create_category(self, name: str, type: CategoryType) -> Category:
        return self.repository.create(name=name, type=type)

    def list_categories(self) -> list[Category]:
        return self.repository.find_all()
