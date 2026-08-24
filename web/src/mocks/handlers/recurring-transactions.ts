import { http, HttpResponse } from 'msw'
import type { RecurringTransaction, RecurringTransactionInput } from '@/lib/types'
import { mockRecurringTransactions } from '@/mocks/fixtures'

let nextId = mockRecurringTransactions.length + 1

export const recurringTransactionHandlers = [
  http.post('/api/recurring-transactions', async ({ request }) => {
    const body = (await request.json()) as Partial<RecurringTransactionInput>
    if (!body.frequency || !body.amount || !body.categoryId || !body.accountId || !body.startDate || !body.generateCount) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    if (body.amount <= 0) {
      return HttpResponse.json({ success: false, error: { message: '金額必須為正數' } }, { status: 400 })
    }
    const rule: RecurringTransaction = {
      id: nextId++,
      frequency: body.frequency,
      amount: body.amount,
      categoryId: body.categoryId,
      accountId: body.accountId,
      type: body.type ?? '支出',
      note: body.note ?? null,
      startDate: body.startDate,
      generateCount: body.generateCount,
      status: '啟用',
    }
    mockRecurringTransactions.push(rule)
    return HttpResponse.json({ success: true, data: rule }, { status: 201 })
  }),

  http.get('/api/recurring-transactions', () => {
    return HttpResponse.json({ success: true, data: mockRecurringTransactions })
  }),

  http.put('/api/recurring-transactions/:id', async ({ request, params }) => {
    const id = Number(params.id)
    const rule = mockRecurringTransactions.find((r) => r.id === id)
    if (!rule) {
      return HttpResponse.json({ success: false, error: { message: '找不到該固定收支規則' } }, { status: 404 })
    }
    const body = (await request.json()) as RecurringTransactionInput
    Object.assign(rule, body, { note: body.note ?? null })
    return HttpResponse.json({ success: true, data: rule })
  }),

  http.delete('/api/recurring-transactions/:id', ({ params }) => {
    const id = Number(params.id)
    const index = mockRecurringTransactions.findIndex((r) => r.id === id)
    if (index === -1) {
      return HttpResponse.json({ success: false, error: { message: '找不到該固定收支規則' } }, { status: 404 })
    }
    mockRecurringTransactions.splice(index, 1)
    return HttpResponse.json({ success: true })
  }),

  http.post('/api/recurring-transactions/:id/generate', ({ params }) => {
    const id = Number(params.id)
    const rule = mockRecurringTransactions.find((r) => r.id === id)
    if (!rule) {
      return HttpResponse.json({ success: false, error: { message: '找不到該固定收支規則' } }, { status: 404 })
    }
    return HttpResponse.json({ success: true, data: { generatedCount: 0, transactions: [] } })
  }),
]
