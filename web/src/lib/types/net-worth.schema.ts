import { z } from 'zod'

export const CurrencySchema = z.enum(['TWD', 'USD'])
export type Currency = z.infer<typeof CurrencySchema>

export const StockDataStatusSchema = z.enum(['ok', 'failed'])
export type StockDataStatus = z.infer<typeof StockDataStatusSchema>

export const StockHoldingSchema = z.object({
  currency: CurrencySchema,
  symbol: z.string(),
  name: z.string(),
  marketValue: z.number(),
  unrealizedPnl: z.number(),
})
export type StockHolding = z.infer<typeof StockHoldingSchema>

export const CurrencyTotalSchema = z.object({
  currency: CurrencySchema,
  total: z.number(),
})
export type CurrencyTotal = z.infer<typeof CurrencyTotalSchema>

export const NetWorthSchema = z.object({
  cashTotal: z.number(),
  creditCardDebtTotal: z.number(),
  stockHoldings: z.array(StockHoldingSchema),
  currencyTotals: z.array(CurrencyTotalSchema),
  stockDataStatus: StockDataStatusSchema,
})
export type NetWorth = z.infer<typeof NetWorthSchema>
