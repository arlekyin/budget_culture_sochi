import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

export interface Institution {
  id: number
  name: string
  short_name: string
  institution_type: string
  institution_type_display: string
  address: string
  head_name: string
  is_active: boolean
}

export function useInstitutions() {
  return useQuery<Institution[]>({
    queryKey: ['institutions'],
    queryFn: async () => {
      const res = await api.get('/api/institutions/')
      return res.data
    },
    staleTime: 60_000,
  })
}

export function useInstitution(id: number | string) {
  return useQuery({
    queryKey: ['institution', id],
    queryFn: async () => {
      const res = await api.get(`/api/institutions/${id}/`)
      return res.data
    },
    enabled: !!id,
  })
}
