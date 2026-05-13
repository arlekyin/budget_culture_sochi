import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Объединяет CSS-классы с поддержкой Tailwind.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/**
 * Форматирует число как российские рубли: 1 234 567,89 ₽
 */
export function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === '') return '—'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return '—'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

/**
 * Форматирует дату в формат DD.MM.YYYY
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '—'
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

/**
 * Возвращает Tailwind-классы для цвета статуса заявки.
 */
export function getStatusColor(status: string): { bg: string; text: string; border: string } {
  switch (status) {
    case 'draft':
      return { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-200' }
    case 'submitted':
      return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' }
    case 'returned':
      return { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' }
    case 'approved':
      return { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' }
    case 'rejected':
      return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' }
    case 'included':
      return { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' }
    default:
      return { bg: 'bg-gray-100', text: 'text-gray-500', border: 'border-gray-200' }
  }
}

/**
 * Возвращает русское название статуса заявки.
 */
export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: 'Черновик',
    submitted: 'На проверке',
    returned: 'Возвращена',
    approved: 'Согласована',
    rejected: 'Отклонена',
    included: 'В бюджете',
  }
  return labels[status] ?? status
}
