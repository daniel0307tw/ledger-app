from sqlalchemy.orm import Session

from app.models.category import Category, CategoryType


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, type: CategoryType) -> Category:
        category = Category(name=name, type=type)
        self.session.add(category)
        self.session.flush()
        return category

    def find(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def find_all(self) -> list[Category]:
        return self.session.query(Category).order_by(Category.id).all()

    def find_by_name(self, name: str) -> Category | None:
        # .first()（非 one_or_none）：category.name 不強制唯一（既有慣例），同名分類理論上
        # 可能有多筆；取 id 最小的一筆做為確定性結果，不因為使用者有重複命名就直接炸掉查詢。
        return self.session.query(Category).filter(Category.name == name).order_by(Category.id).first()
