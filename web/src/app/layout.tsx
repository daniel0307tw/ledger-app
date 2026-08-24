import type { Metadata, Viewport } from 'next'
import { Bricolage_Grotesque, Hanken_Grotesk, Fragment_Mono } from 'next/font/google'
import './globals.css'
import { MSWProvider } from '@/components/MSWProvider'

const display = Bricolage_Grotesque({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['500', '600', '700', '800'],
  display: 'swap',
})

const body = Hanken_Grotesk({
  subsets: ['latin'],
  variable: '--font-body',
  weight: ['400', '500', '600'],
  display: 'swap',
})

const mono = Fragment_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400'],
  style: ['normal', 'italic'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: '記帳',
  description: '個人記帳系統 — 快速記帳、行事曆檢視、股票現金部位同步',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: '記帳',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  viewportFit: 'cover',
  interactiveWidget: 'resizes-content',
  themeColor: '#0A0C10',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-TW" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body>
        <MSWProvider>{children}</MSWProvider>
      </body>
    </html>
  )
}
