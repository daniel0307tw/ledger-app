import { z } from 'zod'

export const TransferInputSchema = z.object({
  fromAccountId: z.number(),
  toAccountId: z.number(),
  amount: z.number().positive(),
  date: z.string(),
})
export type TransferInput = z.infer<typeof TransferInputSchema>
