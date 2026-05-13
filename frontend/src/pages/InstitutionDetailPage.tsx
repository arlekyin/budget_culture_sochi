import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  MapPin,
  User,
  Building2,
  Phone,
  Hash,
  TrendingUp,
  FileText,
} from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatCurrency, formatDate, getStatusColor, getStatusLabel } from '@/lib/utils'
import api from '@/lib/api'

interface Limit {
  year: number
  total_limit: string
}

interface RecentRequest {
  id: number
  period_year: number
  period_type: string
  status: string
  status_display: string
  total_amount: string
  approved_amount: string | null
  created_at: string
}

interface YearStats {
  year: number
  limit: string
  fact: string
  balance: string
  pct: number
}

interface InstitutionDetail {
  id: number
  short_name: string
  name: string
  institution_type: string
  institution_type_display: string
  inn: string
  address: string
  head_name: string
  limits: Limit[]
  recent_requests: RecentRequest[]
  current_year_stats: YearStats
}

const TYPE_VARIANTS: Record<string, 'blue' | 'indigo' | 'success' | 'warning' | 'default' | 'orange'> = {
  library: 'blue',
  museum: 'indigo',
  theater: 'orange',
  culture_house: 'success',
  art_school: 'warning',
  other: 'default',
}

export default function InstitutionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: inst, isLoading, error } = useQuery<InstitutionDetail>({
    queryKey: ['institution', id],
    queryFn: async () => {
      const res = await api.get(`/api/institutions/${id}/`)
      return res.data
    },
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <Layout>
        <TopBar title="Учреждение" />
        <div className="p-6 space-y-4">
          <Skeleton className="h-8 w-64" />
          <div className="grid grid-cols-3 gap-4">
            <Skeleton className="h-28 col-span-1 rounded-xl" />
            <Skeleton className="h-28 col-span-2 rounded-xl" />
          </div>
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </Layout>
    )
  }

  if (error || !inst) {
    return (
      <Layout>
        <TopBar title="Учреждение" />
        <div className="p-6">
          <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-red-700 text-sm">
            Не удалось загрузить данные учреждения.
          </div>
        </div>
      </Layout>
    )
  }

  const stats = inst.current_year_stats
  const pct = stats?.pct ?? 0

  return (
    <Layout>
      <TopBar title={inst.short_name} />
      <div className="p-6 space-y-5 max-w-5xl">
        {/* Back */}
        <button
          onClick={() => navigate('/institutions')}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft size={14} />
          К списку учреждений
        </button>

        {/* Header */}
        <div className="flex items-start gap-3">
          <div
            className="flex items-center justify-center rounded-xl shrink-0"
            style={{ width: 44, height: 44, background: '#f0f1fd' }}
          >
            <Building2 size={22} className="text-[#5e6ad2]" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-xl font-semibold text-gray-900">{inst.short_name}</h1>
              <Badge variant={TYPE_VARIANTS[inst.institution_type] ?? 'default'}>
                {inst.institution_type_display}
              </Badge>
            </div>
            <p className="text-sm text-gray-500">{inst.name}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          {/* Info card */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-gray-700">Реквизиты</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {inst.head_name && (
                <div className="flex items-start gap-2">
                  <User size={14} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-xs text-gray-400 mb-0.5">Руководитель</div>
                    <div className="text-gray-800">{inst.head_name}</div>
                  </div>
                </div>
              )}
              {inst.inn && (
                <div className="flex items-start gap-2">
                  <Hash size={14} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-xs text-gray-400 mb-0.5">ИНН</div>
                    <div className="text-gray-800 font-mono">{inst.inn}</div>
                  </div>
                </div>
              )}
              {inst.address && (
                <div className="flex items-start gap-2">
                  <MapPin size={14} className="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-xs text-gray-400 mb-0.5">Адрес</div>
                    <div className="text-gray-800">{inst.address}</div>
                  </div>
                </div>
              )}

              {/* Лимиты по годам */}
              {inst.limits?.length > 0 && (
                <div className="pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-400 mb-2">Лимиты финансирования</div>
                  <div className="space-y-1.5">
                    {[...inst.limits]
                      .sort((a, b) => b.year - a.year)
                      .map((lim) => (
                        <div key={lim.year} className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">{lim.year} год</span>
                          <span className="text-xs font-semibold text-gray-800">
                            {formatCurrency(lim.total_limit)}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Right column */}
          <div className="lg:col-span-2 space-y-5">
            {/* Budget execution card */}
            {stats && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <TrendingUp size={14} className="text-[#5e6ad2]" />
                    Исполнение бюджета {stats.year} года
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Лимит</div>
                      <div className="text-sm font-semibold text-gray-800">
                        {formatCurrency(stats.limit)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Исполнено</div>
                      <div className="text-sm font-semibold text-green-700">
                        {formatCurrency(stats.fact)}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400 mb-1">Остаток</div>
                      <div className={`text-sm font-semibold ${parseFloat(stats.balance) < 0 ? 'text-red-600' : 'text-gray-800'}`}>
                        {formatCurrency(stats.balance)}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Освоение средств</span>
                      <span className="font-medium">{pct}%</span>
                    </div>
                    <Progress
                      value={pct}
                      className="h-2"
                      indicatorClassName={
                        pct > 90 ? 'bg-red-500' :
                        pct > 70 ? 'bg-amber-500' :
                        pct < 10 ? 'bg-gray-300' :
                        'bg-[#5e6ad2]'
                      }
                    />
                  </div>
                  {pct < 15 && (
                    <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                      ⚠ Низкий процент освоения — возможен риск неосвоения средств.
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Recent requests */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <FileText size={14} className="text-[#5e6ad2]" />
                  Последние заявки
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {inst.recent_requests?.length === 0 ? (
                  <div className="text-center text-gray-400 text-sm py-8">
                    Заявок нет
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>№</TableHead>
                        <TableHead>Год</TableHead>
                        <TableHead>Заявлено</TableHead>
                        <TableHead>Согласовано</TableHead>
                        <TableHead>Статус</TableHead>
                        <TableHead>Дата</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {inst.recent_requests.map((req) => {
                        const sc = getStatusColor(req.status)
                        return (
                          <TableRow
                            key={req.id}
                            className="cursor-pointer hover:bg-gray-50"
                            onClick={() => navigate(`/requests/${req.id}`)}
                          >
                            <TableCell className="text-gray-400 text-xs">#{req.id}</TableCell>
                            <TableCell className="text-sm">{req.period_year}</TableCell>
                            <TableCell className="text-sm font-mono">
                              {formatCurrency(req.total_amount)}
                            </TableCell>
                            <TableCell className="text-sm font-mono text-green-700">
                              {req.approved_amount ? formatCurrency(req.approved_amount) : '—'}
                            </TableCell>
                            <TableCell>
                              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium border ${sc.bg} ${sc.text} ${sc.border}`}>
                                {getStatusLabel(req.status)}
                              </span>
                            </TableCell>
                            <TableCell className="text-xs text-gray-400">
                              {formatDate(req.created_at)}
                            </TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  )
}
