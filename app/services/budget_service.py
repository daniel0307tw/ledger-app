from datetime import date

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.budget import Budget, BudgetScope
from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository


class BudgetService:
    def __init__(self, session: Session):
        self.session = session
        self.budgets = BudgetRepository(session)
        self.transactions = TransactionRepository(session)

    def create_budget(self, *, scope: str, category_id: int | None, monthly_amount) -> Budget:
        scope_enum = BudgetScope(scope)
        if scope_enum == BudgetScope.TOTAL:
            if self.budgets.find_total_budget() is not None:
                raise BusinessError("總預算已存在")
        else:
            if category_id is not None and self.budgets.find_by_category(category_id) is not None:
                raise BusinessError("此分類已設定過預算")

        budget = self.budgets.create(
            scope=scope_enum,
            category_id=category_id if scope_enum == BudgetScope.CATEGORY else None,
            monthly_amount=monthly_amount,
        )
        self.session.flush()
        return budget

    def update_budget(self, budget_id: int, *, monthly_amount) -> Budget:
        budget = self.budgets.find(budget_id)
        if budget is None:
            raise NotFoundError("找不到該預算")
        budget.monthly_amount = monthly_amount
        self.session.flush()
        return budget

    def delete_budget(self, budget_id: int) -> None:
        budget = self.budgets.find(budget_id)
        if budget is None:
            raise NotFoundError("找不到該預算")
        self.budgets.delete(budget)

    def list_budgets(self) -> list[Budget]:
        return self.budgets.find_all()

    def get_status(self) -> list[dict]:
        today = date.today()
        month_start = today.replace(day=1)
        spent_by_category = self.transactions.sum_amount_by_category_in_range(month_start, today)
        total_spent = self.transactions.sum_amount_in_range(month_start, today)

        results = []
        for budget in self.list_budgets():
            spent = total_spent if budget.scope == BudgetScope.TOTAL else spent_by_category.get(
                budget.category_id, 0.0
            )
            monthly_amount = float(budget.monthly_amount)
            remaining = monthly_amount - spent
            results.append(
                {
                    "id": budget.id,
                    "scope": budget.scope.value,
                    "categoryId": budget.category_id,
                    "monthlyAmount": monthly_amount,
                    "spent": spent,
                    "remaining": remaining,
                    "isOverBudget": remaining < 0,
                }
            )
        return results
