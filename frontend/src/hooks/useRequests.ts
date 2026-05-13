import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export interface RequestLine {
  id: number
  kosgu: number
  kosgu_display: string
  kvr: number | null
  kvr_display: string | null
  description: string
  unit_price: string
  quantity: string
  amount: string
  note: string
  attachment: string | null
  attachment_url: string | null
}

export interface BudgetRequest {
  id: number
  institution: number
  institution_name: string
  period_year: number
  period_type: string
  period_type_display: string
  period_quarter: number | null
  funding_type: string
  funding_type_display: string
  status: string
  status_display: string
  total_amount: string
  approved_amount: string | null
  created_at: string
  submitted_at: string | null
  reviewed_at: string | null
  deadline: string | null
  comment: string
  lines: RequestLine[]
  created_by: number | null
  created_by_name: string
  reviewed_by: number | null
  reviewed_by_name: string
}

export interface RequestFilters {
  status?: string
  year?: number | string
}

export function useRequests(filters?: RequestFilters) {
  return useQuery<BudgetRequest[]>({
    queryKey: ['requests', filters],
    queryFn: async () => {
      const res = await api.get('/api/requests/', { params: filters })
      return res.data
    },
    staleTime: 15_000,
  })
}
