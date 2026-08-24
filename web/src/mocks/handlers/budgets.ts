import { http, HttpResponse } from 'msw'
import type { Budget, BudgetInput, BudgetUpdateInput } from '@/lib/types'
import { mockBudgetStatus, mockBudgets } from '@/mocks/fixtures'

let nextId = mockBudgets.length + 1

export const budgetHandlers = [
  http.post('/api/budgets', async ({ request }) => {
    const body = (await request.json()) as Partial<BudgetInput>
    if (!body.scope || !body.monthlyAmount) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    if (body.monthlyAmount <= 0) {
      return HttpResponse.json({ success: false, error: { message: '金額必須為正數' } }, { status: 400 })
    }
    if (body.scope === '總預算' && mockBudgets.some((b) => b.scope === '總預算')) {
      return HttpResponse.json({ success: false, error: { message: '總預算已存在' } }, { status: 422 })
    }
    if (body.scope === '分類預算' && mockBudgets.some((b) => b.categoryId === body.categoryId)) {
      return HttpResponse.json({ success: false, error: { message: '此分類已設定過預算' } }, { status: 422 })
    }
    const budget: Budget = {
      id: nextId++,
      scope: body.scope,
      categoryId: body.scope === '分類預算' ? (body.categoryId ?? null) : null,
      monthlyAmount: body.monthlyAmount,
    }
    mockBudgets.push(budget)
    return HttpResponse.json({ success: true, data: budget }, { status: 201 })
  }),

  http.get('/api/budgets', () => {
    return HttpResponse.json({ success: true, data: mockBudgets })
  }),

  http.get('/api/budgets/status', () => {
    return HttpResponse.json({ success: true, data: mockBudgetStatus })
  }),

  http.put('/api/budgets/:id', async ({ request, params }) => {
    const id = Number(params.id)
    const budget = mockBudgets.find((b) => b.id === id)
    if (!budget) {
      return HttpResponse.json({ success: false, error: { message: '找不到該預算' } }, { status: 404 })
    }
    const body = (await request.json()) as BudgetUpdateInput
    budget.monthlyAmount = body.monthlyAmount
    return HttpResponse.json({ success: true, data: budget })
  }),

  http.delete('/api/budgets/:id', ({ params }) => {
    const id = Number(params.id)
    const index = mockBudgets.findIndex((b) => b.id === id)
    if (index === -1) {
      return HttpResponse.json({ success: false, error: { message: '找不到該預算' } }, { status: 404 })
    }
    mockBudgets.splice(index, 1)
    return HttpResponse.json({ success: true })
  }),
]
