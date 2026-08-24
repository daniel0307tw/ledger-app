from sqlalchemy.orm import Session

from app.models.budget import Budget, BudgetScope


class BudgetRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, scope: BudgetScope, category_id: int | None, monthly_amount) -> Budget:
        budget = Budget(scope=scope, category_id=category_id, monthly_amount=monthly_amount)
        self.session.add(budget)
        self.session.flush()
        return budget

    def find(self, budget_id: int) -> Budget | None:
        return self.session.get(Budget, budget_id)

    def find_all(self) -> list[Budget]:
        return self.session.query(Budget).order_by(Budget.id).all()

    def find_total_budget(self) -> Budget | None:
        return self.session.query(Budget).filter(Budget.scope == BudgetScope.TOTAL).one_or_none()

    def find_by_category(self, category_id: int) -> Budget | None:
        return (
            self.session.query(Budget)
            .filter(Budget.scope == BudgetScope.CATEGORY, Budget.category_id == category_id)
            .one_or_none()
        )

    def delete(self, budget: Budget) -> None:
        self.session.delete(budget)
        self.session.flush()
