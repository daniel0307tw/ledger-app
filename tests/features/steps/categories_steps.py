from behave import given, when

from app.models.category import CategoryType
from app.repositories.category_repository import CategoryRepository


@given("系統中有以下分類：")
def step_given_categories(context):
    repo = CategoryRepository(context.db_session)
    for row in context.table:
        category = repo.create(name=row["name"], type=CategoryType(row["type"]))
        context.categories_by_name[row["name"]] = category
    context.db_session.commit()


@when("使用者建立分類：")
def step_when_create_category(context):
    row = context.table[0]
    payload = {}
    if row["name"]:
        payload["name"] = row["name"]
    if row["type"]:
        payload["type"] = row["type"]
    context.last_response = context.api_client.post("/api/categories", json=payload)


@when("使用者查詢分類列表")
def step_when_list_categories(context):
    context.last_response = context.api_client.get("/api/categories")
