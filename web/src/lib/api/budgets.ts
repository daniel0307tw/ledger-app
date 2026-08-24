import { apiClient } from '@/lib/api/client'
import type { Budget, BudgetInput, BudgetStatus, BudgetUpdateInput } from '@/lib/types'

export async function createBudget(input: BudgetInput): Promise<Budget> {
  return apiClient<Budget>('/budgets', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listBudgets(): Promise<Budget[]> {
  return apiClient<Budget[]>('/budgets')
}

export async function getBudgetStatus(): Promise<BudgetStatus[]> {
  return apiClient<BudgetStatus[]>('/budgets/status')
}

export async function updateBudget(id: number, input: BudgetUpdateInput): Promise<Budget> {
  return apiClient<Budget>(`/budgets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export async function deleteBudget(id: number): Promise<void> {
  await apiClient<void>(`/budgets/${id}`, { method: 'DELETE' })
}
