import { apiClient } from '@/lib/api/client'
import type { NetWorth } from '@/lib/types'

export async function getNetWorth(): Promise<NetWorth> {
  return apiClient<NetWorth>('/net-worth')
}

// 會真的觸發 stock_analyzer 去外部股價 API 抓即時市價並落地保存快照（消耗 API 額度），
// 只給使用者主動要求更新時呼叫（例如下拉刷新），不要在頁面掛載時自動呼叫。
export async function refreshNetWorth(): Promise<NetWorth> {
  return apiClient<NetWorth>('/net-worth/refresh', { method: 'POST' })
}
