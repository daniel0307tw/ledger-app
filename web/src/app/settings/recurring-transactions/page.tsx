'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import {
  createRecurringTransaction,
  deleteRecurringTransaction,
  generateRecurringTransaction,
  listAccounts,
  listCategories,
  listRecurringTransactions,
} from '@/lib/api'
import type { Account, Category, RecurringFrequency, RecurringTransaction } from '@/lib/types'

const FREQUENCIES: RecurringFrequency[] = ['每天', '每週', '每月', '每季', '每年', '每三年']
const TYPES = ['支出', '收入'] as const

export default function RecurringTransactionsPage() {
  const [rules, setRules] = useState<RecurringTransaction[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const [frequency, setFrequency] = useState<RecurringFrequency>('每月')
  const [amount, setAmount] = useState('')
  const [categoryId, setCategoryId] = useState<number | ''>('')
  const [accountId, setAccountId] = useState<number | ''>('')
  const [type, setType] = useState<(typeof TYPES)[number]>('支出')
  const [startDate, setStartDate] = useState('')
  const [generateCount, setGenerateCount] = useState('3')

  function refresh() {
    setLoading(true)
    Promise.all([listRecurringTransactions(), listAccounts(), listCategories()])
      .then(([r, a, c]) => {
        setRules(r)
        setAccounts(a)
        setCategories(c)
      })
      .catch((e) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!amount || !categoryId || !accountId || !startDate || !generateCount) return
    setCreating(true)
    setError(null)
    try {
      await createRecurringTransaction({
        frequency,
        amount: Number(amount),
        categoryId: Number(categoryId),
        accountId: Number(accountId),
        type,
        startDate,
        generateCount: Number(generateCount),
      })
      setAmount('')
      setStartDate('')
      setShowForm(false)
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '建立失敗')
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteRecurringTransaction(id)
      setError(null)
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '刪除失敗')
    }
  }

  async function handleGenerate(id: number) {
    try {
      const result = await generateRecurringTransaction(id)
      setError(null)
      if (result.generatedCount === 0) {
        setError('目前不需要補生成（已生成期數已達設定值）')
      }
    } catch (err: any) {
      setError(err?.message ?? '補生成失敗')
    }
  }

  const categoryName = (id: number) => categories.find((c) => c.id === id)?.name ?? `#${id}`
  const accountName = (id: number) => accounts.find((a) => a.id === id)?.name ?? `#${id}`

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <Link href="/settings" className="text-xs text-ink-soft/50">
          ← 設定
        </Link>
        <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          固定收支<span className="text-mint">.</span>
        </h1>
      </header>

      <section className="px-5 pt-5">
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : rules.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            還沒有任何固定收支規則
          </p>
        ) : (
          <ul className="space-y-2" data-testid="recurring-transaction-list">
            {rules.map((r) => (
              <li
                key={r.id}
                data-testid={`recurring-transaction-row-${r.id}`}
                className="rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-ink">
                      {categoryName(r.categoryId)} · {r.frequency}
                    </p>
                    <p className="text-xs text-ink-soft/50">
                      {accountName(r.accountId)} · 提前生成 {r.generateCount} 期 ·{' '}
                      <span className={r.status === '啟用' ? 'text-mint' : 'text-ink-soft/40'}>{r.status}</span>
                    </p>
                  </div>
                  <p className={`font-mono text-base tabular-nums ${r.type === '支出' ? 'text-ink' : 'text-mint'}`}>
                    {r.type === '支出' ? '-' : '+'}${r.amount.toLocaleString()}
                  </p>
                </div>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => handleGenerate(r.id)}
                    data-testid={`generate-${r.id}`}
                    className="rounded-xl border border-line px-3 py-1.5 text-xs text-ink-soft/70"
                  >
                    補生成
                  </button>
                  <button
                    onClick={() => handleDelete(r.id)}
                    data-testid={`delete-${r.id}`}
                    className="rounded-xl border border-coral/30 px-3 py-1.5 text-xs text-coral"
                  >
                    刪除
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {error && (
          <p role="alert" className="mt-3 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
            {error}
          </p>
        )}

        <button
          type="button"
          onClick={() => setShowForm((v) => !v)}
          data-testid="toggle-new-recurring-form"
          className="mt-6 flex w-full items-center justify-between rounded-2xl border border-line bg-surface px-4 py-3 text-sm font-medium text-ink"
        >
          新增規則
          <span className="text-ink-soft/50">{showForm ? '收合 ▲' : '展開 ▼'}</span>
        </button>

        {showForm && (
        <form onSubmit={handleCreate} className="mt-2 space-y-2">
          <div className="grid grid-cols-3 gap-1.5 rounded-2xl border border-line bg-surface p-1.5">
            {FREQUENCIES.map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFrequency(f)}
                data-testid={`frequency-${f}`}
                className={`rounded-xl py-2 text-xs font-medium transition-all ${
                  frequency === f ? 'bg-mint text-void shadow-glow-mint' : 'text-ink-soft/60'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-1.5 rounded-2xl border border-line bg-surface p-1.5">
            {TYPES.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setType(t)}
                className={`rounded-xl py-2.5 text-sm font-medium transition-all ${
                  type === t ? 'bg-mint text-void shadow-glow-mint' : 'text-ink-soft/60'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="金額"
            data-testid="new-amount"
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink placeholder:text-ink-soft/40 outline-none focus:border-mint"
          />
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : '')}
            data-testid="new-category"
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          >
            <option value="">選擇分類</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <select
            value={accountId}
            onChange={(e) => setAccountId(e.target.value ? Number(e.target.value) : '')}
            data-testid="new-account"
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          >
            <option value="">選擇帳戶</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            data-testid="new-start-date"
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          />
          <div className="flex items-center gap-2">
            <label className="text-sm text-ink-soft/60">提前生成期數</label>
            <input
              type="number"
              min={1}
              value={generateCount}
              onChange={(e) => setGenerateCount(e.target.value)}
              data-testid="new-generate-count"
              className="w-20 rounded-xl border border-line bg-surface px-3 py-2 text-ink outline-none focus:border-mint"
            />
          </div>
          <button
            type="submit"
            disabled={creating}
            data-testid="create-recurring-transaction"
            className="w-full rounded-2xl bg-mint py-3 font-semibold text-void shadow-glow-mint disabled:opacity-50"
          >
            建立規則
          </button>
        </form>
        )}
      </section>
    </main>
  )
}
