import type { CategorySummary, Transaction } from '@/lib/types'
import { Amount } from '@/components/Amount'

export interface CategoryDetailState {
  loading: boolean
  error: string | null
  transactions: Transaction[]
}

const PALETTE = [
  '#2EE6A6', // mint
  '#FF6A5E', // coral
  '#FFC24B', // amber
  '#9B8CFF', // violet
  '#4DB8FF', // sky
  '#FF8FB3', // rose
  '#6FCF97', // sage
  '#C9A0FF', // lavender
  '#FF9F5A', // tangerine
  '#5CE1E6', // cyan
]

export function CategoryPieChart({
  data,
  onCategoryClick,
  expandedCategory,
  detail,
  accountName,
}: {
  data: CategorySummary[]
  onCategoryClick?: (category: string) => void
  expandedCategory?: string | null
  detail?: CategoryDetailState | null
  accountName?: (accountId: number) => string
}) {
  const total = data.reduce((sum, d) => sum + d.totalAmount, 0)
  const size = 220
  const strokeWidth = 32
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  let cumulative = 0

  return (
    <div className="flex flex-col items-center gap-6">
      <div className="relative shrink-0" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#1C2028" strokeWidth={strokeWidth} />
          {data.map((d, i) => {
            const fraction = total > 0 ? d.totalAmount / total : 0
            const dash = fraction * circumference
            const dashOffset = -cumulative
            cumulative += dash
            return (
              <circle
                key={d.category}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={PALETTE[i % PALETTE.length]}
                strokeWidth={strokeWidth}
                strokeDasharray={`${dash} ${circumference - dash}`}
                strokeDashoffset={dashOffset}
              />
            )
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[10px] font-medium uppercase tracking-widest text-ink-soft/50">本月支出</span>
          <span className="font-mono text-2xl text-ink tabular-nums">{total.toLocaleString()}</span>
        </div>
      </div>

      <ul className="w-full space-y-2" data-testid="category-summary-list">
        {data.map((d, i) => {
          const isExpanded = expandedCategory === d.category
          return (
            <li key={d.category}>
              <button
                type="button"
                data-testid="category-summary-row"
                aria-expanded={isExpanded}
                onClick={() => onCategoryClick?.(d.category)}
                className="flex w-full items-center justify-between rounded-xl border border-line bg-surface px-4 py-2.5 shadow-card transition-colors hover:border-mint/40 active:scale-[0.99]"
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
                  />
                  <span className="text-sm text-ink">{d.category}</span>
                </div>
                <div className="flex items-center gap-2 font-mono text-sm tabular-nums">
                  <span className="text-ink-soft/50">
                    {total > 0 ? Math.round((d.totalAmount / total) * 100) : 0}%
                  </span>
                  <span className="text-ink">{d.totalAmount.toLocaleString()}</span>
                </div>
              </button>

              {isExpanded && (
                <div
                  data-testid={`category-detail-${d.category}`}
                  className="mt-2 rounded-xl border border-line bg-surface-high px-3 py-3"
                >
                  {detail?.loading ? (
                    <p className="py-6 text-center text-sm text-ink-soft/50">載入中…</p>
                  ) : detail?.error ? (
                    <p
                      className="rounded-lg border border-coral/30 bg-coral-dim px-3 py-2 text-sm text-coral"
                      role="alert"
                    >
                      {detail.error}
                    </p>
                  ) : detail && detail.transactions.length === 0 ? (
                    <p
                      data-testid="category-detail-empty-state"
                      className="py-6 text-center text-sm text-ink-soft/40"
                    >
                      這段期間沒有{d.category}的紀錄
                    </p>
                  ) : (
                    <ul className="space-y-2" data-testid="category-detail-list">
                      {detail?.transactions.map((t) => (
                        <li
                          key={t.id}
                          data-testid={`category-detail-row-${t.id}`}
                          className="flex items-start justify-between gap-3 rounded-lg border border-line bg-surface px-3 py-2.5"
                        >
                          <p className="text-sm text-ink">
                            {d.category} · {t.date}
                            {t.note ? ` · ${t.note}` : ''}
                          </p>
                          <div className="shrink-0 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              <Amount value={t.amount} type={t.type} className="text-sm" />
                              {t.advancePaymentAmount != null && (
                                <span
                                  data-testid={`category-detail-advance-badge-${t.id}`}
                                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                                    t.advancePaymentStatus === 'settled'
                                      ? 'bg-mint-dim text-mint'
                                      : 'bg-coral-dim text-coral'
                                  }`}
                                >
                                  代墊 ${t.advancePaymentAmount.toLocaleString()} ·{' '}
                                  {t.advancePaymentStatus === 'settled' ? '已收回' : '待收回'}
                                </span>
                              )}
                            </div>
                            <p className="mt-0.5 text-xs text-ink-soft/50">
                              {accountName ? accountName(t.accountId) : `#${t.accountId}`}
                            </p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
