import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import type { BudgetRequest } from './useRequests'

export function useRequest(id: number | string) {
  return useQuery<BudgetRequest>({
    queryKey: ['request', id],
    queryFn: async () => {
      const res = await api.get(`/api/requests/${id}/`)
      return res.data
    },
    enabled: !!id,
  })
}

export function useSubmitRequest(id: number | string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const res = await api.post(`/api/requests/${id}/submit/`)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['request', id] })
      qc.invalidateQueries({ queryKey: ['requests'] })
    },
  })
}

export function useReviewRequest(id: number | string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: {
      action: 'approve' | 'return' | 'reject'
      approved_amount?: string
      comment?: string
    }) => {
      const res = await api.post(`/api/requests/${id}/review/`, data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['request', id] })
      qc.invalidateQueries({ queryKey: ['requests'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useAddLine(id: number | string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const res = await api.post(`/api/requests/${id}/lines/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['request', id] })
    },
  })
}

export function useDeleteLine(requestId: number | string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (lineId: number) => {
      await api.delete(`/api/requests/${requestId}/lines/${lineId}/`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['request', requestId] })
    },
  })
}

export interface LineLog {
  id: number
  line: number
  line_description: string
  old_amount: string
  new_amount: string
  comment: string
  changed_by_name: string
  changed_at: string
}

export function useLineLogs(requestId: number | string) {
  return useQuery<LineLog[]>({
    queryKey: ['line-logs', requestId],
    queryFn: async () => {
      const res = await api.get(`/api/requests/${requestId}/logs/`)
      return res.data
    },
    enabled: !!requestId,
  })
}

export function useCreateRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: {
      period_year: number
      period_type: string
      period_quarter?: number | null
      funding_type: string
      deadline?: string
    }) => {
      const res = await api.post('/api/requests/create/', data)
      return res.data as BudgetRequest
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['requests'] })
    },
  })
}
