import { http, HttpResponse } from 'msw'
import type { CategorySummary, Transaction } from '@/lib/types'
import { mockCategories, mockTransactions } from '@/mocks/fixtures'

export const reportHandlers = [
  http.get('/api/reports/category-summary', ({ request }) => {
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

    const totals = new Map<number, number>()
    for (const t of mockTransactions) {
      if (t.isTransfer || t.type !== '支出') continue
      if (t.date < startDate || t.date > endDate) continue
      if (t.categoryId === null) continue
      totals.set(t.categoryId, (totals.get(t.categoryId) ?? 0) + t.amount)
    }

    const data: CategorySummary[] = Array.from(totals.entries())
      .map(([categoryId, totalAmount]) => ({
        category: mockCategories.find((c) => c.id === categoryId)?.name ?? '未知分類',
        totalAmount,
      }))
      .sort((a, b) => b.totalAmount - a.totalAmount)

    return HttpResponse.json({ success: true, data })
  }),

  http.get('/api/reports/category-detail', ({ request }) => {
    const url = new URL(request.url)
    const category = url.searchParams.get('category')
    const startDate = url.searchParams.get('startDate')
    const endDate = url.searchParams.get('endDate')
    if (!category || !startDate || !endDate) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    if (startDate > endDate) {
      return HttpResponse.json(
        { success: false, error: { message: '起始日期不可晚於結束日期' } },
        { status: 400 }
      )
    }

    const categoryId = mockCategories.find((c) => c.name === category)?.id

    const data: Transaction[] = mockTransactions
      .filter((t) => {
        if (t.isTransfer || t.type !== '支出') return false
        if (t.date < startDate || t.date > endDate) return false
        if (t.categoryId === null || t.categoryId !== categoryId) return false
        return true
      })
      .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))

    return HttpResponse.json({ success: true, data })
  }),
]
