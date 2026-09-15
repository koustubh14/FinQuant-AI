import { describe, expect, it } from 'vitest'
import { num, pct, safeUrl } from './utils'
describe('Financial display', () => {
  it('distinguishes unavailable metrics from zero', () => {
    expect(pct(null)).toBe('\u2014'); expect(pct(0)).toBe('0.00%'); expect(num(Infinity)).toBe('\u2014')
  })
  it('uses fractional units', () => { expect(pct(.125)).toBe('12.50%') })
  it('rejects executable news links', () => { expect(safeUrl('javascript:alert(1)')).toBeUndefined() })
})
