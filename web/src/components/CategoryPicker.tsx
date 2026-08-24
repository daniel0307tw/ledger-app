'use client'

import { useEffect, useRef, useState } from 'react'
import { createCategory, listCategories } from '@/lib/api'
import type { Category } from '@/lib/types'

export function CategoryPicker({
  value,
  onChange,
  transactionType,
}: {
  value: number | ''
  onChange: (categoryId: number) => void
  transactionType: '收入' | '支出'
}) {
  const [allCategories, setAllCategories] = useState<Category[]>([])
  const [open, setOpen] = useState(false)
  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const lastCloseAt = useRef(0)

  function close() {
    lastCloseAt.current = Date.now()
    setOpen(false)
  }

  function openSheet() {
    // 手機瀏覽器在關閉彈出層的同一個觸控手勢裡，偶爾會讓底下剛顯露出來的觸發按鈕
    // 也收到一次「幽靈點擊」，導致彈出層關閉後又立刻被重新打開。這裡用一個很短的
    // 冷卻時間擋掉緊接在「剛關閉」之後的觸發，實測能解決手機上分類選擇器點了沒反應/關不掉的問題。
    if (Date.now() - lastCloseAt.current < 400) return
    setOpen(true)
  }

  useEffect(() => {
    listCategories().then(setAllCategories).catch(() => {})
  }, [])

  const categories = allCategories.filter((c) => c.type === '皆可' || c.type === transactionType)

  useEffect(() => {
    if (!open) return
    // iOS Safari 不會確實遵守 body { overflow: hidden }（背景仍可被觸控捲動），
    // 導致底下表單「偷走」原本要傳給彈出層按鈕的觸控事件，看起來像是按鈕整個沒反應。
    // 改用 position: fixed 鎖定 body 才是 iOS Safari 上可靠的做法。
    const scrollY = window.scrollY
    const body = document.body
    const previous = {
      position: body.style.position,
      top: body.style.top,
      width: body.style.width,
      overflow: body.style.overflow,
    }
    body.style.position = 'fixed'
    body.style.top = `-${scrollY}px`
    body.style.width = '100%'
    body.style.overflow = 'hidden'
    return () => {
      body.style.position = previous.position
      body.style.top = previous.top
      body.style.width = previous.width
      body.style.overflow = previous.overflow
      window.scrollTo(0, scrollY)
    }
  }, [open])

  const selected = allCategories.find((c) => c.id === value)

  function pick(id: number) {
    onChange(id)
    close()
    setNewName('')
    setError(null)
  }

  async function handleCreate() {
    if (!newName.trim()) return
    setCreating(true)
    setError(null)
    try {
      const category = await createCategory({ name: newName.trim(), type: transactionType })
      setAllCategories((prev) => [...prev, category])
      pick(category.id)
    } catch (err: any) {
      setError(err?.message ?? '新增分類失敗')
    } finally {
      setCreating(false)
    }
  }

  return (
    <>
      <button
        type="button"
        data-testid="category-picker-trigger"
        onClick={openSheet}
        className="flex w-full items-center justify-between rounded-2xl border border-line bg-surface px-4 py-3 text-left outline-none focus:border-mint"
      >
        <span className={selected ? 'text-ink' : 'text-ink-soft/40'}>{selected ? selected.name : '請選擇分類'}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="shrink-0 text-ink-soft/50">
          <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
          <button
            type="button"
            aria-label="關閉"
            onClick={close}
            className="absolute inset-0 bg-void-deep/70"
          />
          <div
            data-testid="category-picker-sheet"
            className="relative mx-auto flex max-h-[75dvh] w-full max-w-md flex-col rounded-t-3xl border-t border-line bg-surface shadow-card"
          >
            <div className="flex shrink-0 items-center justify-between px-5 pb-2 pt-4">
              <h2 className="font-display text-lg font-semibold text-ink">選擇分類</h2>
              <button
                type="button"
                aria-label="關閉"
                onClick={close}
                className="flex h-8 w-8 items-center justify-center rounded-full text-ink-soft/60 hover:bg-surface-high hover:text-ink"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-5 py-3">
              <div className="flex flex-wrap gap-2">
                {categories.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    data-testid={`category-option-${c.id}`}
                    onClick={() => pick(c.id)}
                    className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                      c.id === value ? 'bg-mint text-void' : 'bg-surface-high text-ink hover:bg-line'
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>

            {/* 不能用 <form>：這個元件會被嵌在 TransactionForm 的外層 <form> 裡，
                巢狀 form 不合法 HTML，瀏覽器會打亂 DOM 結構導致提交行為失常。 */}
            <div className="flex gap-2 border-t border-line px-5 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
              <input
                data-testid="new-category-name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleCreate()
                  }
                }}
                placeholder="新增分類…"
                className="flex-1 rounded-2xl border border-line bg-void px-4 py-2.5 text-ink placeholder:text-ink-soft/40 outline-none focus:border-mint"
              />
              <button
                type="button"
                data-testid="create-category-inline"
                onClick={handleCreate}
                disabled={creating || !newName.trim()}
                className="rounded-2xl bg-mint px-4 py-2.5 text-sm font-semibold text-void shadow-glow-mint disabled:opacity-40"
              >
                {creating ? '新增中…' : '新增'}
              </button>
            </div>
            {error && (
              <p role="alert" className="px-5 pb-4 text-sm text-coral">
                {error}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  )
}
