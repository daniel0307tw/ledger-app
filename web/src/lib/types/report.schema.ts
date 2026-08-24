import { z } from 'zod'

export const CategorySummarySchema = z.object({
  category: z.string(),
  totalAmount: z.number(),
})
export type CategorySummary = z.infer<typeof CategorySummarySchema>
