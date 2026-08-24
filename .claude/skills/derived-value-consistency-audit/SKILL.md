---
name: derived-value-consistency-audit
description: Use when a business rule computes a derived value (a discount, an "effective amount", a status-dependent total) that isn't stored directly but re-derived at multiple call sites. Before shipping a fix or new call site for such a rule, audit every place that computes it to make sure they all agree.
---

## The failure shape

A rule like "settled advance-payment transactions count as `amount − advance_payment_amount`; pending ones count the full amount" looks like it lives in one place (a SQL `CASE` in the repository layer), but the moment any *other* code path needs the same total, it's tempting to just re-add the raw `amount` — because that path was written before the rule existed, or because the rule's owner didn't know this second path existed.

In this project that happened twice with the same rule:
1. The edit-transaction endpoint didn't re-evaluate `advance_payment_status` when a first-time advance-payment flag was added via edit — it stayed unset, so the transaction silently never appeared in the "pending advance payments" list.
2. The frontend calendar page's monthly total summed raw `t.amount` instead of the effective amount, so it disagreed with the reports page's category-summary total for the same month.

Neither bug was caught by "does this file's tests pass" — each file's own tests were internally consistent. The bug only shows up when you compare two independently-computed totals for the same underlying data.

## What to do when you touch a derived-value rule

1. **Grep for every call site that could plausibly need this value**, not just the one you're editing. Search for the raw field name (e.g. `amount`) across both backend query/service code and frontend aggregation code — a derived rule that lives only in one repository method is not the only place a total gets computed; frontend pages often re-aggregate from a list response instead of calling the authoritative endpoint.
2. **Extract the rule into a single named function/helper** wherever the language allows, instead of inlining the same conditional in N places. This project has `_effective_amount()` (backend SQL CASE) and `effectiveAmount()` (`web/src/lib/transactions.ts`) as the two authoritative implementations — new call sites should call these, not reimplement the condition.
3. **Verify agreement against real data**, not just unit tests in isolation: pull the same period/filter through every call site (e.g. `/api/reports/category-summary` vs. the calendar page vs. the budget page) and confirm the totals match exactly before calling the change done.
4. **When adding a new status transition** (edit, delete, revert) to an entity that carries a derived-value flag, ask explicitly: does this transition need to reset the flag? (e.g. editing a settled advance payment's amount must flip it back to pending — the old amount's settlement no longer applies to the new amount.)
