import { apiClient } from '@/lib/api/client'
import type { CloudInvoice, CloudInvoiceHealth, CloudInvoiceSyncResult, ConfirmCloudInvoiceInput } from '@/lib/types'

export async function listPendingCloudInvoices(): Promise<CloudInvoice[]> {
  return apiClient<CloudInvoice[]>('/cloud-invoices/pending')
}

export async function confirmCloudInvoice(id: number, input: ConfirmCloudInvoiceInput): Promise<CloudInvoice> {
  return apiClient<CloudInvoice>(`/cloud-invoices/${id}/confirm`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function getCloudInvoiceHealth(): Promise<CloudInvoiceHealth> {
  return apiClient<CloudInvoiceHealth>('/cloud-invoices/health')
}

// syncCloudInvoices 由 Hermes 呼叫，不是網頁操作，這裡仍提供 client function 供未來測試/除錯用
export async function syncCloudInvoices(items: unknown[]): Promise<CloudInvoiceSyncResult[]> {
  return apiClient<CloudInvoiceSyncResult[]>('/cloud-invoices/sync', {
    method: 'POST',
    body: JSON.stringify(items),
  })
}
