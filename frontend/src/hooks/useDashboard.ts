import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export interface DirectorDashboard {
  role: 'director'
  institution: { id: number; name: string; full_name: string }
  limit: string
  fact_total: string
  reserved_total: string
  approved_total: string
  free: string
  pct_used: number
  year: number
  recent_requests: Array<{
    id: number
    period_year: number
    period_type: string
    status: string
    status_display: string
    total_amount: string
    approved_amount: string | null
    created_at: string
  }>
}

export interface AccountantDashboard {
  role: 'accountant'
  year: number
  pending_requests: number
  stats: {
    draft: number
    submitted: number
    approved: number
    total_approved_amount: string
  }
  incoming_requests: Array<{
    id: number
    institution_name: string
    period_year: number
    period_type: string
    total_amount: string
    submitted_at: string | null
    deadline: string | null
  }>
}

export interface HeadDashboard {
  role: 'head' | 'admin'
  year: number
  total_limit: string
  total_fact: string
  pct_overall: number
  institution_stats: Array<{
    id: number
    name: string
    limit: string
    fact: string
    pct: number
  }>
  kosgu_breakdown: Array<{
    code: string
    name: string
    total: string
  }>
}

export type DashboardData = DirectorDashboard | AccountantDashboard | HeadDashboard

export function useDashboard(year?: number) {
  return useQuery<DashboardData>({
    queryKey: ['dashboard', year],
    queryFn: async () => {
      const params = year ? { year } : {}
      const res = await api.get('/api/dashboard/', { params })
      return res.data
    },
    staleTime: 30_000,
  })
}
