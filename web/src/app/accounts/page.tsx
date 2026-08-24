'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { createAccount, listAccounts } from '@/lib/api'
import type { Account } from '@/lib/types'
import { BottomNav } from '@/components/BottomNav'

const ACCOUNT_TYPES = ['一般帳戶', '信用卡'] as const

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [newName, setNewName] = useState('')
  const [newType, setNewType] = useState<(typeof ACCOUNT_TYPES)[number]>('一般帳戶')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function refresh() {
    setLoading(true)
    listAccounts()
      .then(setAccounts)
      .catch((e) => setError(e.message ?? '載入失敗'))
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return
    setCreating(true)
    setError(null)
    try {
      await createAccount({ name: newName.trim(), type: newType })
      setNewName('')
      refresh()
    } catch (err: any) {
      setError(err?.message ?? '建立失敗')
    } finally {
      setCreating(false)
    }
  }

  return (
    <main className="mx-auto min-h-dvh max-w-md pb-28">
      <header className="sticky top-0 z-10 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1.5rem+env(safe-area-inset-top))] backdrop-blur-xl">
        <h1 className="font-display text-2xl font-bold tracking-tight text-ink">
          帳戶<span className="text-mint">.</span>
        </h1>
        <Link
          href="/transfer"
          data-testid="go-transfer"
          className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-mint"
        >
          帳戶間轉帳 →
        </Link>
      </header>

      <section className="px-5 pt-5">
        {loading ? (
          <p className="py-8 text-center text-sm text-ink-soft/50">載入中…</p>
        ) : accounts.length === 0 ? (
          <p className="rounded-xl border border-dashed border-line py-8 text-center text-sm text-ink-soft/40">
            還沒有任何帳戶
          </p>
        ) : (
          <ul className="space-y-2" data-testid="account-list">
            {accounts.map((a) => (
              <li
                key={a.id}
                data-testid={`account-row-${a.id}`}
                className="flex items-center justify-between rounded-2xl border border-line bg-surface px-4 py-3.5 shadow-card"
              >
                <div>
                  <span className="text-ink">{a.name}</span>
                  <span className="ml-2 rounded-full bg-surface-high px-2 py-0.5 text-[10px] font-medium text-ink-soft/60">
                    {a.type}
                  </span>
                </div>
                <div className="text-right">
                  <div
                    data-testid={`account-balance-${a.id}`}
                    className={`font-mono text-base tabular-nums ${a.balance < 0 ? 'text-coral' : 'text-ink'}`}
                  >
                    {a.balance < 0 ? '-' : ''}${Math.abs(a.balance).toLocaleString()}
                  </div>
                  <div className="text-[10px] text-ink-soft/40">{a.type === '信用卡' ? '未繳金額' : '餘額'}</div>
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

        <form onSubmit={handleCreate} className="mt-6 space-y-2">
          <div className="grid grid-cols-2 gap-1.5 rounded-2xl border border-line bg-surface p-1.5">
            {ACCOUNT_TYPES.map((t) => (
              <button
                key={t}
                type="button"
                data-testid={`account-type-${t}`}
                onClick={() => setNewType(t)}
                className={`rounded-xl py-2.5 text-sm font-medium transition-all ${
                  newType === t ? 'bg-mint text-void shadow-glow-mint' : 'text-ink-soft/60'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              data-testid="new-account-name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="新增帳戶名稱"
              className="flex-1 rounded-2xl border border-line bg-surface px-4 py-3 text-ink placeholder:text-ink-soft/40 outline-none focus:border-mint"
            />
            <button
              type="submit"
              data-testid="create-account"
              disabled={creating}
              className="rounded-2xl bg-mint px-5 py-3 font-semibold text-void shadow-glow-mint disabled:opacity-50"
            >
              新增
            </button>
          </div>
        </form>
      </section>

      <BottomNav />
    </main>
  )
}
