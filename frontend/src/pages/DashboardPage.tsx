import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  BarChart2,
  Download,
} from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useAuth } from '@/contexts/AuthContext'
import { useDashboard, type DirectorDashboard, type AccountantDashboard, type HeadDashboard } from '@/hooks/useDashboard'
import { formatCurrency, formatDate, getStatusColor, getStatusLabel } from '@/lib/utils'

const KOSGU_COLORS = [
  '#5e6ad2', '#7c8ce0', '#3b4bc4', '#8b5cf6', '#06b6d4',
  '#10b981', '#f59e0b', '#ef4444',
]

export default function DashboardPage() {
  const { user } = useAuth()
  const { data, isLoading, error } = useDashboard()

  if (isLoading) {
    return (
      <Layout>
        <TopBar title="Дашборд" />
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <TopBar title="Дашборд" />
        <div className="p-6">
          <div className="rounded-xl border border-red-100 bg-red-50 p-4 text-red-700 text-sm">
            Ошибка загрузки данных. Попробуйте обновить страницу.
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <TopBar title={`Дашборд — ${data?.year ?? ''}`} />
      <div className="p-6">
        {user?.role === 'director' && data && <DirectorDashboard data={data as DirectorDashboard} />}
        {user?.role === 'accountant' && data && <AccountantDashboard data={data as AccountantDashboard} />}
        {(user?.role === 'head' || user?.role === 'admin') && data && (
          <HeadDashboard data={data as HeadDashboard} />
        )}
      </div>
    </Layout>
  )
}

// ─── Director ──────────────────────────────────────────────────────────────

function DirectorDashboard({ data }: { data: DirectorDashboard }) {
  const navigate = useNavigate()

  const limit = parseFloat(data.limit)
  const fact = parseFloat(data.fact_total)
  const reserved = parseFloat(data.reserved_total)
  const free = parseFloat(data.free)

  const isWarningLow = data.pct_used < 20 && limit > 0
  const isWarningHigh = data.pct_used >= 90

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-sm text-gray-500 mb-1">Учреждение</h2>
        <p className="text-base font-medium text-gray-800">{data.institution.full_name}</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="Годовой лимит"
          value={formatCurrency(limit)}
          icon={<BarChart2 size={16} className="text-indigo-500" />}
          color="indigo"
        />
        <StatCard
          label="Исполнено (факт)"
          value={formatCurrency(fact)}
          icon={<CheckCircle size={16} className="text-green-500" />}
          color="green"
        />
        <StatCard
          label="Зарезервировано"
          value={formatCurrency(reserved)}
          icon={<Clock size={16} className="text-amber-500" />}
          color="amber"
        />
        <StatCard
          label="Свободный остаток"
          value={formatCurrency(free)}
          icon={<TrendingUp size={16} className="text-blue-500" />}
          color="blue"
        />
      </div>

      {/* Progress bar */}
      <Card>
        <CardContent className="pt-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Исполнение бюджета {data.year}</span>
            <span className="text-sm font-semibold text-gray-900">{data.pct_used}%</span>
          </div>
          <Progress
            value={data.pct_used}
            className="h-2.5"
            indicatorClassName={
              isWarningHigh ? 'bg-red-500' : isWarningLow ? 'bg-amber-400' : 'bg-[#5e6ad2]'
            }
          />
          {(isWarningLow || isWarningHigh) && (
            <div
              className={`flex items-center gap-2 mt-3 text-sm rounded-lg px-3 py-2 ${
                isWarningHigh
                  ? 'bg-red-50 text-red-700 border border-red-100'
                  : 'bg-amber-50 text-amber-700 border border-amber-100'
              }`}
            >
              <AlertTriangle size={14} />
              {isWarningHigh
                ? 'Внимание: бюджет использован более чем на 90%'
                : 'Низкий процент исполнения бюджета'}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent requests */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Последние заявки</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate('/requests')}>
              Все заявки →
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-2">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>№</TableHead>
                <TableHead>Период</TableHead>
                <TableHead>Сумма</TableHead>
                <TableHead>Согласовано</TableHead>
                <TableHead>Статус</TableHead>
                <TableHead>Дата</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.recent_requests.map((r) => {
                const colors = getStatusColor(r.status)
                return (
                  <TableRow
                    key={r.id}
                    className="cursor-pointer"
                    onClick={() => navigate(`/requests/${r.id}`)}
                  >
                    <TableCell className="font-medium text-gray-900">#{r.id}</TableCell>
                    <TableCell>
                      {r.period_year}
                      {r.period_type === 'quarterly' ? ' (квартал)' : ''}
                    </TableCell>
                    <TableCell>{formatCurrency(r.total_amount)}</TableCell>
                    <TableCell>
                      {r.approved_amount ? formatCurrency(r.approved_amount) : '—'}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border}`}
                      >
                        {getStatusLabel(r.status)}
                      </span>
                    </TableCell>
                    <TableCell className="text-gray-400">{formatDate(r.created_at)}</TableCell>
                  </TableRow>
                )
              })}
              {data.recent_requests.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-400 py-8">
                    Заявок пока нет
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── Accountant ─────────────────────────────────────────────────────────────

function AccountantDashboard({ data }: { data: AccountantDashboard }) {
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="На проверке"
          value={String(data.pending_requests)}
          icon={<Clock size={16} className="text-amber-500" />}
          color="amber"
          isCount
        />
        <StatCard
          label="Черновиков"
          value={String(data.stats.draft)}
          icon={<FileText size={16} className="text-gray-400" />}
          color="gray"
          isCount
        />
        <StatCard
          label="Согласовано"
          value={String(data.stats.approved)}
          icon={<CheckCircle size={16} className="text-green-500" />}
          color="green"
          isCount
        />
        <StatCard
          label="Сумма согласована"
          value={formatCurrency(data.stats.total_approved_amount)}
          icon={<TrendingUp size={16} className="text-indigo-500" />}
          color="indigo"
        />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-3">
        <QuickActionCard
          icon={<BarChart2 size={20} className="text-indigo-500" />}
          label="Сводная ведомость"
          onClick={() => navigate('/reports/consolidated')}
        />
        <QuickActionCard
          icon={<Download size={20} className="text-green-500" />}
          label="Экспорт Excel"
          onClick={() => {
            window.open('/api/reports/export/excel/?year=2026', '_blank')
          }}
        />
        <QuickActionCard
          icon={<FileText size={20} className="text-blue-500" />}
          label="Все заявки"
          onClick={() => navigate('/requests')}
        />
      </div>

      {/* Incoming requests */}
      <Card>
        <CardHeader>
          <CardTitle>Входящие заявки на проверку</CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Учреждение</TableHead>
                <TableHead>Период</TableHead>
                <TableHead>Сумма</TableHead>
                <TableHead>Отправлено</TableHead>
                <TableHead>Дедлайн</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.incoming_requests.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium text-gray-900">{r.institution_name}</TableCell>
                  <TableCell>
                    {r.period_year} ({r.period_type})
                  </TableCell>
                  <TableCell>{formatCurrency(r.total_amount)}</TableCell>
                  <TableCell className="text-gray-400">
                    {r.submitted_at ? formatDate(r.submitted_at) : '—'}
                  </TableCell>
                  <TableCell>
                    {r.deadline ? (
                      <span className="text-amber-600 font-medium">{formatDate(r.deadline)}</span>
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/requests/${r.id}`)}
                    >
                      Проверить
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {data.incoming_requests.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-400 py-8">
                    Входящих заявок нет
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── Head / Admin ───────────────────────────────────────────────────────────

function HeadDashboard({ data }: { data: HeadDashboard }) {
  const navigate = useNavigate()

  const chartData = data.kosgu_breakdown.map((item) => ({
    name: `${item.code}`,
    value: parseFloat(item.total),
    fullName: item.name,
  }))

  return (
    <div className="space-y-6">
      {/* KPI */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Суммарный лимит"
          value={formatCurrency(data.total_limit)}
          icon={<BarChart2 size={16} className="text-indigo-500" />}
          color="indigo"
        />
        <StatCard
          label="Исполнено"
          value={formatCurrency(data.total_fact)}
          icon={<CheckCircle size={16} className="text-green-500" />}
          color="green"
        />
        <StatCard
          label="Общее освоение"
          value={`${data.pct_overall}%`}
          icon={<TrendingUp size={16} className="text-blue-500" />}
          color="blue"
          isCount
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* KOSGU Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Расходы по КОСГУ</CardTitle>
          </CardHeader>
          <CardContent>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {chartData.map((_, index) => (
                      <Cell key={index} fill={KOSGU_COLORS[index % KOSGU_COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    formatter={(value: number, _name: string, props) => [
                      formatCurrency(value),
                      props.payload.fullName,
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
                Нет данных за {data.year} год
              </div>
            )}
          </CardContent>
        </Card>

        {/* Institutions list */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Учреждения</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => navigate('/institutions')}>
                Все →
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-2 space-y-3">
            {data.institution_stats.slice(0, 6).map((inst) => (
              <div key={inst.id} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700 truncate mr-2" title={inst.name}>
                    {inst.name}
                  </span>
                  <span className="text-gray-500 shrink-0 text-xs">{inst.pct}%</span>
                </div>
                <Progress
                  value={inst.pct}
                  className="h-1.5"
                  indicatorClassName={
                    inst.pct >= 90
                      ? 'bg-red-500'
                      : inst.pct >= 60
                      ? 'bg-green-500'
                      : 'bg-[#5e6ad2]'
                  }
                />
              </div>
            ))}
            {data.institution_stats.length === 0 && (
              <div className="text-center text-gray-400 text-sm py-4">Нет данных</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  icon,
  color,
  isCount = false,
}: {
  label: string
  value: string
  icon: React.ReactNode
  color: string
  isCount?: boolean
}) {
  const bgMap: Record<string, string> = {
    indigo: 'bg-indigo-50',
    green: 'bg-green-50',
    amber: 'bg-amber-50',
    blue: 'bg-blue-50',
    gray: 'bg-gray-50',
  }

  return (
    <Card>
      <CardContent className="pt-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`font-semibold text-gray-900 ${isCount ? 'text-2xl' : 'text-lg'}`}>
              {value}
            </p>
          </div>
          <div className={`rounded-lg p-2 ${bgMap[color] ?? 'bg-gray-50'}`}>{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}

function QuickActionCard({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode
  label: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-3 p-4 rounded-xl border border-gray-200 bg-white hover:border-[#5e6ad2] hover:shadow-sm transition-all text-center"
    >
      <div className="rounded-lg p-2.5 bg-gray-50">{icon}</div>
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </button>
  )
}
