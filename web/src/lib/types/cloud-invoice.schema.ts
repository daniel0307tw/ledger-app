import { z } from 'zod'

export const CloudInvoiceStatusSchema = z.enum(['pending_review', 'synced', 'skipped'])
export type CloudInvoiceStatus = z.infer<typeof CloudInvoiceStatusSchema>

export const CloudInvoiceSyncResultTypeSchema = z.enum(['created', 'pending_review', 'skipped', 'invalid'])
export type CloudInvoiceSyncResultType = z.infer<typeof CloudInvoiceSyncResultTypeSchema>

export const CloudInvoiceSyncResultSchema = z.object({
  invoiceNumber: z.string(),
  result: CloudInvoiceSyncResultTypeSchema,
  transactionId: z.number().nullable().optional(),
  errorMessage: z.string().nullable().optional(),
})
export type CloudInvoiceSyncResult = z.infer<typeof CloudInvoiceSyncResultSchema>

export const SimilarTransactionSchema = z.object({
  id: z.number(),
  date: z.string(),
  amount: z.number(),
  note: z.string().nullable(),
})
export type SimilarTransaction = z.infer<typeof SimilarTransactionSchema>

export const CloudInvoiceSchema = z.object({
  id: z.number(),
  invoiceNumber: z.string(),
  invoiceDate: z.string(),
  amount: z.number(),
  sellerName: z.string(),
  itemSummary: z.string().nullable(),
  status: CloudInvoiceStatusSchema,
  transactionId: z.number().nullable(),
  similarTransaction: SimilarTransactionSchema.nullable().optional(),
})
export type CloudInvoice = z.infer<typeof CloudInvoiceSchema>

export const ConfirmCloudInvoiceDecisionSchema = z.enum(['confirm_new', 'confirm_duplicate'])
export type ConfirmCloudInvoiceDecision = z.infer<typeof ConfirmCloudInvoiceDecisionSchema>

export const ConfirmCloudInvoiceInputSchema = z.object({
  decision: ConfirmCloudInvoiceDecisionSchema,
  accountId: z.number().optional(),
  categoryId: z.number().optional(),
})
export type ConfirmCloudInvoiceInput = z.infer<typeof ConfirmCloudInvoiceInputSchema>

export const CloudInvoiceHealthSchema = z.object({
  hasSyncHistory: z.boolean(),
  lastSyncedAt: z.string().nullable(),
  pendingCount: z.number(),
  syncedCount: z.number(),
  errorCount: z.number(),
})
export type CloudInvoiceHealth = z.infer<typeof CloudInvoiceHealthSchema>
