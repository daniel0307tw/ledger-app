import { http, HttpResponse } from 'msw'
import { mockNetWorth } from '@/mocks/fixtures'

export const netWorthHandlers = [
  http.get('/api/net-worth', () => {
    return HttpResponse.json({ success: true, data: mockNetWorth })
  }),
  http.post('/api/net-worth/refresh', () => {
    return HttpResponse.json({ success: true, data: mockNetWorth })
  }),
]
