'use client'

import Link from 'next/link'
import { BottomNav } from '@/components/BottomNav'

const ENTRIES = [
  {
    href: '/transfer',
    title: '轉帳',
    desc: '帳戶間轉帳',
  },
  {
    href: '/settings/recurring-transactions',
    title: '固定收支',
    desc: '房租、訂閱等定期項目，自動提前生成',
  },
  {
    href: '/settings/budgets',
    title: '預算',
    desc: '設定每月總預算與各分類上限',
  },
  {
    href: '/settings/cloud-invoices',
    title: '雲端發票',
    desc: '待確認清單與自動同步健康狀態',
  },
  {
    href: '/transactions/pending-advance-payments',
    title: '待收回代墊款',
    desc: '查看尚未收回的代墊款並確認收到還款',
  },
]

export default function SettingsPage() {
  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <h1 className="font-display text-2xl font-bold tracking-tight text-ink">
          設定<span className="text-mint">.</span>
        </h1>
      </header>

      <section className="space-y-2 px-5 pt-5">
        {ENTRIES.map((entry) => (
          <Link
            key={entry.href}
            href={entry.href}
            data-testid={`settings-entry-${entry.href.split('/').pop()}`}
            className="flex items-center justify-between rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card transition-colors active:bg-surface-high"
          >
            <div>
              <p className="text-ink">{entry.title}</p>
              <p className="text-xs text-ink-soft/50">{entry.desc}</p>
            </div>
            <span className="text-ink-soft/40">→</span>
          </Link>
        ))}
      </section>

      <BottomNav />
    </main>
  )
}
