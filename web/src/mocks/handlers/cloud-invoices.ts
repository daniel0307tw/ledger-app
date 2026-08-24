import { http, HttpResponse } from 'msw'
import type { CloudInvoice, ConfirmCloudInvoiceInput } from '@/lib/types'
import { mockCloudInvoices } from '@/mocks/fixtures'

export const cloudInvoiceHandlers = [
  http.get('/api/cloud-invoices/pending', () => {
    const data = mockCloudInvoices.filter((i) => i.status === 'pending_review')
    return HttpResponse.json({ success: true, data })
  }),

  http.post('/api/cloud-invoices/:id/confirm', async ({ request, params }) => {
    const id = Number(params.id)
    const invoice = mockCloudInvoices.find((i) => i.id === id)
    if (!invoice) {
      return HttpResponse.json({ success: false, error: { message: '找不到該筆雲端發票' } }, { status: 404 })
    }
    if (invoice.status !== 'pending_review') {
      return HttpResponse.json({ success: false, error: { message: '此筆發票已處理過' } }, { status: 422 })
    }
    const body = (await request.json()) as ConfirmCloudInvoiceInput
    const updated: CloudInvoice =
      body.decision === 'confirm_duplicate'
        ? { ...invoice, status: 'skipped' }
        : { ...invoice, status: 'synced', transactionId: 999 }
    Object.assign(invoice, updated)
    return HttpResponse.json({ success: true, data: updated })
  }),

  http.get('/api/cloud-invoices/health', () => {
    const pendingCount = mockCloudInvoices.filter((i) => i.status === 'pending_review').length
    const syncedCount = mockCloudInvoices.filter((i) => i.status === 'synced').length
    return HttpResponse.json({
      success: true,
      data: {
        hasSyncHistory: mockCloudInvoices.length > 0,
        lastSyncedAt: mockCloudInvoices.length > 0 ? '2026-08-21T10:00:00' : null,
        pendingCount,
        syncedCount,
        errorCount: 0,
      },
    })
  }),
]
