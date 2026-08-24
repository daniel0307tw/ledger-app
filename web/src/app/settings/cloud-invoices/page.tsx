'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { confirmCloudInvoice, getCloudInvoiceHealth, listPendingCloudInvoices } from '@/lib/api'
import type { CloudInvoice, CloudInvoiceHealth } from '@/lib/types'

export default function CloudInvoicesPage() {
  const [pending, setPending] = useState<CloudInvoice[]>([])
  const [health, setHealth] = useState<CloudInvoiceHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null)

  function refresh() {
    setLoading(true)
    Promise.all([listPendingCloudInvoices(), getCloudInvoiceHealth()])
      .then(([p, h]) => {
        setPending(p)
        setHealth(h)
      })
      .catch((e) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleConfirm(id: number, decision: 'confirm_new' | 'confirm_duplicate') {
    setBusyId(id)
    setError(null)
    try {
      await confirmCloudInvoice(id, { decision })
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '處理失敗')
    } finally {
      setBusyId(null)
    }
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <Link href="/settings" className="text-xs text-ink-soft/50">
          ← 設定
        </Link>
        <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink">
          雲端發票<span className="text-mint">.</span>
        </h1>
      </header>

      <section className="px-5 pt-5">
        <p className="mb-2 text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">同步健康狀態</p>
        {health && (
          <div data-testid="cloud-invoice-health" className="rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card">
            {!health.hasSyncHistory ? (
              <p className="text-sm text-ink-soft/40">尚無同步紀錄</p>
            ) : (
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="font-mono text-lg tabular-nums text-ink">{health.syncedCount}</p>
                  <p className="text-[10px] text-ink-soft/50">已同步</p>
                </div>
                <div>
                  <p className="font-mono text-lg tabular-nums text-ink">{health.pendingCount}</p>
                  <p className="text-[10px] text-ink-soft/50">待確認</p>
                </div>
                <div>
                  <p className={`font-mono text-lg tabular-nums ${health.errorCount > 0 ? 'text-coral' : 'text-ink'}`}>
                    {health.errorCount}
                  </p>
                  <p className="text-[10px] text-ink-soft/50">資料錯誤</p>
                </div>
              </div>
            )}
          </div>
        )}

        <p className="mb-2 mt-6 text-[11px] font-medium uppercase tracking-widest text-ink-soft/50">
          待確認清單{pending.length > 0 && `（${pending.length}）`}
        </p>
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : pending.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            沒有待確認的發票
          </p>
        ) : (
          <ul className="space-y-2" data-testid="pending-cloud-invoice-list">
            {pending.map((invoice) => (
              <li
                key={invoice.id}
                data-testid={`pending-cloud-invoice-${invoice.id}`}
                className="rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-ink">{invoice.sellerName}</p>
                    <p className="text-xs text-ink-soft/50">
                      {invoice.invoiceDate} · {invoice.invoiceNumber}
                    </p>
                  </div>
                  <p className="font-mono text-base tabular-nums text-ink">${invoice.amount.toLocaleString()}</p>
                </div>
                {invoice.similarTransaction && (
                  <p className="mt-2 rounded-xl bg-surface-high px-3 py-2 text-xs text-ink-soft/60">
                    可能重複：{invoice.similarTransaction.date} 已有一筆 ${invoice.similarTransaction.amount.toLocaleString()}{' '}
                    的紀錄{invoice.similarTransaction.note ? `（${invoice.similarTransaction.note}）` : ''}
                  </p>
                )}
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => handleConfirm(invoice.id, 'confirm_new')}
                    disabled={busyId === invoice.id}
                    data-testid={`confirm-new-${invoice.id}`}
                    className="flex-1 rounded-xl bg-mint py-2 text-xs font-semibold text-void disabled:opacity-50"
                  >
                    確認為新交易
                  </button>
                  <button
                    onClick={() => handleConfirm(invoice.id, 'confirm_duplicate')}
                    disabled={busyId === invoice.id}
                    data-testid={`confirm-duplicate-${invoice.id}`}
                    className="flex-1 rounded-xl border border-line py-2 text-xs text-ink-soft/70 disabled:opacity-50"
                  >
                    這是重複的
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        {error && (
          <p role="alert" className="mt-3 rounded-xl border border-coral/30 bg-coral-dim px-4 py-3 text-sm text-coral">
            {error}
          </p>
        )}
      </section>
    </main>
  )
}
