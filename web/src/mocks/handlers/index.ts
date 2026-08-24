import type { RequestHandler } from 'msw'
// Worker adds per-resource handler imports here:
import { accountHandlers } from './accounts'
import { budgetHandlers } from './budgets'
import { categoryHandlers } from './categories'
import { cloudInvoiceHandlers } from './cloud-invoices'
import { netWorthHandlers } from './net-worth'
import { recurringTransactionHandlers } from './recurring-transactions'
import { reportHandlers } from './reports'
import { transactionHandlers } from './transactions'
import { transferHandlers } from './transfers'

export const handlers: RequestHandler[] = [
  // Worker adds handler spreads here:
  ...accountHandlers,
  ...budgetHandlers,
  ...categoryHandlers,
  ...cloudInvoiceHandlers,
  ...netWorthHandlers,
  ...recurringTransactionHandlers,
  ...reportHandlers,
  ...transactionHandlers,
  ...transferHandlers,
]
