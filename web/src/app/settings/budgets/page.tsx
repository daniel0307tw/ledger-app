'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { createBudget, deleteBudget, getBudgetStatus, listCategories } from '@/lib/api'
import type { BudgetScope, BudgetStatus, Category } from '@/lib/types'

export default function BudgetsPage() {
  const [statuses, setStatuses] = useState<BudgetStatus[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const [scope, setScope] = useState<BudgetScope>('分類預算')
  const [categoryId, setCategoryId] = useState<number | ''>('')
  const [monthlyAmount, setMonthlyAmount] = useState('')

  function refresh() {
    setLoading(true)
    Promise.all([getBudgetStatus(), listCategories()])
      .then(([s, c]) => {
        setStatuses(s)
        setCategories(c)
      })
      .catch((e) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleDelete(id: number) {
    try {
      await deleteBudget(id)
      setError(null)
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '刪除失敗')
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!monthlyAmount || (scope === '分類預算' && !categoryId)) return
    setCreating(true)
    setError(null)
    try {
      await createBudget({
        scope,
        categoryId: scope === '分類預算' ? Number(categoryId) : undefined,
        monthlyAmount: Number(monthlyAmount),
      })
      setMonthlyAmount('')
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '建立失敗')
    } finally {
      setCreating(false)
    }
  }

  const categoryName = (id: number | null) => (id === null ? '總預算' : categories.find((c) => c.id === id)?.name ?? `#${id}`)

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <Link href="/settings" className="text-xs text-ink-soft/50">
          ← 設定
        </Link>
        <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          預算<span className="text-mint">.</span>
        </h1>
      </header>

      <section className="px-5 pt-5">
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : statuses.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            還沒有設定任何預算
          </p>
        ) : (
          <ul className="space-y-2" data-testid="budget-status-list">
            {statuses.map((s) => {
              const pct = s.monthlyAmount > 0 ? Math.min(100, Math.max(0, (s.spent / s.monthlyAmount) * 100)) : 0
              return (
                <li
                  key={`${s.scope}-${s.categoryId ?? 'total'}`}
                  data-testid={`budget-status-${s.categoryId ?? 'total'}`}
                  className="rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-ink">{categoryName(s.categoryId)}</p>
                    <p className={`font-mono text-sm tabular-nums ${s.isOverBudget ? 'text-coral' : 'text-ink-soft/60'}`}>
                      ${s.spent.toLocaleString()} / ${s.monthlyAmount.toLocaleString()}
                    </p>
                  </div>
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-surface-high">
                    <div
                      className={`h-full rounded-full ${s.isOverBudget ? 'bg-coral' : 'bg-mint'}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  {s.isOverBudget && (
                    <p data-testid={`over-budget-${s.categoryId ?? 'total'}`} className="mt-1.5 text-xs text-coral">
                      已超支 ${Math.abs(s.remaining).toLocaleString()}
                    </p>
                  )}
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => handleDelete(s.id)}
                      data-testid={`delete-budget-${s.categoryId ?? 'total'}`}
                      className="rounded-xl border border-coral/30 px-3 py-1.5 text-xs text-coral"
                    >
                      刪除
                    </button>
                  </div>
                </li>
              )
            })}
          </ul>
        )}

        {error && (
          <p role="alert" className="mt-3 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
            {error}
          </p>
        )}

        <form onSubmit={handleCreate} className="mt-6 space-y-2">
          <p className="text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">新增預算</p>
          <div className="grid grid-cols-2 gap-1.5 rounded-2xl border border-line bg-surface p-1.5">
            {(['分類預算', '總預算'] as BudgetScope[]).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setScope(s)}
                data-testid={`scope-${s}`}
                className={`rounded-xl py-2.5 text-sm font-medium transition-all ${
                  scope === s ? 'bg-mint text-void shadow-glow-mint' : 'text-ink-soft/60'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
          {scope === '分類預算' && (
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : '')}
              data-testid="new-budget-category"
              className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
            >
              <option value="">選擇分類</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
          <input
            type="number"
            value={monthlyAmount}
            onChange={(e) => setMonthlyAmount(e.target.value)}
            placeholder="每月金額上限"
            data-testid="new-budget-amount"
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink placeholder:text-ink-soft/40 outline-none focus:border-mint"
          />
          <button
            type="submit"
            disabled={creating}
            data-testid="create-budget"
            className="w-full rounded-2xl bg-mint py-3 font-semibold text-void shadow-glow-mint disabled:opacity-50"
          >
            建立預算
          </button>
        </form>
      </section>
    </main>
  )
}
