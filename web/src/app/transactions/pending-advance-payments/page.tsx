'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { listAccounts, listCategories, listPendingAdvancePayments, settleAdvancePayment } from '@/lib/api'
import type { Account, Category, Transaction } from '@/lib/types'
import { todayISO } from '@/lib/date'

export default function PendingAdvancePaymentsPage() {
  const [pending, setPending] = useState<Transaction[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const [openId, setOpenId] = useState<number | null>(null)
  const [settleDate, setSettleDate] = useState('')
  const [settleAmount, setSettleAmount] = useState('')
  const [settleAccountId, setSettleAccountId] = useState<number | ''>('')

  function refresh() {
    setLoading(true)
    Promise.all([listPendingAdvancePayments(), listAccounts(), listCategories()])
      .then(([p, a, c]) => {
        setPending(p)
        setAccounts(a)
        setCategories(c)
      })
      .catch((e) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  const categoryName = (id: number | null) => (id === null ? '—' : (categories.find((c) => c.id === id)?.name ?? `#${id}`))
  const accountName = (id: number) => accounts.find((a) => a.id === id)?.name ?? `#${id}`

  function openSettleForm(t: Transaction) {
    setError(null)
    setOpenId(t.id)
    setSettleDate(todayISO())
    // 預帶「代墊金額」（advancePaymentAmount），不是交易總金額（amount）——還款只針對代墊的那一部分。
    setSettleAmount(t.advancePaymentAmount != null ? String(t.advancePaymentAmount) : '')
    setSettleAccountId('')
  }

  function closeSettleForm() {
    setOpenId(null)
  }

  async function handleSettle(e: React.FormEvent, id: number) {
    e.preventDefault()
    if (!settleDate || !settleAmount || !settleAccountId) return
    setSubmitting(true)
    setError(null)
    try {
      await settleAdvancePayment(id, {
        date: settleDate,
        amount: Number(settleAmount),
        accountId: Number(settleAccountId),
      })
      setOpenId(null)
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '確認收到還款失敗')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <Link href="/settings" className="text-xs text-ink-soft/50">
          ← 設定
        </Link>
        <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          待收回代墊款<span className="text-mint">.</span>
        </h1>
      </header>

      <section className="px-5 pt-5">
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : pending.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            目前沒有待收回的代墊款
          </p>
        ) : (
          <ul className="space-y-2" data-testid="pending-advance-payment-list">
            {pending.map((t) => (
              <li
                key={t.id}
                data-testid={`pending-advance-payment-${t.id}`}
                className="rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-ink">{categoryName(t.categoryId)}</p>
                    <p className="text-xs text-ink-soft/50">
                      {t.date} · {accountName(t.accountId)}
                      {t.note ? ` · ${t.note}` : ''}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-base tabular-nums text-coral">
                      總額 ${t.amount.toLocaleString()}
                    </p>
                    <p className="font-mono text-xs tabular-nums text-ink-soft/50">
                      （代墊 ${(t.advancePaymentAmount ?? 0).toLocaleString()}）
                    </p>
                  </div>
                </div>

                {openId === t.id ? (
                  <form onSubmit={(e) => handleSettle(e, t.id)} className="mt-3 space-y-2 border-t border-line pt-3">
                    <label className="block">
                      <span className="mb-1 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">
                        還款日期
                      </span>
                      <input
                        type="date"
                        value={settleDate}
                        onChange={(e) => setSettleDate(e.target.value)}
                        data-testid={`settle-date-${t.id}`}
                        className="w-full rounded-xl border border-line bg-surface-high px-3 py-2 text-ink outline-none focus:border-mint"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-1 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">
                        還款金額
                      </span>
                      <input
                        type="number"
                        min="0"
                        step="1"
                        value={settleAmount}
                        onChange={(e) => setSettleAmount(e.target.value)}
                        data-testid={`settle-amount-${t.id}`}
                        className="w-full rounded-xl border border-line bg-surface-high px-3 py-2 text-ink outline-none focus:border-mint"
                      />
                    </label>
                    <label className="block">
                      <span className="mb-1 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">
                        入帳帳戶
                      </span>
                      <select
                        value={settleAccountId}
                        onChange={(e) => setSettleAccountId(e.target.value ? Number(e.target.value) : '')}
                        data-testid={`settle-account-${t.id}`}
                        className="w-full rounded-xl border border-line bg-surface-high px-3 py-2 text-ink outline-none focus:border-mint"
                      >
                        <option value="">請選擇帳戶</option>
                        {accounts.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <div className="flex gap-2 pt-1">
                      <button
                        type="submit"
                        disabled={submitting}
                        data-testid={`confirm-settle-${t.id}`}
                        className="flex-1 rounded-xl bg-mint py-2 text-xs font-semibold text-void disabled:opacity-50"
                      >
                        {submitting ? '處理中…' : '確認收到還款'}
                      </button>
                      <button
                        type="button"
                        onClick={closeSettleForm}
                        data-testid={`cancel-settle-${t.id}`}
                        className="rounded-xl border border-line px-3 py-2 text-xs text-ink-soft/70"
                      >
                        取消
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => openSettleForm(t)}
                      data-testid={`settle-advance-payment-${t.id}`}
                      className="rounded-xl border border-line px-3 py-1.5 text-xs text-ink-soft/70"
                    >
                      確認收到還款
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}

        {error && (
          <p role="alert" className="mt-3 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
            {error}
          </p>
        )}
      </section>
    </main>
  )
}
