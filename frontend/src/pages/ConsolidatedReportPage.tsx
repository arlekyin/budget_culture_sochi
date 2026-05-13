import { useState } from 'react'
import { Download } from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
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
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
  TableCaption,
} from '@/components/ui/table'
import { useReport } from '@/hooks/useReport'
import { formatCurrency } from '@/lib/utils'

export default function ConsolidatedReportPage() {
  const [year, setYear] = useState(2026)
  const { data, isLoading } = useReport(year)

  const handleExcel = () => {
    window.open(`/api/reports/export/excel/?year=${year}`, '_blank')
  }

  return (
    <Layout>
      <TopBar title="Сводная ведомость">
        <div className="flex items-center gap-2">
          <Select value={String(year)} onValueChange={(v) => setYear(parseInt(v))}>
            <SelectTrigger className="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {[2024, 2025, 2026, 2027].map((y) => (
                <SelectItem key={y} value={String(y)}>
                  {y} год
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={handleExcel}>
            <Download size={14} />
            Выгрузить Excel
          </Button>
        </div>
      </TopBar>

      <div className="p-6">
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-xl" />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableCaption>
                  МКУ «ЦБ УК г. Сочи» — Управление культуры Администрации г. Сочи
                </TableCaption>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-8">№</TableHead>
                    <TableHead>Учреждение</TableHead>
                    <TableHead className="text-right">Лимит</TableHead>
                    <TableHead className="text-right">Заявлено</TableHead>
                    <TableHead className="text-right">Согласовано</TableHead>
                    <TableHead className="text-right">Исполнено</TableHead>
                    <TableHead className="text-right">Остаток</TableHead>
                    <TableHead className="w-36">Освоение</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(data?.rows ?? []).map((row, idx) => (
                    <TableRow key={row.institution_id}>
                      <TableCell className="text-gray-400">{idx + 1}</TableCell>
                      <TableCell className="font-medium text-gray-900">
                        {row.institution_name}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatCurrency(row.limit)}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatCurrency(row.requested)}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatCurrency(row.approved)}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatCurrency(row.fact)}
                      </TableCell>
                      <TableCell
                        className={`text-right tabular-nums font-medium ${
                          parseFloat(row.balance) < 0 ? 'text-red-600' : 'text-gray-700'
                        }`}
                      >
                        {formatCurrency(row.balance)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress
                            value={row.pct}
                            className="h-1.5 flex-1"
                            indicatorClassName={
                              row.pct >= 90
                                ? 'bg-red-500'
                                : row.pct >= 60
                                ? 'bg-green-500'
                                : 'bg-[#5e6ad2]'
                            }
                          />
                          <span className="text-xs text-gray-500 w-8 text-right shrink-0">
                            {row.pct}%
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {(data?.rows ?? []).length === 0 && (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center text-gray-400 py-12">
                        Нет данных за {year} год
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
                {data?.totals && (
                  <TableFooter>
                    <TableRow>
                      <TableCell></TableCell>
                      <TableCell className="font-semibold text-gray-900">ИТОГО</TableCell>
                      <TableCell className="text-right font-semibold tabular-nums">
                        {formatCurrency(data.totals.limit)}
                      </TableCell>
                      <TableCell className="text-right font-semibold tabular-nums">
                        {formatCurrency(data.totals.requested)}
                      </TableCell>
                      <TableCell className="text-right font-semibold tabular-nums">
                        {formatCurrency(data.totals.approved)}
                      </TableCell>
                      <TableCell className="text-right font-semibold tabular-nums">
                        {formatCurrency(data.totals.fact)}
                      </TableCell>
                      <TableCell className="text-right font-semibold tabular-nums">
                        {formatCurrency(data.totals.balance)}
                      </TableCell>
                      <TableCell></TableCell>
                    </TableRow>
                  </TableFooter>
                )}
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  )
}
