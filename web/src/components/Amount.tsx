const formatter = new Intl.NumberFormat('zh-TW', { maximumFractionDigits: 0 })

export function Amount({
  value,
  type,
  className = '',
}: {
  value: number
  type: '收入' | '支出'
  className?: string
}) {
  const isIncome = type === '收入'
  return (
    <span className={`font-mono tabular-nums ${isIncome ? 'text-mint' : 'text-coral'} ${className}`}>
      {isIncome ? '+' : '−'}
      {formatter.format(value)}
    </span>
  )
}
