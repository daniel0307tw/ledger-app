import { z } from 'zod'

export const RecurringFrequencySchema = z.enum(['每天', '每週', '每月', '每季', '每年', '每三年'])
export type RecurringFrequency = z.infer<typeof RecurringFrequencySchema>

export const RecurringTransactionStatusSchema = z.enum(['啟用', '停用'])
export type RecurringTransactionStatus = z.infer<typeof RecurringTransactionStatusSchema>

export const RecurringTransactionInputSchema = z.object({
  frequency: RecurringFrequencySchema,
  amount: z.number().positive(),
  categoryId: z.number(),
  accountId: z.number(),
  type: z.enum(['收入', '支出']),
  note: z.string().optional(),
  startDate: z.string(),
  generateCount: z.number().int().positive(),
})
export type RecurringTransactionInput = z.infer<typeof RecurringTransactionInputSchema>

export const RecurringTransactionSchema = z.object({
  id: z.number(),
  frequency: RecurringFrequencySchema,
  amount: z.number(),
  categoryId: z.number(),
  accountId: z.number(),
  type: z.enum(['收入', '支出']),
  note: z.string().nullable(),
  startDate: z.string(),
  generateCount: z.number(),
  status: RecurringTransactionStatusSchema,
})
export type RecurringTransaction = z.infer<typeof RecurringTransactionSchema>

export const TransactionLikeSchema = z.object({
  id: z.number(),
  date: z.string(),
  amount: z.number(),
  categoryId: z.number().nullable(),
  accountId: z.number(),
  type: z.string(),
})

export const GenerateRecurringTransactionResultSchema = z.object({
  generatedCount: z.number(),
  transactions: z.array(TransactionLikeSchema),
})
export type GenerateRecurringTransactionResult = z.infer<typeof GenerateRecurringTransactionResultSchema>
