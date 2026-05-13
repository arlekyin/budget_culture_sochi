import { useNavigate } from 'react-router-dom'
import { MapPin, User, ChevronRight } from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useInstitutions } from '@/hooks/useInstitutions'

const TYPE_VARIANTS: Record<string, 'blue' | 'indigo' | 'success' | 'warning' | 'default' | 'orange'> = {
  library: 'blue',
  museum: 'indigo',
  theater: 'orange',
  culture_house: 'success',
  art_school: 'warning',
  other: 'default',
}

export default function InstitutionsPage() {
  const { data, isLoading } = useInstitutions()
  const navigate = useNavigate()

  return (
    <Layout>
      <TopBar title="Учреждения культуры" />
      <div className="p-6">
        {isLoading ? (
          <div className="grid grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-40 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {(data ?? []).map((inst) => (
              <Card
                key={inst.id}
                className="cursor-pointer hover:border-[#5e6ad2] hover:shadow-md transition-all"
                onClick={() => navigate(`/institutions/${inst.id}`)}
              >
                <CardContent className="pt-5">
                  <div className="flex items-start justify-between mb-3">
                    <Badge variant={TYPE_VARIANTS[inst.institution_type] ?? 'default'}>
                      {inst.institution_type_display}
                    </Badge>
                    <ChevronRight size={14} className="text-gray-300 shrink-0" />
                  </div>

                  <h3 className="font-semibold text-gray-900 text-sm leading-snug mb-3">
                    {inst.short_name}
                  </h3>

                  <div className="space-y-1.5 text-xs text-gray-500">
                    {inst.head_name && (
                      <div className="flex items-center gap-1.5">
                        <User size={11} className="shrink-0 text-gray-400" />
                        <span className="truncate">{inst.head_name}</span>
                      </div>
                    )}
                    {inst.address && (
                      <div className="flex items-start gap-1.5">
                        <MapPin size={11} className="shrink-0 text-gray-400 mt-0.5" />
                        <span className="line-clamp-2">{inst.address}</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <span className="text-xs text-[#5e6ad2] font-medium">Подробнее →</span>
                  </div>
                </CardContent>
              </Card>
            ))}
            {(data ?? []).length === 0 && (
              <div className="col-span-3 text-center text-gray-400 py-12">
                Учреждений не найдено
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
