import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

export interface FactPayment {
  id: number
  institution: number
  institution_name: string
  kosgu: number
  kosgu_display: string
  year: number
  amount: string
  payment_date: string
  description: string
  document_number: string
  added_by_name: string
  added_at: string
}

export interface Reservation {
  id: number
  institution: number
  institution_name: string
  kosgu: number
  kosgu_display: string
  year: number
  contract_number: string
  contractor: string
  amount: string
  contract_date: string
  status: string
  status_display: string
  created_by_name: string
  created_at: string
  note: string
}

export function useFactPayments(year: number) {
  return useQuery<FactPayment[]>({
    queryKey: ['fact-payments', year],
    queryFn: async () => {
      const res = await api.get('/api/monitoring/fact-payments/', { params: { year } })
      return res.data
    },
  })
}

export function useReservations(year: number) {
  return useQuery<Reservation[]>({
    queryKey: ['reservations', year],
    queryFn: async () => {
      const res = await api.get('/api/monitoring/reservations/', { params: { year } })
      return res.data
    },
  })
}

export function useAddFactPayment(year: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post('/api/monitoring/fact-payments/', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['fact-payments', year] }),
  })
}

export function useAddReservation(year: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api.post('/api/monitoring/reservations/', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reservations', year] }),
  })
}
