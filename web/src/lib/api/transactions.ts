import { apiClient } from '@/lib/api/client'
import type { SettleAdvancePaymentInput, SettleAdvancePaymentResult, Transaction, TransactionInput } from '@/lib/types'

export async function createTransaction(input: TransactionInput): Promise<Transaction> {
  return apiClient<Transaction>('/transactions', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function updateTransaction(id: number, input: TransactionInput): Promise<Transaction> {
  return apiClient<Transaction>(`/transactions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export async function deleteTransaction(id: number): Promise<void> {
  await apiClient<void>(`/transactions/${id}`, { method: 'DELETE' })
}

export async function listTransactions(startDate: string, endDate: string): Promise<Transaction[]> {
  const params = new URLSearchParams({ startDate, endDate })
  return apiClient<Transaction[]>(`/transactions?${params.toString()}`)
}

export async function settleAdvancePayment(
  id: number,
  input: SettleAdvancePaymentInput
): Promise<SettleAdvancePaymentResult> {
  return apiClient<SettleAdvancePaymentResult>(`/transactions/${id}/settle-advance-payment`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listPendingAdvancePayments(): Promise<Transaction[]> {
  return apiClient<Transaction[]>('/transactions/pending-advance-payments')
}
