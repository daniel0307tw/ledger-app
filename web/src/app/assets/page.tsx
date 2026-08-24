'use client'

import { useEffect, useState } from 'react'
import { getNetWorth, refreshNetWorth } from '@/lib/api'
import type { NetWorth } from '@/lib/types'
import { BottomNav } from '@/components/BottomNav'
import { PullToRefresh } from '@/components/PullToRefresh'

export default function AssetsPage() {
  const [netWorth, setNetWorth] = useState<NetWorth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getNetWorth()
      .then((data) => !cancelled && setNetWorth(data))
      .catch((e) => !cancelled && setError(e.message ?? '載入失敗'))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [])

  async function handlePullRefresh() {
    setError(null)
    try {
      const data = await refreshNetWorth()
      setNetWorth(data)
    } catch (e: any) {
      setError(e.message ?? '刷新失敗')
    }
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <h1 className="font-display text-2xl font-bold tracking-tight text-ink">
          資產<span className="text-mint">.</span>
        </h1>
      </header>

      <PullToRefresh onRefresh={handlePullRefresh}>
      {error && (
        <p className="mx-5 mt-4 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral" role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className="py-16 text-center text-sm text-ink-soft/50">載入中…</p>
      ) : netWorth ? (
        <>
          <section className="px-5 pt-5">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">總資產（依幣別）</p>
            <div className="flex gap-3" data-testid="currency-totals">
              {netWorth.currencyTotals.length === 0 ? (
                <p className="flex-1 rounded-2xl border border-dashed border-line py-6 text-center text-sm text-ink-soft/40">
                  尚無任何資產
                </p>
              ) : (
                netWorth.currencyTotals.map((c) => (
                  <div
                    key={c.currency}
                    data-testid={`currency-total-${c.currency}`}
                    className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 shadow-card"
                  >
                    <p className="text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">{c.currency}</p>
                    <p className={`font-mono text-lg tabular-nums ${c.total < 0 ? 'text-coral' : 'text-ink'}`}>
                      {c.total < 0 ? '-' : ''}
                      {Math.abs(c.total).toLocaleString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="px-5 pt-5">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">現金與信用卡</p>
            <div className="flex gap-3">
              <div className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 shadow-card">
                <p className="text-[11px] text-ink-soft/50">現金餘額</p>
                <p className="font-mono text-lg tabular-nums text-mint" data-testid="cash-total">
                  {netWorth.cashTotal.toLocaleString()}
                </p>
              </div>
              <div className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 shadow-card">
                <p className="text-[11px] text-ink-soft/50">信用卡未繳</p>
                <p
                  className={`font-mono text-lg tabular-nums ${netWorth.creditCardDebtTotal < 0 ? 'text-coral' : 'text-ink'}`}
                  data-testid="credit-card-debt-total"
                >
                  {netWorth.creditCardDebtTotal.toLocaleString()}
                </p>
              </div>
            </div>
          </section>

          <section className="px-5 pt-5">
            <p className="mb-2 text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">股票持倉</p>

            {netWorth.stockDataStatus === 'failed' && (
              <p
                data-testid="stock-data-failed"
                role="alert"
                className="mb-2 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral"
              >
                股票資料查詢失敗，暫時無法顯示
              </p>
            )}

            {netWorth.stockDataStatus === 'ok' && netWorth.stockHoldings.length === 0 ? (
              <p
                data-testid="no-holdings"
                className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40"
              >
                尚無持股
              </p>
            ) : (
              <ul className="space-y-2" data-testid="stock-holdings">
                {netWorth.stockHoldings.map((h) => (
                  <li
                    key={`${h.currency}-${h.symbol}`}
                    className="flex items-center justify-between rounded-2xl border border-line bg-surface px-4 py-3 shadow-card"
                  >
                    <div>
                      <p className="text-sm text-ink">
                        {h.symbol} <span className="text-ink-soft/50">{h.name}</span>
                      </p>
                      <p className="text-xs text-ink-soft/40">{h.currency}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono text-sm tabular-nums text-ink">{h.marketValue.toLocaleString()}</p>
                      <p className={`font-mono text-xs tabular-nums ${h.unrealizedPnl >= 0 ? 'text-mint' : 'text-coral'}`}>
                        {h.unrealizedPnl >= 0 ? '+' : ''}
                        {h.unrealizedPnl.toLocaleString()}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      ) : null}
      </PullToRefresh>

      <BottomNav />
    </main>
  )
}
