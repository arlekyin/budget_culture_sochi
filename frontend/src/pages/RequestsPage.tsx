import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ChevronRight, Filter } from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useAuth } from '@/contexts/AuthContext'
import { useRequests } from '@/hooks/useRequests'
import { formatCurrency, formatDate, getStatusColor, getStatusLabel } from '@/lib/utils'

const STATUS_OPTIONS = [
  { value: '', label: 'Все статусы' },
  { value: 'draft', label: 'Черновик' },
  { value: 'submitted', label: 'На проверке' },
  { value: 'returned', label: 'Возвращена' },
  { value: 'approved', label: 'Согласована' },
  { value: 'rejected', label: 'Отклонена' },
  { value: 'included', label: 'В бюджете' },
]

const YEAR_OPTIONS = [2024, 2025, 2026, 2027].map((y) => ({
  value: String(y),
  label: String(y),
}))

export default function RequestsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [statusFilter, setStatusFilter] = useState('')
  const [yearFilter, setYearFilter] = useState('')
  const [appliedFilters, setAppliedFilters] = useState<{ status?: string; year?: string }>({})

  const { data, isLoading } = useRequests({
    status: appliedFilters.status || undefined,
    year: appliedFilters.year || undefined,
  })

  const applyFilters = () => {
    setAppliedFilters({
      status: statusFilter && statusFilter !== '__all__' ? statusFilter : undefined,
      year: yearFilter && yearFilter !== '__all__' ? yearFilter : undefined,
    })
  }

  const resetFilters = () => {
    setStatusFilter('')
    setYearFilter('')
    setAppliedFilters({})
  }

  return (
    <Layout>
      <TopBar title="Бюджетные заявки">
        {user?.role === 'director' && (
          <Button size="sm" onClick={() => navigate('/requests/new')}>
            <Plus size={14} />
            Новая заявка
          </Button>
        )}
      </TopBar>

      <div className="p-6 space-y-4">
        {/* Filters */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <Filter size={14} className="text-gray-400 shrink-0" />
              <div className="flex items-center gap-2 flex-1 flex-wrap">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-44">
                    <SelectValue placeholder="Статус" />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value || '__all__'}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={yearFilter} onValueChange={setYearFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Год" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__all__">Все годы</SelectItem>
                    {YEAR_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Button size="sm" onClick={applyFilters}>
                  Применить
                </Button>
                <Button size="sm" variant="ghost" onClick={resetFilters}>
                  Сбросить
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-5 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full rounded-lg" />
                ))}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>№</TableHead>
                    <TableHead>Учреждение</TableHead>
                    <TableHead>Период</TableHead>
                    <TableHead>Тип средств</TableHead>
                    <TableHead>Заявлено</TableHead>
                    <TableHead>Согласовано</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Дата</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(data ?? []).map((req) => {
                    const colors = getStatusColor(req.status)
                    return (
                      <TableRow
                        key={req.id}
                        className="cursor-pointer"
                        onClick={() => navigate(`/requests/${req.id}`)}
                      >
                        <TableCell className="font-medium text-gray-900">
                          #{req.id}
                        </TableCell>
                        <TableCell className="max-w-[180px]">
                          <span className="truncate block" title={req.institution_name}>
                            {req.institution_name}
                          </span>
                        </TableCell>
                        <TableCell>
                          {req.period_year}
                          {req.period_type === 'quarterly' && req.period_quarter
                            ? ` / ${req.period_quarter} кв.`
                            : ''}
                        </TableCell>
                        <TableCell className="text-gray-500 text-xs">
                          {req.funding_type_display}
                        </TableCell>
                        <TableCell>{formatCurrency(req.total_amount)}</TableCell>
                        <TableCell>
                          {req.approved_amount
                            ? formatCurrency(req.approved_amount)
                            : '—'}
                        </TableCell>
                        <TableCell>
                          <span
                            className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border}`}
                          >
                            {getStatusLabel(req.status)}
                          </span>
                        </TableCell>
                        <TableCell className="text-gray-400 text-xs">
                          {formatDate(req.created_at)}
                        </TableCell>
                        <TableCell>
                          <ChevronRight size={14} className="text-gray-300" />
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  {(data ?? []).length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={9}
                        className="text-center text-gray-400 py-12"
                      >
                        Заявок не найдено
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
