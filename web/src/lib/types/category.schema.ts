import { z } from 'zod'

export const CategoryTypeSchema = z.enum(['收入', '支出', '皆可'])
export type CategoryType = z.infer<typeof CategoryTypeSchema>

export const CategorySchema = z.object({
  id: z.number(),
  name: z.string(),
  type: CategoryTypeSchema,
})
export type Category = z.infer<typeof CategorySchema>

export const CategoryInputSchema = z.object({
  name: z.string().min(1),
  type: CategoryTypeSchema,
})
export type CategoryInput = z.infer<typeof CategoryInputSchema>
