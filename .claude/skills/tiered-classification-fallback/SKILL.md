---
name: tiered-classification-fallback
description: Use when designing an auto-categorization/classification feature that has no ground truth to train on (e.g. classifying imported transactions into spending categories from free-text seller/item names). A layered keyword → LLM-suggestion → default fallback, with each tier only acting on high confidence, keeps errors visible and correctable instead of silently wrong.
---

## The situation this fits

A feature needed to auto-assign a spending category to transactions synced from cloud invoices, based only on seller name + item description. There was no existing categorization logic at all — everything fell into one hardcoded default category ("日常用品" / general goods), which is why an unrelated amount of food purchases ended up misclassified as general goods. The fix wasn't "make the AI smarter" (there was no AI involved yet) — it was building the first tier of actual classification logic.

## The pattern

Three tiers, each only committing to an answer it's actually confident about, falling through otherwise:

1. **Keyword rules** (`category_classifier.py`'s `CATEGORY_KEYWORDS`) — a deliberately small, high-precision keyword list per category, substring-matched against `f"{seller_name} {item_summary}"`. Returns `None` (not a guess) when nothing matches. Keep this list conservative: a keyword that's *usually* right but sometimes wrong (e.g. a seller name that sells multiple categories of goods) does more damage silently miscategorizing than it saves by auto-classifying a few more items.
2. **LLM suggestion** — when keyword rules don't match, an LLM (with access to the category list) makes a best-effort guess but is explicitly instructed to leave the field empty rather than force a guess it isn't confident about ("猜不出來就不填，不要硬猜").
3. **Default fallback** — only when neither tier above produced an answer, fall back to the same default category as before. This is a deliberate, discussed tradeoff, not an accident: silently defaulting is more useful day-to-day than blocking every ambiguous item on a manual decision, as long as tiers 1–2 keep the *frequency* of hitting this tier low.

## Why this beats "make it a single smarter classifier"

- Each tier is independently auditable — a miscategorization can be traced to "no keyword matched and the LLM also didn't suggest one" vs. "a keyword rule was wrong," which tells you whether to fix a keyword list entry or reconsider the LLM prompt.
- Retroactively fixing bad historical data is safe: correcting already-synced records is a matter of replaying them through `_resolve_category_id()` and comparing old vs. new category — because the tiers are pure functions of the same seller/item text, results are reproducible.
- Before shipping the fallback behavior, explicitly decide (and ideally get sign-off) on whether "can't classify" should silently default or stop and ask — that's a product decision with real UX cost either way, not something to default silently without discussion.
