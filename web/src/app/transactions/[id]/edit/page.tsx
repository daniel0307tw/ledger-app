'use client'

import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { deleteTransaction, updateTransaction } from '@/lib/api'
import { TransactionForm, type TransactionFormValue } from '@/components/TransactionForm'
import { PageHeader } from '@/components/PageHeader'

export default function EditTransactionPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const searchParams = useSearchParams()
  const id = Number(params.id)

  // 目前的 API 只有依日期區間查詢的清單端點，沒有單筆查詢端點；
  // 從行事曆頁點進來時已經有完整資料，直接透過 URL query 帶過來，避免多一次往返。
  const categoryIdParam = searchParams.get('categoryId')
  const advancePaymentAmountParam = searchParams.get('advancePaymentAmount')
  const initial: Partial<TransactionFormValue> = {
    date: searchParams.get('date') ?? undefined,
    amount: searchParams.get('amount') ?? undefined,
    categoryId: categoryIdParam ? Number(categoryIdParam) : undefined,
    accountId: searchParams.get('accountId') ?? undefined,
    type: (searchParams.get('type') as '收入' | '支出') ?? undefined,
    note: searchParams.get('note') ?? undefined,
    advancePaymentAmount: advancePaymentAmountParam ?? '',
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-16">
      <PageHeader title="編輯收支紀錄" />
      <TransactionForm
        initial={initial}
        submitLabel="儲存"
        onSubmit={async (input) => {
          await updateTransaction(id, input)
          router.push('/calendar')
        }}
        onDelete={async () => {
          await deleteTransaction(id)
          router.push('/calendar')
        }}
      />
    </main>
  )
}
