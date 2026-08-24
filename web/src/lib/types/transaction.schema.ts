import { z } from 'zod'

export const TransactionTypeSchema = z.enum(['收入', '支出'])
export type TransactionType = z.infer<typeof TransactionTypeSchema>

export const SyncStatusSchema = z.enum(['pending', 'synced', 'failed'])
export type SyncStatus = z.infer<typeof SyncStatusSchema>

export const AdvancePaymentStatusSchema = z.enum(['pending', 'settled']).nullable()
export type AdvancePaymentStatus = z.infer<typeof AdvancePaymentStatusSchema>

export const TransactionSchema = z.object({
  id: z.number(),
  date: z.string(),
  amount: z.number(),
  categoryId: z.number().nullable(),
  accountId: z.number(),
  type: TransactionTypeSchema,
  note: z.string().nullable(),
  isTransfer: z.boolean(),
  transferGroupId: z.string().nullable(),
  syncStatus: SyncStatusSchema,
  cashPositionId: z.number().nullable(),
  advancePaymentAmount: z.number().nullable(),
  advancePaymentStatus: AdvancePaymentStatusSchema,
  settlementTransactionId: z.number().nullable(),
})
export type Transaction = z.infer<typeof TransactionSchema>

export const TransactionInputSchema = z.object({
  date: z.string(),
  amount: z.number().positive(),
  categoryId: z.number(),
  accountId: z.number(),
  type: TransactionTypeSchema,
  note: z.string().optional(),
  advancePaymentAmount: z.number().positive().nullable().optional(),
})
export type TransactionInput = z.infer<typeof TransactionInputSchema>

export const SettleAdvancePaymentInputSchema = z.object({
  date: z.string(),
  amount: z.number().positive(),
  accountId: z.number(),
})
export type SettleAdvancePaymentInput = z.infer<typeof SettleAdvancePaymentInputSchema>

export const SettleAdvancePaymentResultSchema = z.object({
  settlementTransaction: TransactionSchema,
  advancePaymentTransaction: TransactionSchema,
})
export type SettleAdvancePaymentResult = z.infer<typeof SettleAdvancePaymentResultSchema>
