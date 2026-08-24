---
name: native-pull-to-refresh
description: Use when building a touch-driven pull-to-refresh gesture in React (or reviewing one). React's JSX touch event props are passive by default, which silently breaks preventDefault() on touchmove — this documents the correct pattern and how to catch the bug before it reaches a real device.
---

## The bug this prevents

React 17+ attaches JSX touch handlers (`onTouchMove`, `onTouchStart`, etc.) as **passive listeners** by default, for scroll performance. Calling `e.preventDefault()` inside a JSX-attached `onTouchMove` handler is silently ignored — no error, no warning, it just doesn't suppress the browser's native scroll/overscroll behavior. On a real phone this shows up as your custom pull-indicator and the browser's/PWA's native pull-to-refresh (or rubber-band overscroll) both firing at once, fighting each other visually.

This is easy to miss in development because:
- Desktop browsers don't have a native pull-to-refresh gesture to conflict with.
- A headless test browser typically has `navigator.maxTouchPoints === 0` and no real touch emulation, so naive manual testing won't reproduce it either — you have to dispatch synthetic `Touch`/`TouchEvent` objects to exercise the code path at all, and a *passive* listener will still "receive" a synthetic dispatch, making the bug look fixed when it isn't (the dispatch mechanism, not `preventDefault`, is what you're accidentally testing).

## The correct pattern

Attach the listener manually via `addEventListener` with `{ passive: false }` inside a `useEffect`, using a ref to the DOM node — never via the JSX prop:

```tsx
useEffect(() => {
  const el = containerRef.current
  if (!el) return

  function handleTouchMove(e: TouchEvent) {
    // ...compute pull distance...
    e.preventDefault() // only works because passive:false below
  }

  el.addEventListener('touchmove', handleTouchMove, { passive: false })
  return () => el.removeEventListener('touchmove', handleTouchMove)
}, [])
```

See `web/src/components/PullToRefresh.tsx` in this repo for the full working implementation (start/move/end handlers, pull-distance threshold, refreshing state).

## Verifying it actually works without a real device

Dispatch synthetic touch events through the browser's own `Touch`/`TouchEvent` constructors (not a testing-library helper that may not route through real DOM event dispatch), and check for the actual visual state transition (e.g. indicator height / status text changing), not just that a handler function was called. If the synthetic dispatch shows zero effect, suspect the passive-listener issue first — it's the most common cause, not a mocking gap.
