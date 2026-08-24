'use client'

import { useEffect, useState } from 'react'

// React Strict Mode 在 dev 模式會把這個 effect 呼叫兩次；MSW 的 worker.start() 不能同時被
// 呼叫兩次（第二次會噴 "cannot configure an already enabled network"），若把這個錯誤吞掉直接
// setReady(true)，就會在真正的初始化完成前讓子元件掛載、提早發出還沒被攔截的 fetch。
// 用 module-level 的 singleton promise，確保無論 effect 被呼叫幾次，實際初始化只執行一次，
// 兩次呼叫都等同一個結果。
let mockReadyPromise: Promise<void> | null = null

function ensureMockReady(): Promise<void> {
  if (!mockReadyPromise) {
    mockReadyPromise = import('@/mocks/browser').then(({ initMocks }) => initMocks().then(waitForServiceWorkerControl))
  }
  return mockReadyPromise
}

// 等到瀏覽器實際回報「這個 client 已被 service worker 接管」再放行子元件，
// 否則 worker.start() resolve 後的第一批 fetch 仍可能在接管完成前送出，
// 直接打到真實網路（bypass），對還沒啟動的後端得到非 JSON 的錯誤頁。
function waitForServiceWorkerControl(): Promise<void> {
  if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) {
    return Promise.resolve()
  }
  if (navigator.serviceWorker.controller) {
    return Promise.resolve()
  }
  return new Promise((resolve) => {
    const onChange = () => {
      navigator.serviceWorker.removeEventListener('controllerchange', onChange)
      resolve()
    }
    navigator.serviceWorker.addEventListener('controllerchange', onChange)
    // 保底：萬一瀏覽器已經是 controller 但事件在監聽前就已觸發過
    setTimeout(() => {
      navigator.serviceWorker.removeEventListener('controllerchange', onChange)
      resolve()
    }, 2000)
  })
}

export function MSWProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_MOCK_API !== 'true') {
      setReady(true)
      return
    }

    let cancelled = false
    ensureMockReady()
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setReady(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (!ready) return null
  return <>{children}</>
}
