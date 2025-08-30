import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, formatPercent, capitalizeWords } from '../formatters'

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('formats positive numbers correctly', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56')
      expect(formatCurrency(0)).toBe('$0.00')
      expect(formatCurrency(1000000)).toBe('$1,000,000.00')
    })

    it('handles null and undefined values', () => {
      expect(formatCurrency(null)).toBe('$0.00')
      expect(formatCurrency(undefined)).toBe('$0.00')
    })

    it('formats negative numbers correctly', () => {
      expect(formatCurrency(-1234.56)).toBe('-$1,234.56')
    })
  })

  describe('formatDate', () => {
    it('formats valid date strings', () => {
      expect(formatDate('2024-01-15')).toBe('Jan 15, 2024')
      expect(formatDate('2024-12-31')).toBe('Dec 31, 2024')
    })

    it('handles null and undefined values', () => {
      expect(formatDate(null)).toBe('Not set')
      expect(formatDate(undefined)).toBe('Not set')
      expect(formatDate('')).toBe('Not set')
    })

    it('handles invalid date strings', () => {
      expect(formatDate('invalid-date')).toBe('Invalid Date')
    })
  })

  describe('formatPercent', () => {
    it('formats numbers correctly', () => {
      expect(formatPercent(50)).toBe('50%')
      expect(formatPercent(0)).toBe('0%')
      expect(formatPercent(100)).toBe('100%')
    })

    it('handles null and undefined values', () => {
      expect(formatPercent(null)).toBe('0%')
      expect(formatPercent(undefined)).toBe('0%')
    })

    it('handles decimal values', () => {
      expect(formatPercent(75.5)).toBe('75.5%')
    })
  })

  describe('capitalizeWords', () => {
    it('capitalizes words correctly', () => {
      expect(capitalizeWords('hello world')).toBe('Hello World')
      expect(capitalizeWords('test_string')).toBe('Test String')
      expect(capitalizeWords('not_started')).toBe('Not Started')
    })

    it('handles empty and null values', () => {
      expect(capitalizeWords('')).toBe('')
      expect(capitalizeWords(null)).toBe('')
      expect(capitalizeWords(undefined)).toBe('')
    })

    it('handles single words', () => {
      expect(capitalizeWords('test')).toBe('Test')
      expect(capitalizeWords('UPPERCASE')).toBe('UPPERCASE')
    })
  })
})
