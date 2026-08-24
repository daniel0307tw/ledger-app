import { http, HttpResponse } from 'msw'
import type { SettleAdvancePaymentInput, Transaction, TransactionInput } from '@/lib/types'
import { mockAccounts, mockCategories, mockTransactions } from '@/mocks/fixtures'

let nextId = mockTransactions.length + 1

function validateInput(body: Partial<TransactionInput>) {
  if (!body.date || !body.amount || !body.categoryId || !body.accountId || !body.type) {
    return { status: 400 as const, message: '必要參數未提供' }
  }
  if (body.amount <= 0) {
    return { status: 400 as const, message: '金額必須為正數' }
  }
  if (body.advancePaymentAmount != null && body.type !== '支出') {
    return { status: 422 as const, message: '代墊款標記僅限支出交易' }
  }
  if (body.advancePaymentAmount != null && body.amount != null && body.advancePaymentAmount > body.amount) {
    return { status: 422 as const, message: '代墊金額不可超過交易總金額' }
  }
  if (!mockAccounts.some((a) => a.id === body.accountId)) {
    return { status: 404 as const, message: '找不到該帳戶' }
  }
  const category = mockCategories.find((c) => c.id === body.categoryId)
  if (!category) {
    return { status: 404 as const, message: '找不到該分類' }
  }
  if (category.type !== '皆可' && category.type !== body.type) {
    return { status: 422 as const, message: '分類收支類型與交易類型不符' }
  }
  return null
}

export const transactionHandlers = [
  http.post('/api/transactions', async ({ request }) => {
    const body = (await request.json()) as Partial<TransactionInput>
    const error = validateInput(body)
    if (error) {
      return HttpResponse.json({ success: false, error: { message: error.message } }, { status: error.status })
    }
    const advancePaymentAmount = body.advancePaymentAmount ?? null
    const transaction: Transaction = {
      id: nextId++,
      date: body.date!,
      amount: body.amount!,
      categoryId: body.categoryId!,
      accountId: body.accountId!,
      type: body.type!,
      note: body.note ?? null,
      isTransfer: false,
      transferGroupId: null,
      syncStatus: 'synced',
      cashPositionId: 9000 + nextId,
      advancePaymentAmount,
      advancePaymentStatus: advancePaymentAmount != null ? 'pending' : null,
      settlementTransactionId: null,
    }
    mockTransactions.push(transaction)
    return HttpResponse.json({ success: true, data: transaction }, { status: 201 })
  }),

  http.put('/api/transactions/:id', async ({ params, request }) => {
    const id = Number(params.id)
    const existing = mockTransactions.find((t) => t.id === id)
    if (!existing) {
      return HttpResponse.json({ success: false, error: { message: '找不到該筆收支紀錄' } }, { status: 404 })
    }
    const body = (await request.json()) as Partial<TransactionInput>
    const error = validateInput(body)
    if (error) {
      return HttpResponse.json({ success: false, error: { message: error.message } }, { status: error.status })
    }
    const wasSettled = existing.advancePaymentStatus === 'settled'
    const originalAmount = existing.amount
    const originalAdvancePaymentAmount = existing.advancePaymentAmount
    const nextAdvancePaymentAmount = body.advancePaymentAmount ?? null

    Object.assign(existing, {
      date: body.date,
      amount: body.amount,
      categoryId: body.categoryId,
      accountId: body.accountId,
      type: body.type,
      note: body.note ?? null,
      advancePaymentAmount: nextAdvancePaymentAmount,
    })

    // 編輯一筆已結清的代墊款交易，若總金額或代墊金額任一變動，自動改回未結清並解除與還款交易的關聯。
    if (
      wasSettled &&
      (body.amount !== originalAmount || nextAdvancePaymentAmount !== originalAdvancePaymentAmount)
    ) {
      existing.advancePaymentStatus = 'pending'
      existing.settlementTransactionId = null
    }

    return HttpResponse.json({ success: true, data: existing })
  }),

  http.delete('/api/transactions/:id', ({ params }) => {
    const id = Number(params.id)
    const index = mockTransactions.findIndex((t) => t.id === id)
    if (index === -1) {
      return HttpResponse.json({ success: false, error: { message: '找不到該筆收支紀錄' } }, { status: 404 })
    }
    mockTransactions.splice(index, 1)
    return HttpResponse.json({ success: true })
  }),

  http.get('/api/transactions', ({ request }) => {
    const url = new URL(request.url)
    const startDate = url.searchParams.get('startDate')
    const endDate = url.searchParams.get('endDate')
    if (!startDate || !endDate) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    if (startDate > endDate) {
      return HttpResponse.json(
        { success: false, error: { message: '起始日期不可晚於結束日期' } },
        { status: 400 }
      )
    }
    const data = mockTransactions
      .filter((t) => t.date >= startDate && t.date <= endDate)
      .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
    return HttpResponse.json({ success: true, data })
  }),

  http.get('/api/transactions/pending-advance-payments', () => {
    const data = mockTransactions.filter((t) => t.advancePaymentAmount != null && t.advancePaymentStatus === 'pending')
    return HttpResponse.json({ success: true, data })
  }),

  http.post('/api/transactions/:id/settle-advance-payment', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as Partial<SettleAdvancePaymentInput>
    const transaction = mockTransactions.find((t) => t.id === id)
    if (!transaction) {
      return HttpResponse.json({ success: false, error: { message: '找不到該筆收支紀錄' } }, { status: 404 })
    }
    if (!body.date || !body.amount || !body.accountId) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    if (transaction.advancePaymentAmount == null) {
      return HttpResponse.json({ success: false, error: { message: '該筆交易非代墊款交易' } }, { status: 422 })
    }
    if (transaction.advancePaymentStatus === 'settled') {
      return HttpResponse.json({ success: false, error: { message: '該筆代墊款已結清' } }, { status: 422 })
    }
    if (body.amount !== transaction.advancePaymentAmount) {
      return HttpResponse.json(
        { success: false, error: { message: '還款金額與代墊金額不符，僅支援全額還款' } },
        { status: 422 }
      )
    }
    const account = mockAccounts.find((a) => a.id === body.accountId)
    if (!account) {
      return HttpResponse.json({ success: false, error: { message: '找不到該帳戶' } }, { status: 404 })
    }

    const settlementTransaction: Transaction = {
      id: nextId++,
      date: body.date,
      amount: body.amount,
      categoryId: null,
      accountId: body.accountId,
      type: '收入',
      note: null,
      isTransfer: false,
      transferGroupId: null,
      syncStatus: 'synced',
      cashPositionId: 9000 + nextId,
      advancePaymentAmount: null,
      advancePaymentStatus: null,
      settlementTransactionId: null,
    }
    mockTransactions.push(settlementTransaction)

    transaction.advancePaymentStatus = 'settled'
    transaction.settlementTransactionId = settlementTransaction.id

    return HttpResponse.json({
      success: true,
      data: { settlementTransaction, advancePaymentTransaction: transaction },
    })
  }),
]
