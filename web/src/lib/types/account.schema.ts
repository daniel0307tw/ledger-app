import { z } from 'zod'

export const AccountTypeSchema = z.enum(['一般帳戶', '信用卡'])
export type AccountType = z.infer<typeof AccountTypeSchema>

export const AccountSchema = z.object({
  id: z.number(),
  name: z.string(),
  type: AccountTypeSchema,
  balance: z.number(),
})
export type Account = z.infer<typeof AccountSchema>

export const AccountInputSchema = z.object({
  name: z.string().min(1),
  type: AccountTypeSchema,
})
export type AccountInput = z.infer<typeof AccountInputSchema>
