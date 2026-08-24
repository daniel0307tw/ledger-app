import { apiClient } from '@/lib/api/client'
import type { Category, CategoryInput } from '@/lib/types'

export async function createCategory(input: CategoryInput): Promise<Category> {
  return apiClient<Category>('/categories', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listCategories(): Promise<Category[]> {
  return apiClient<Category[]>('/categories')
}
