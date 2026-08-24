'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'
import { listTransactions, listAccounts, listCategories } from '@/lib/api'
import type { Account, Category, Transaction } from '@/lib/types'
import { Amount } from '@/components/Amount'
import { BottomNav } from '@/components/BottomNav'
import { buildCalendarGrid, monthLabel, toISODate, todayISO } from '@/lib/date'
import { effectiveAmount } from '@/lib/transactions'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

export default function CalendarPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth())
  const [selectedDate, setSelectedDate] = useState(todayISO())
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const grid = buildCalendarGrid(year, month)
    const startDate = toISODate(grid[0].date)
    const endDate = toISODate(grid[grid.length - 1].date)

    Promise.all([listTransactions(startDate, endDate), listAccounts(), listCategories()])
      .then(([tx, acc, cat]) => {
        if (cancelled) return
        setTransactions(tx)
        setAccounts(acc)
        setCategories(cat)
      })
      .catch((e) => !cancelled && setError(e.message ?? '載入失敗'))
      .finally(() => !cancelled && setLoading(false))

    return () => {
      cancelled = true
    }
  }, [year, month])

  const accountName = (id: number) => accounts.find((a) => a.id === id)?.name ?? '—'
  const categoryName = (id: number | null) =>
    id === null ? '轉帳' : (categories.find((c) => c.id === id)?.name ?? '—')

  const byDate = useMemo(() => {
    const map = new Map<string, Transaction[]>()
    for (const t of transactions) {
      if (!map.has(t.date)) map.set(t.date, [])
      map.get(t.date)!.push(t)
    }
    return map
  }, [transactions])

  const monthTotals = useMemo(() => {
    let income = 0
    let expense = 0
    for (const t of transactions) {
      if (t.isTransfer) continue
      if (t.type === '收入') income += t.amount
      else expense += effectiveAmount(t)
    }
    return { income, expense }
  }, [transactions])

  const grid = buildCalendarGrid(year, month)
  const selectedTransactions = (byDate.get(selectedDate) ?? []).slice().sort((a, b) => b.id - a.id)

  function goMonth(delta: number) {
    const d = new Date(year, month + delta, 1)
    setYear(d.getFullYear())
    setMonth(d.getMonth())
    setSelectedDate(toISODate(d))
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <div className="flex items-baseline justify-between">
          <h1 className="font-display text-2xl font-bold tracking-tight text-ink">
            記帳<span className="text-mint">.</span>
          </h1>
          <div className="flex items-center gap-3 text-sm text-ink-soft/70">
            <button
              aria-label="上個月"
              onClick={() => goMonth(-1)}
              className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-surface-high hover:text-ink active:scale-95"
            >
              ‹
            </button>
            <span className="font-mono text-base tabular-nums text-ink" data-testid="current-month">
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

        <div className="mt-4 flex gap-3">
          <div className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 shadow-card">
            <p className="text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">本月收入</p>
            <p className="font-mono text-lg text-mint">+{monthTotals.income.toLocaleString()}</p>
          </div>
          <div className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 shadow-card">
            <p className="text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">本月支出</p>
            <p className="font-mono text-lg text-coral">−{monthTotals.expense.toLocaleString()}</p>
          </div>
        </div>
      </header>

      {error && (
        <p className="mx-5 mt-4 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral" role="alert">
          {error}
        </p>
      )}

      <section className="px-5 pt-4">
        <div className="grid grid-cols-7 text-center text-xs text-ink-soft/40">
          {WEEKDAYS.map((w) => (
            <div key={w} className="py-1">
              {w}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-y-1" data-testid="calendar-grid">
          {grid.map(({ date, inMonth }) => {
            const iso = toISODate(date)
            const dayTx = byDate.get(iso) ?? []
            const netExpense = dayTx
              .filter((t) => !t.isTransfer)
              .reduce((s, t) => s + (t.type === '支出' ? effectiveAmount(t) : -t.amount), 0)
            const isSelected = iso === selectedDate
            const isToday = iso === todayISO()
            return (
              <button
                key={iso}
                data-testid={`day-${iso}`}
                onClick={() => setSelectedDate(iso)}
                disabled={!inMonth}
                className={`flex h-14 flex-col items-center justify-center rounded-xl text-sm transition-all
                  ${!inMonth ? 'text-ink-soft/20' : 'text-ink'}
                  ${isSelected ? 'bg-mint text-void shadow-glow-mint' : 'hover:bg-surface-high'}
                `}
              >
                <span className={isToday && !isSelected ? 'font-semibold text-coral' : ''}>{date.getDate()}</span>
                {dayTx.length > 0 && inMonth && (
                  <span
                    className={`mt-0.5 h-1 w-1 rounded-full ${isSelected ? 'bg-void' : netExpense >= 0 ? 'bg-coral' : 'bg-mint'}`}
                  />
                )}
              </button>
            )
          })}
        </div>
      </section>

      <section className="mt-5 px-5">
        <h2 className="mb-2 font-mono text-sm text-ink-soft/60">{selectedDate}</h2>
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : selectedTransactions.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            這天還沒有記帳
          </p>
        ) : (
          <ul className="space-y-2" data-testid="day-transactions">
            {selectedTransactions.map((t) => (
              <li key={t.id}>
                <Link
                  href={`/transactions/${t.id}/edit?${new URLSearchParams({
                    date: t.date,
                    amount: String(t.amount),
                    categoryId: t.categoryId !== null ? String(t.categoryId) : '',
                    accountId: String(t.accountId),
                    type: t.type,
                    note: t.note ?? '',
                    advancePaymentAmount: t.advancePaymentAmount != null ? String(t.advancePaymentAmount) : '',
                  }).toString()}`}
                  className="flex items-center justify-between rounded-xl border border-line bg-surface px-4 py-3 shadow-card transition-transform active:scale-[0.99]"
                >
                  <div>
                    <p className="flex items-center gap-1.5 text-sm text-ink">
                      {categoryName(t.categoryId)}
                      {t.advancePaymentAmount != null && (
                        <span
                          data-testid={`advance-payment-badge-${t.id}`}
                          className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            t.advancePaymentStatus === 'settled'
                              ? 'bg-mint-dim text-mint'
                              : 'bg-coral-dim text-coral'
                          }`}
                        >
                          代墊款 ${t.advancePaymentAmount.toLocaleString()} ·{' '}
                          {t.advancePaymentStatus === 'settled' ? '已收回' : '待收回'}
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-ink-soft/50">
                      {accountName(t.accountId)}
                      {t.note ? ` · ${t.note}` : ''}
                      {t.isTransfer ? ' · 轉帳' : ''}
                    </p>
                  </div>
                  <Amount value={t.amount} type={t.type} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <Link
        href="/transactions/new"
        aria-label="新增收支紀錄"
        data-testid="fab-new-transaction"
        className="fixed bottom-24 right-5 flex h-14 w-14 items-center justify-center rounded-full bg-mint text-2xl font-medium text-void shadow-glow-mint transition-transform active:scale-95"
      >
        +
      </Link>

      <BottomNav />
    </main>
  )
}
