import { apiClient } from '@/lib/api/client'
import type { GenerateRecurringTransactionResult, RecurringTransaction, RecurringTransactionInput } from '@/lib/types'

export async function createRecurringTransaction(input: RecurringTransactionInput): Promise<RecurringTransaction> {
  return apiClient<RecurringTransaction>('/recurring-transactions', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listRecurringTransactions(): Promise<RecurringTransaction[]> {
  return apiClient<RecurringTransaction[]>('/recurring-transactions')
}

export async function updateRecurringTransaction(
  id: number,
  input: RecurringTransactionInput
): Promise<RecurringTransaction> {
  return apiClient<RecurringTransaction>(`/recurring-transactions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export async function deleteRecurringTransaction(id: number): Promise<void> {
  await apiClient<void>(`/recurring-transactions/${id}`, { method: 'DELETE' })
}

export async function generateRecurringTransaction(id: number): Promise<GenerateRecurringTransactionResult> {
  return apiClient<GenerateRecurringTransactionResult>(`/recurring-transactions/${id}/generate`, {
    method: 'POST',
  })
}
