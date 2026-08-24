'use client'

import { useRouter } from 'next/navigation'

export function PageHeader({ title }: { title: string }) {
  const router = useRouter()
  return (
    <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-line bg-void/85 px-5 pb-4 pt-[calc(1rem+env(safe-area-inset-top))] backdrop-blur-xl">
      <button
        aria-label="返回"
        onClick={() => router.back()}
        className="flex h-9 w-9 items-center justify-center rounded-full text-ink-soft/70 hover:bg-surface-high hover:text-ink active:scale-95"
      >
        ‹
      </button>
      <h1 className="font-display text-xl font-semibold text-ink">{title}</h1>
    </header>
  )
}
