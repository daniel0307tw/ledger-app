import type {
  Account,
  Budget,
  BudgetStatus,
  Category,
  CloudInvoice,
  NetWorth,
  RecurringTransaction,
  Transaction,
} from '@/lib/types'

// 資料取自 tests/features/{accounts,transactions,categories}/*.feature 的 Given 步驟具體範例，不憑空編造。

export const mockAccounts: Account[] = [
  { id: 1, name: '永豐銀行', type: '一般帳戶', balance: 0 },
  { id: 2, name: '新光銀行', type: '一般帳戶', balance: 0 },
]

// 與後端 alembic migration 003 的 20 個預設分類 seed data 一致（順序也一致，id 依序遞增）。
export const mockCategories: Category[] = [
  { id: 1, name: '餐飲', type: '支出' },
  { id: 2, name: '日常用品', type: '支出' },
  { id: 3, name: '交通', type: '支出' },
  { id: 4, name: '水電瓦斯', type: '支出' },
  { id: 5, name: '電話網路', type: '支出' },
  { id: 6, name: '居家', type: '支出' },
  { id: 7, name: '服飾', type: '支出' },
  { id: 8, name: '汽車', type: '支出' },
  { id: 9, name: '娛樂', type: '支出' },
  { id: 10, name: '美容美髮', type: '支出' },
  { id: 11, name: '交際應酬', type: '支出' },
  { id: 12, name: '學習深造', type: '支出' },
  { id: 13, name: '保險', type: '支出' },
  { id: 14, name: '稅金', type: '支出' },
  { id: 15, name: '醫療', type: '支出' },
  { id: 16, name: '校正回歸', type: '皆可' },
  { id: 17, name: '轉帳手續費', type: '支出' },
  { id: 18, name: '薪資', type: '收入' },
  { id: 19, name: '獎金', type: '收入' },
  { id: 20, name: '投資', type: '收入' },
]

// 取自 tests/features/assets/查詢資產總覽.feature 的 Given 具體範例（永豐銀行現金 30000、
// 台新信用卡負債 -8000、台股 2330 台積電市值 150000、美股 AAPL 市值 5000）。
export const mockNetWorth: NetWorth = {
  cashTotal: 30000,
  creditCardDebtTotal: -8000,
  stockHoldings: [
    { currency: 'TWD', symbol: '2330', name: '台積電', marketValue: 150000, unrealizedPnl: 20000 },
    { currency: 'USD', symbol: 'AAPL', name: '蘋果', marketValue: 5000, unrealizedPnl: 500 },
  ],
  currencyTotals: [
    { currency: 'TWD', total: 172000 },
    { currency: 'USD', total: 5000 },
  ],
  stockDataStatus: 'ok',
}

export const mockTransactions: Transaction[] = [
  {
    id: 1,
    date: '2026-01-10',
    amount: 500,
    categoryId: 1,
    accountId: 1,
    type: '支出',
    note: null,
    isTransfer: false,
    transferGroupId: null,
    syncStatus: 'synced',
    cashPositionId: 101,
    advancePaymentAmount: null,
    advancePaymentStatus: null,
    settlementTransactionId: null,
  },
  {
    id: 2,
    date: '2026-01-20',
    amount: 800,
    categoryId: 3,
    accountId: 1,
    type: '支出',
    note: null,
    isTransfer: false,
    transferGroupId: null,
    syncStatus: 'synced',
    cashPositionId: 102,
    advancePaymentAmount: null,
    advancePaymentStatus: null,
    settlementTransactionId: null,
  },
  {
    id: 3,
    date: '2026-01-05',
    amount: 4000,
    categoryId: 1,
    accountId: 1,
    type: '支出',
    note: '聚餐',
    isTransfer: false,
    transferGroupId: null,
    syncStatus: 'synced',
    cashPositionId: 103,
    advancePaymentAmount: null,
    advancePaymentStatus: null,
    settlementTransactionId: null,
  },
  // 取自 tests/features/transactions/查詢待收回代墊款清單.feature 的 Given 具體範例（未結清代墊款，
  // 總金額 4000、代墊 3000，混合情境：自己吃了 1000、代墊 3000）。
  {
    id: 4,
    date: '2026-08-05',
    amount: 4000,
    categoryId: 1,
    accountId: 1,
    type: '支出',
    note: null,
    isTransfer: false,
    transferGroupId: null,
    syncStatus: 'synced',
    cashPositionId: 104,
    advancePaymentAmount: 3000,
    advancePaymentStatus: 'pending',
    settlementTransactionId: null,
  },
  // 與 id 4 同月同分類（餐飲、2026-08），讓分類花費明細點開後同時看得到「備註」與「代墊款標記」兩種情境。
  {
    id: 5,
    date: '2026-08-12',
    amount: 320,
    categoryId: 1,
    accountId: 2,
    type: '支出',
    note: '早餐',
    isTransfer: false,
    transferGroupId: null,
    syncStatus: 'synced',
    cashPositionId: 105,
    advancePaymentAmount: null,
    advancePaymentStatus: null,
    settlementTransactionId: null,
  },
]

// 取自 tests/features/cloud-invoices/查詢待確認雲端發票清單.feature 的 Given 具體範例。
export const mockCloudInvoices: CloudInvoice[] = [
  {
    id: 1,
    invoiceNumber: 'AB-11111111',
    invoiceDate: '2026-08-19',
    amount: 200,
    sellerName: '全家便利商店',
    itemSummary: null,
    status: 'pending_review',
    transactionId: null,
    similarTransaction: null,
  },
]

// 取自 tests/features/recurring-transactions/查詢固定收支規則列表.feature 的 Given 具體範例。
export const mockRecurringTransactions: RecurringTransaction[] = [
  {
    id: 1,
    frequency: '每月',
    amount: 15000,
    categoryId: 6,
    accountId: 1,
    type: '支出',
    note: null,
    startDate: '2026-09-05',
    generateCount: 3,
    status: '啟用',
  },
]

// 取自 tests/features/budgets/查詢預算列表.feature 的 Given 具體範例。
export const mockBudgets: Budget[] = [
  { id: 1, scope: '總預算', categoryId: null, monthlyAmount: 30000 },
  { id: 2, scope: '分類預算', categoryId: 1, monthlyAmount: 8000 },
]

// 取自 tests/features/budgets/查詢預算執行狀況.feature 的 Given/Then 具體範例。
export const mockBudgetStatus: BudgetStatus[] = [
  { id: 2, scope: '分類預算', categoryId: 1, monthlyAmount: 8000, spent: 3000, remaining: 5000, isOverBudget: false },
]
