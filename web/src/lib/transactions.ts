import type { Transaction } from '@/lib/types'

// 比照後端 app/repositories/transaction_repository.py 的 _effective_amount()：
// 已結清（advancePaymentStatus=settled）的代墊款交易，計入支出/預算/報表的有效金額為
// amount − advancePaymentAmount；尚未結清或非代墊款交易仍以 amount 全額計入。
export function effectiveAmount(t: Pick<Transaction, 'amount' | 'advancePaymentAmount' | 'advancePaymentStatus'>): number {
  if (t.advancePaymentAmount != null && t.advancePaymentStatus === 'settled') {
    return t.amount - t.advancePaymentAmount
  }
  return t.amount
}
