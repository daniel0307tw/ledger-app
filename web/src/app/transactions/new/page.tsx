'use client'

import { useRouter } from 'next/navigation'
import { createTransaction } from '@/lib/api'
import { TransactionForm } from '@/components/TransactionForm'
import { PageHeader } from '@/components/PageHeader'

export default function NewTransactionPage() {
  const router = useRouter()

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-16">
      <PageHeader title="新增收支紀錄" />
      <TransactionForm
        submitLabel="新增"
        onSubmit={async (input) => {
          await createTransaction(input)
          router.push('/calendar')
        }}
      />
    </main>
  )
}
