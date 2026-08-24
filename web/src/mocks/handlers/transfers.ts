import { http, HttpResponse } from 'msw'
import type { Transaction, TransferInput } from '@/lib/types'
import { mockAccounts, mockTransactions } from '@/mocks/fixtures'

let nextId = mockTransactions.length + 1000

export const transferHandlers = [
  http.post('/api/transfers', async ({ request }) => {
    const body = (await request.json()) as Partial<TransferInput>
    if (!body.fromAccountId || !body.toAccountId || !body.amount || !body.date) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    const fromAccount = mockAccounts.find((a) => a.id === body.fromAccountId)
    const toAccount = mockAccounts.find((a) => a.id === body.toAccountId)
    if (!fromAccount || !toAccount) {
      return HttpResponse.json({ success: false, error: { message: '找不到該帳戶' } }, { status: 404 })
    }
    if (body.fromAccountId === body.toAccountId) {
      return HttpResponse.json(
        { success: false, error: { message: '轉出帳戶與轉入帳戶不可相同' } },
        { status: 422 }
      )
    }
    if (body.amount <= 0) {
      return HttpResponse.json({ success: false, error: { message: '金額必須為正數' } }, { status: 400 })
    }

    const transferGroupId = `mock-group-${nextId}`
    const outgoing: Transaction = {
      id: nextId++,
      date: body.date,
      amount: body.amount,
      categoryId: null,
      accountId: fromAccount.id,
      type: '支出',
      note: null,
      isTransfer: true,
      transferGroupId,
      syncStatus: 'synced',
      cashPositionId: 9000 + nextId,
      advancePaymentAmount: null,
      advancePaymentStatus: null,
      settlementTransactionId: null,
    }
    const incoming: Transaction = {
      id: nextId++,
      date: body.date,
      amount: body.amount,
      categoryId: null,
      accountId: toAccount.id,
      type: '收入',
      note: null,
      isTransfer: true,
      transferGroupId,
      syncStatus: 'synced',
      cashPositionId: 9000 + nextId,
      advancePaymentAmount: null,
      advancePaymentStatus: null,
      settlementTransactionId: null,
    }
    mockTransactions.push(outgoing, incoming)
    return HttpResponse.json({ success: true, data: [outgoing, incoming] }, { status: 201 })
  }),
]
