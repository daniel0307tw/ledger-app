'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const TABS = [
  { href: '/calendar', label: '行事曆', icon: CalendarIcon },
  { href: '/reports', label: '報表', icon: ChartIcon },
  { href: '/accounts', label: '帳戶', icon: WalletIcon },
  { href: '/assets', label: '資產', icon: TrendIcon },
  { href: '/settings', label: '設定', icon: SettingsIcon },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav
      data-testid="bottom-nav"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-void/90 backdrop-blur-xl pb-[env(safe-area-inset-bottom)]"
    >
      <div className="mx-auto flex max-w-md items-stretch">
        {TABS.map((tab) => {
          const active = pathname.startsWith(tab.href)
          const Icon = tab.icon
          return (
            <Link
              key={tab.href}
              href={tab.href}
              data-testid={`nav-${tab.href.slice(1)}`}
              className="flex flex-1 flex-col items-center gap-1 py-2.5"
            >
              <Icon className={active ? 'text-mint drop-shadow-[0_0_6px_rgba(46,230,166,0.5)]' : 'text-ink-soft/50'} />
              <span
                className={`text-[11px] tracking-wide ${active ? 'font-medium text-mint' : 'text-ink-soft/50'}`}
              >
                {tab.label}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

function CalendarIcon({ className }: { className?: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className={className}>
      <rect x="3.5" y="5" width="17" height="16" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M3.5 9.5h17" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8 3v4M16 3v4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="8" cy="13.2" r="1.1" fill="currentColor" />
      <circle cx="12" cy="13.2" r="1.1" fill="currentColor" />
    </svg>
  )
}

function ChartIcon({ className }: { className?: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M12 3.5A8.5 8.5 0 0 1 20.5 12H12V3.5Z" fill="currentColor" />
    </svg>
  )
}

function TrendIcon({ className }: { className?: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M3.5 17.5l6-6.5 4 4 6.5-8" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15.5 6.5h4.5v4.5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className={className}>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M12 3.5v2.2M12 18.3v2.2M20.5 12h-2.2M5.7 12H3.5M17.8 6.2l-1.6 1.6M7.8 16.2l-1.6 1.6M17.8 17.8l-1.6-1.6M7.8 7.8L6.2 6.2"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  )
}

function WalletIcon({ className }: { className?: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M4 7.5A2.5 2.5 0 0 1 6.5 5h11A2.5 2.5 0 0 1 20 7.5v9a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5v-9Z"
        stroke="currentColor"
        strokeWidth="1.7"
      />
      <path d="M14.5 12.2h3.2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M4 9.5h16" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  )
}
