import { http, HttpResponse } from 'msw'
import type { Category, CategoryInput } from '@/lib/types'
import { mockCategories } from '@/mocks/fixtures'

let nextId = mockCategories.length + 1

export const categoryHandlers = [
  http.post('/api/categories', async ({ request }) => {
    const body = (await request.json()) as Partial<CategoryInput>
    if (!body.name || !body.type) {
      return HttpResponse.json({ success: false, error: { message: '必要參數未提供' } }, { status: 400 })
    }
    const category: Category = { id: nextId++, name: body.name, type: body.type }
    mockCategories.push(category)
    return HttpResponse.json({ success: true, data: category }, { status: 201 })
  }),

  http.get('/api/categories', () => {
    return HttpResponse.json({ success: true, data: mockCategories })
  }),
]
