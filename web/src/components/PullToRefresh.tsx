'use client'

import { useEffect, useRef, useState } from 'react'

const PULL_THRESHOLD = 64
const MAX_PULL = 96

export function PullToRefresh({
  onRefresh,
  children,
}: {
  onRefresh: () => Promise<void>
  children: React.ReactNode
}) {
  const [pullDistance, setPullDistance] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const startY = useRef<number | null>(null)
  const pulling = useRef(false)
  // 用來讓 touchend 判斷是否達到觸發門檻，不依賴 state（避免閉包抓到過期的值）
  const pullDistanceRef = useRef(0)
  const refreshingRef = useRef(false)

  useEffect(() => {
    const el = containerRef.current
    if (!el) return

    function handleTouchStart(e: TouchEvent) {
      if (refreshingRef.current) return
      if (window.scrollY > 0) return
      startY.current = e.touches[0].clientY
      pulling.current = true
    }

    function handleTouchMove(e: TouchEvent) {
      if (!pulling.current || startY.current === null) return
      const delta = e.touches[0].clientY - startY.current
      if (delta <= 0) {
        pullDistanceRef.current = 0
        setPullDistance(0)
        return
      }
      if (window.scrollY > 0) {
        pulling.current = false
        pullDistanceRef.current = 0
        setPullDistance(0)
        return
      }
      // 手勢確實是「在頁面頂端往下拉」才蓋掉瀏覽器/PWA 原生的下拉行為（例如 Safari
      // 自己的下拉重整、橡皮筋效果），避免兩層下拉指示同時出現互相打架
      e.preventDefault()
      const next = Math.min(delta * 0.5, MAX_PULL)
      pullDistanceRef.current = next
      setPullDistance(next)
    }

    async function handleTouchEnd() {
      if (!pulling.current) return
      pulling.current = false
      startY.current = null
      if (pullDistanceRef.current >= PULL_THRESHOLD) {
        refreshingRef.current = true
        setRefreshing(true)
        try {
          await onRefresh()
        } finally {
          refreshingRef.current = false
          setRefreshing(false)
        }
      }
      pullDistanceRef.current = 0
      setPullDistance(0)
    }

    // passive: false 是關鍵——React 的合成 touch 事件預設 passive，preventDefault 不會
    // 生效，實機上會變成我們的下拉指示跟 Safari 原生下拉重整同時出現，只能用原生
    // addEventListener 手動關掉 passive 才擋得住
    el.addEventListener('touchstart', handleTouchStart, { passive: true })
    el.addEventListener('touchmove', handleTouchMove, { passive: false })
    el.addEventListener('touchend', handleTouchEnd)
    return () => {
      el.removeEventListener('touchstart', handleTouchStart)
      el.removeEventListener('touchmove', handleTouchMove)
      el.removeEventListener('touchend', handleTouchEnd)
    }
  }, [onRefresh])

  const indicatorHeight = refreshing ? 48 : pullDistance

  return (
    <div ref={containerRef}>
      <div
        data-testid="pull-to-refresh-indicator"
        data-refreshing={refreshing}
        className="flex items-center justify-center overflow-hidden transition-[height] duration-200"
        style={{ height: indicatorHeight }}
      >
        <span className="font-mono text-xs text-ink-soft/50">
          {refreshing ? '更新股票現值中…' : pullDistance >= PULL_THRESHOLD ? '放開更新' : '下拉更新股票現值'}
        </span>
      </div>
      {children}
    </div>
  )
}
