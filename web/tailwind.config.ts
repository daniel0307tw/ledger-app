import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        void: '#0A0C10',
        'void-deep': '#050608',
        surface: '#14171E',
        'surface-high': '#1C2028',
        line: '#252A34',
        'line-soft': '#1B1F27',
        ink: '#F3F5F8',
        'ink-soft': '#8B90A0',
        mint: '#2EE6A6',
        'mint-dim': 'rgba(46, 230, 166, 0.14)',
        coral: '#FF6A5E',
        'coral-dim': 'rgba(255, 106, 94, 0.14)',
      },
      fontFamily: {
        display: ['var(--font-display)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['var(--font-body)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 0 rgba(255,255,255,0.045) inset, 0 16px 32px -20px rgba(0,0,0,0.7)',
        'glow-mint': '0 0 0 1px rgba(46,230,166,0.25), 0 8px 28px -6px rgba(46,230,166,0.45)',
        'glow-coral': '0 0 0 1px rgba(255,106,94,0.25), 0 8px 28px -6px rgba(255,106,94,0.35)',
      },
      backgroundImage: {
        'mesh-glow':
          'radial-gradient(circle at 12% -10%, rgba(46,230,166,0.16), transparent 42%), radial-gradient(circle at 100% 10%, rgba(255,106,94,0.10), transparent 38%)',
      },
    },
  },
  plugins: [],
}
export default config
