'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createTransfer, listAccounts } from '@/lib/api'
import type { Account } from '@/lib/types'
import { PageHeader } from '@/components/PageHeader'
import { todayISO } from '@/lib/date'

export default function TransferPage() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [fromAccountId, setFromAccountId] = useState('')
  const [toAccountId, setToAccountId] = useState('')
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState(todayISO())
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listAccounts().then(setAccounts).catch(() => {})
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!fromAccountId || !toAccountId || !amount) {
      setError('請填寫所有欄位')
      return
    }
    setSubmitting(true)
    try {
      await createTransfer({
        fromAccountId: Number(fromAccountId),
        toAccountId: Number(toAccountId),
        amount: Number(amount),
        date,
      })
      router.push('/accounts')
    } catch (err: any) {
      setError(err?.message ?? '轉帳失敗')
      setSubmitting(false)
    }
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-16">
      <PageHeader title="帳戶間轉帳" />
      <form onSubmit={handleSubmit} className="space-y-5 px-5 pb-10 pt-4">
        <label className="block">
          <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">轉出帳戶</span>
          <select
            data-testid="from-account"
            value={fromAccountId}
            onChange={(e) => setFromAccountId(e.target.value)}
            className="w-full appearance-none rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          >
            <option value="">請選擇</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </label>

        <div className="flex justify-center text-mint">↓</div>

        <label className="block">
          <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">轉入帳戶</span>
          <select
            data-testid="to-account"
            value={toAccountId}
            onChange={(e) => setToAccountId(e.target.value)}
            className="w-full appearance-none rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          >
            <option value="">請選擇</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">金額</span>
          <div className="flex items-center rounded-2xl border border-line bg-surface px-4 focus-within:border-mint">
            <span className="font-mono text-xl text-ink-soft/40">$</span>
            <input
              data-testid="transfer-amount"
              type="number"
              inputMode="decimal"
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0"
              className="w-full bg-transparent py-3.5 pl-2 font-mono text-3xl text-ink outline-none tabular-nums"
            />
          </div>
        </label>

        <label className="block">
          <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">日期</span>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
          />
        </label>

        {error && (
          <p role="alert" className="rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
            {error}
          </p>
        )}

        <button
          type="submit"
          data-testid="submit-transfer"
          disabled={submitting}
          className="w-full rounded-2xl bg-mint py-3.5 text-center font-semibold text-void shadow-glow-mint transition-transform active:scale-[0.99] disabled:opacity-50"
        >
          {submitting ? '轉帳中…' : '確認轉帳'}
        </button>
      </form>
    </main>
  )
}
