import { apiClient } from '@/lib/api/client'
import type { Account, AccountInput } from '@/lib/types'

export async function createAccount(input: AccountInput): Promise<Account> {
  return apiClient<Account>('/accounts', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listAccounts(): Promise<Account[]> {
  return apiClient<Account[]>('/accounts')
}
