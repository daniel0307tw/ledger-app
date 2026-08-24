export function toISODate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export function startOfMonth(year: number, month: number): Date {
  return new Date(year, month, 1)
}

export function endOfMonth(year: number, month: number): Date {
  return new Date(year, month + 1, 0)
}

export function todayISO(): string {
  return toISODate(new Date())
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export function monthLabel(year: number, month: number): string {
  return MONTH_NAMES[month]
}

/** 產出月曆網格所需的日期矩陣：從週日開始的完整週，含前後月份的填補日 */
export function buildCalendarGrid(year: number, month: number): { date: Date; inMonth: boolean }[] {
  const first = startOfMonth(year, month)
  const last = endOfMonth(year, month)
  const startWeekday = first.getDay()
  const cells: { date: Date; inMonth: boolean }[] = []

  for (let i = startWeekday - 1; i >= 0; i--) {
    cells.push({ date: new Date(year, month, -i), inMonth: false })
  }
  for (let d = 1; d <= last.getDate(); d++) {
    cells.push({ date: new Date(year, month, d), inMonth: true })
  }
  while (cells.length % 7 !== 0) {
    const lastCell = cells[cells.length - 1].date
    cells.push({ date: new Date(lastCell.getFullYear(), lastCell.getMonth(), lastCell.getDate() + 1), inMonth: false })
  }
  return cells
}
