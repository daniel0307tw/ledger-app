import { http, HttpResponse } from 'msw'
import type { Account, AccountInput } from '@/lib/types'
import { mockAccounts, mockTransactions } from '@/mocks/fixtures'

let nextId = mockAccounts.length + 1

function computeBalance(accountId: number): number {
  return mockTransactions
    .filter((t) => t.accountId === accountId)
    .reduce((sum, t) => (t.type === '收入' ? sum + t.amount : sum - t.amount), 0)
}

export const accountHandlers = [
  http.post('/api/accounts', async ({ request }) => {
    const body = (await request.json()) as Partial<AccountInput>
    if (!body.name || !body.type) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    const account: Account = { id: nextId++, name: body.name, type: body.type, balance: 0 }
    mockAccounts.push(account)
    return HttpResponse.json({ success: true, data: account }, { status: 201 })
  }),

  http.get('/api/accounts', () => {
    const data = mockAccounts.map((a) => ({ ...a, balance: computeBalance(a.id) }))
    return HttpResponse.json({ success: true, data })
  }),
]
