import { z } from 'zod'

export const BudgetScopeSchema = z.enum(['總預算', '分類預算'])
export type BudgetScope = z.infer<typeof BudgetScopeSchema>

export const BudgetInputSchema = z.object({
  scope: BudgetScopeSchema,
  categoryId: z.number().nullable().optional(),
  monthlyAmount: z.number().positive(),
})
export type BudgetInput = z.infer<typeof BudgetInputSchema>

export const BudgetUpdateInputSchema = z.object({
  monthlyAmount: z.number().positive(),
})
export type BudgetUpdateInput = z.infer<typeof BudgetUpdateInputSchema>

export const BudgetSchema = z.object({
  id: z.number(),
  scope: BudgetScopeSchema,
  categoryId: z.number().nullable(),
  monthlyAmount: z.number(),
})
export type Budget = z.infer<typeof BudgetSchema>

export const BudgetStatusSchema = z.object({
  id: z.number(),
  scope: BudgetScopeSchema,
  categoryId: z.number().nullable(),
  monthlyAmount: z.number(),
  spent: z.number(),
  remaining: z.number(),
  isOverBudget: z.boolean(),
})
export type BudgetStatus = z.infer<typeof BudgetStatusSchema>
