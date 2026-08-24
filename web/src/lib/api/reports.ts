import { apiClient } from '@/lib/api/client'
import type { CategorySummary, Transaction } from '@/lib/types'

export async function getCategorySummary(startDate: string, endDate: string): Promise<CategorySummary[]> {
  const params = new URLSearchParams({ startDate, endDate })
  return apiClient<CategorySummary[]>(`/reports/category-summary?${params.toString()}`)
}

export async function getCategoryDetail(
  category: string,
  startDate: string,
  endDate: string
): Promise<Transaction[]> {
  const params = new URLSearchParams({ category, startDate, endDate })
  return apiClient<Transaction[]>(`/reports/category-detail?${params.toString()}`)
}
