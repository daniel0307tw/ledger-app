from behave import then


@then('操作失敗，錯誤為"{message}"')
def step_then_failure_with_message(context, message):
    assert context.last_response is not None, "No response received"
    resp = context.last_response.json()
    assert resp.get("success") is False, f"Expected success=false, got {resp}"
    actual_message = resp.get("error", {}).get("message")
    assert actual_message == message, f'Expected error message "{message}", got "{actual_message}"'
