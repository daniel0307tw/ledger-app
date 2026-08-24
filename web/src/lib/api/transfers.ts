import { apiClient } from '@/lib/api/client'
import type { Transaction, TransferInput } from '@/lib/types'

export async function createTransfer(input: TransferInput): Promise<[Transaction, Transaction]> {
  return apiClient<[Transaction, Transaction]>('/transfers', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
