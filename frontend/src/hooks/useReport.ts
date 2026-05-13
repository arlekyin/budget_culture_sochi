import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export interface ReportRow {
  institution_id: number
  institution_name: string
  limit: string
  requested: string
  approved: string
  fact: string
  balance: string
  pct: number
}

export interface ConsolidatedReport {
  year: number
  rows: ReportRow[]
  totals: {
    limit: string
    requested: string
    approved: string
    fact: string
    balance: string
  }
}

export function useReport(year: number) {
  return useQuery<ConsolidatedReport>({
    queryKey: ['report', year],
    queryFn: async () => {
      const res = await api.get('/api/reports/consolidated/', { params: { year } })
      return res.data
    },
    staleTime: 60_000,
  })
}

export function useClassifiers() {
  const kosgu = useQuery({
    queryKey: ['kosgu'],
    queryFn: async () => {
      const res = await api.get('/api/classifiers/kosgu/')
      return res.data as Array<{ id: number; code: string; name: string }>
    },
    staleTime: Infinity,
  })

  const kvr = useQuery({
    queryKey: ['kvr'],
    queryFn: async () => {
      const res = await api.get('/api/classifiers/kvr/')
      return res.data as Array<{ id: number; code: string; name: string }>
    },
    staleTime: Infinity,
  })

  return { kosgu, kvr }
}
