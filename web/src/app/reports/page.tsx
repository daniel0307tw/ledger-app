'use client'

import { useEffect, useRef, useState } from 'react'
import { getCategoryDetail, getCategorySummary, listAccounts } from '@/lib/api'
import type { Account, CategorySummary } from '@/lib/types'
import { CategoryPieChart, type CategoryDetailState } from '@/components/CategoryPieChart'
import { BottomNav } from '@/components/BottomNav'
import { endOfMonth, monthLabel, startOfMonth, toISODate } from '@/lib/date'

export default function ReportsPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth())
  const [summary, setSummary] = useState<CategorySummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accounts, setAccounts] = useState<Account[]>([])

  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)
  const [detail, setDetail] = useState<CategoryDetailState | null>(null)
  const detailRequestRef = useRef<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setExpandedCategory(null)
    setDetail(null)

    const startDate = toISODate(startOfMonth(year, month))
    const endDate = toISODate(endOfMonth(year, month))

    getCategorySummary(startDate, endDate)
      .then((data) => {
        if (cancelled) return
        setSummary(data)
      })
      .catch((e) => !cancelled && setError(e.message ?? '載入失敗'))
      .finally(() => !cancelled && setLoading(false))

    return () => {
      cancelled = true
    }
  }, [year, month])

  useEffect(() => {
    listAccounts()
      .then(setAccounts)
      .catch(() => {})
  }, [])

  function accountName(accountId: number) {
    return accounts.find((a) => a.id === accountId)?.name ?? `#${accountId}`
  }

  function goMonth(delta: number) {
    const d = new Date(year, month + delta, 1)
    setYear(d.getFullYear())
    setMonth(d.getMonth())
  }

  function handleCategoryClick(category: string) {
    if (expandedCategory === category) {
      detailRequestRef.current = null
      setExpandedCategory(null)
      setDetail(null)
      return
    }

    detailRequestRef.current = category
    setExpandedCategory(category)
    setDetail({ loading: true, error: null, transactions: [] })

    const startDate = toISODate(startOfMonth(year, month))
    const endDate = toISODate(endOfMonth(year, month))

    getCategoryDetail(category, startDate, endDate)
      .then((transactions) => {
        if (detailRequestRef.current !== category) return
        setDetail({ loading: false, error: null, transactions })
      })
      .catch((e) => {
        if (detailRequestRef.current !== category) return
        setDetail({ loading: false, error: e.message ?? '載入失敗', transactions: [] })
      })
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <div className="flex items-baseline justify-between">
          <h1 className="font-display text-2xl font-bold tracking-tight text-ink">
            報表<span className="text-mint">.</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-ink-soft/70">
            <button
              aria-label="上個月"
              onClick={() => goMonth(-1)}
              className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-surface-high hover:text-ink active:scale-95"
            >
              ‹
            </button>
            <span className="font-mono text-base tabular-nums text-ink" data-testid="reports-current-month">
              {year}　{monthLabel(year, month)}
            </span>
            <button
              aria-label="下個月"
              onClick={() => goMonth(1)}
              className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-surface-high hover:text-ink active:scale-95"
            >
              ›
            </button>
          </div>
        </div>
      </header>

      {error && (
        <p className="mx-5 mt-4 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral" role="alert">
          {error}
        </p>
      )}

      <section className="px-5 pt-6">
        {loading ? (
          <p className="py-16 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : summary.length === 0 ? (
          <p
            data-testid="reports-empty-state"
            className="rounded-xl border border-dashed border-line py-16 text-center text-sm text-ink-soft/40"
          >
            這個月還沒有支出紀錄
          </p>
        ) : (
          <CategoryPieChart
            data={summary}
            onCategoryClick={handleCategoryClick}
            expandedCategory={expandedCategory}
            detail={detail}
            accountName={accountName}
          />
        )}
      </section>

      <BottomNav />
    </main>
  )
}
