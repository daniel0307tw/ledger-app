'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { listAccounts, listCategories } from '@/lib/api'
import type { Account, Category, TransactionInput } from '@/lib/types'
import { todayISO } from '@/lib/date'
import { CategoryPicker } from '@/components/CategoryPicker'

export type TransactionFormValue = {
  date: string
  amount: string
  categoryId: number | ''
  accountId: string
  type: '收入' | '支出'
  note: string
  advancePaymentAmount: string
}

const emptyValue: TransactionFormValue = {
  date: todayISO(),
  amount: '',
  categoryId: '',
  accountId: '',
  type: '支出',
  note: '',
  advancePaymentAmount: '',
}

export function TransactionForm({
  initial,
  submitLabel,
  onSubmit,
  onDelete,
  showAdvancePayment = true,
}: {
  initial?: Partial<TransactionFormValue>
  submitLabel: string
  onSubmit: (input: TransactionInput) => Promise<void>
  onDelete?: () => Promise<void>
  showAdvancePayment?: boolean
}) {
  const router = useRouter()
  const [value, setValue] = useState<TransactionFormValue>({ ...emptyValue, ...initial })
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listAccounts().then(setAccounts).catch(() => {})
    listCategories().then(setCategories).catch(() => {})
  }, [])

  function handleTypeChange(type: '收入' | '支出') {
    setValue((v) => {
      const selectedCategory = categories.find((c) => c.id === v.categoryId)
      const stillValid = selectedCategory && (selectedCategory.type === '皆可' || selectedCategory.type === type)
      return {
        ...v,
        type,
        categoryId: stillValid ? v.categoryId : '',
        // 代墊金額僅限支出交易，切換為收入時一併清除
        advancePaymentAmount: type === '支出' ? v.advancePaymentAmount : '',
      }
    })
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    const amount = Number(value.amount)
    if (!value.date || !amount || !value.categoryId || !value.accountId || !value.type) {
      setError('請填寫所有必填欄位')
      return
    }

    const advancePaymentAmount =
      isExpense && value.advancePaymentAmount !== '' ? Number(value.advancePaymentAmount) : null
    if (advancePaymentAmount != null && advancePaymentAmount > amount) {
      setError('代墊金額不可超過交易總金額')
      return
    }

    setSubmitting(true)
    try {
      await onSubmit({
        date: value.date,
        amount,
        categoryId: value.categoryId,
        accountId: Number(value.accountId),
        type: value.type,
        note: value.note || undefined,
        advancePaymentAmount,
      })
    } catch (err: any) {
      setError(err?.message ?? '操作失敗')
      setSubmitting(false)
    }
  }

  async function handleDelete() {
    if (!onDelete) return
    if (!confirm('確定要刪除這筆收支紀錄嗎？')) return
    setDeleting(true)
    setError(null)
    try {
      await onDelete()
    } catch (err: any) {
      setError(err?.message ?? '刪除失敗')
      setDeleting(false)
    }
  }

  const isExpense = value.type === '支出'

  return (
    <form onSubmit={handleSubmit} className="space-y-5 px-5 pb-10 pt-4">
      <div className="grid grid-cols-2 gap-1.5 rounded-2xl border border-line bg-surface p-1.5">
        {(['支出', '收入'] as const).map((t) => (
          <button
            key={t}
            type="button"
            data-testid={`type-${t}`}
            onClick={() => handleTypeChange(t)}
            className={`rounded-xl py-2.5 text-sm font-medium transition-all ${
              value.type === t
                ? t === '支出'
                  ? 'bg-coral text-void shadow-glow-coral'
                  : 'bg-mint text-void shadow-glow-mint'
                : 'text-ink-soft/60'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <label className="block">
        <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">金額</span>
        <div className="flex items-center rounded-2xl border border-line bg-surface px-4 transition-colors focus-within:border-mint">
          <span className="font-mono text-xl text-ink-soft/40">$</span>
          <input
            data-testid="input-amount"
            type="number"
            inputMode="decimal"
            min="0"
            step="1"
            placeholder="0"
            value={value.amount}
            onChange={(e) => setValue((v) => ({ ...v, amount: e.target.value }))}
            className={`w-full bg-transparent py-3.5 pl-2 font-mono text-3xl outline-none tabular-nums ${isExpense ? 'text-coral' : 'text-mint'}`}
          />
        </div>
      </label>

      <label className="block">
        <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">日期</span>
        <input
          data-testid="input-date"
          type="date"
          value={value.date}
          onChange={(e) => setValue((v) => ({ ...v, date: e.target.value }))}
          className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">分類</span>
        <CategoryPicker
          value={value.categoryId}
          onChange={(categoryId) => setValue((v) => ({ ...v, categoryId }))}
          transactionType={value.type}
        />
      </label>

      <label className="block">
        <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">帳戶</span>
        <select
          data-testid="input-account"
          value={value.accountId}
          onChange={(e) => setValue((v) => ({ ...v, accountId: e.target.value }))}
          className="w-full appearance-none rounded-2xl border border-line bg-surface px-4 py-3 text-ink outline-none focus:border-mint"
        >
          <option value="">請選擇帳戶</option>
          {accounts.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </label>

      {isExpense && showAdvancePayment && (
        <label className="block">
          <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">
            代墊金額（選填）
            <span className="ml-2 normal-case tracking-normal text-ink-soft/40">
              這筆金額中有多少是幫別人代墊的，之後收到還款再結清
            </span>
          </span>
          <div className="flex items-center rounded-2xl border border-line bg-surface px-4 transition-colors focus-within:border-mint">
            <span className="font-mono text-base text-ink-soft/40">$</span>
            <input
              data-testid="input-advance-payment-amount"
              type="number"
              inputMode="decimal"
              min="0"
              step="1"
              placeholder="0"
              value={value.advancePaymentAmount}
              onChange={(e) => setValue((v) => ({ ...v, advancePaymentAmount: e.target.value }))}
              className="w-full bg-transparent py-3 pl-2 font-mono text-lg text-ink outline-none tabular-nums"
            />
          </div>
        </label>
      )}

      <label className="block">
        <span className="mb-2 block text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">備註（選填）</span>
        <input
          data-testid="input-note"
          value={value.note}
          onChange={(e) => setValue((v) => ({ ...v, note: e.target.value }))}
          className="w-full rounded-2xl border border-line bg-surface px-4 py-3 text-ink placeholder:text-ink-soft/40 outline-none focus:border-mint"
        />
      </label>

      {error && (
        <p role="alert" className="rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
          {error}
        </p>
      )}

      <div className="space-y-2 pt-2">
        <button
          type="submit"
          data-testid="submit-transaction"
          disabled={submitting}
          className="w-full rounded-2xl bg-mint py-3.5 text-center font-semibold text-void shadow-glow-mint transition-transform active:scale-[0.99] disabled:opacity-50"
        >
          {submitting ? '儲存中…' : submitLabel}
        </button>
        {onDelete && (
          <button
            type="button"
            data-testid="delete-transaction"
            onClick={handleDelete}
            disabled={deleting}
            className="w-full rounded-2xl border border-coral/30 py-3.5 text-center font-medium text-coral disabled:opacity-50"
          >
            {deleting ? '刪除中…' : '刪除這筆紀錄'}
          </button>
        )}
        <button
          type="button"
          onClick={() => router.back()}
          className="w-full py-2 text-center text-sm text-ink-soft/50"
        >
          取消
        </button>
      </div>
    </form>
  )
}
