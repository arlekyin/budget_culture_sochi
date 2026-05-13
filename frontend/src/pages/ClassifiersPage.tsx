import { useState } from 'react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useClassifiers } from '@/hooks/useReport'
import { Skeleton } from '@/components/ui/skeleton'

export default function ClassifiersPage() {
  const { kosgu, kvr } = useClassifiers()
  const [kosguSearch, setKosguSearch] = useState('')
  const [kvrSearch, setKvrSearch] = useState('')

  const filteredKosgu = (kosgu.data ?? []).filter(
    (k) =>
      k.code.includes(kosguSearch) ||
      k.name.toLowerCase().includes(kosguSearch.toLowerCase())
  )

  const filteredKvr = (kvr.data ?? []).filter(
    (k) =>
      k.code.includes(kvrSearch) ||
      k.name.toLowerCase().includes(kvrSearch.toLowerCase())
  )

  return (
    <Layout>
      <TopBar title="Бюджетные классификаторы" />

      <div className="p-6 space-y-6 max-w-5xl">
        {/* KOSGU */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardTitle className="text-sm font-semibold text-gray-700">
                  КОСГУ — Классификатор операций сектора государственного управления
                </CardTitle>
                <p className="text-xs text-gray-400 mt-0.5">
                  Определяет экономическое содержание операции
                </p>
              </div>
              {kosgu.data && (
                <Badge variant="default">{kosgu.data.length} записей</Badge>
              )}
            </div>
            <div className="pt-2">
              <Input
                placeholder="Поиск по коду или наименованию..."
                value={kosguSearch}
                onChange={(e) => setKosguSearch(e.target.value)}
                className="max-w-sm"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {kosgu.isLoading ? (
              <div className="p-4 space-y-2">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-8 w-full" />
                ))}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-24">Код</TableHead>
                    <TableHead>Наименование</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredKosgu.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={2} className="text-center text-gray-400 py-6">
                        Ничего не найдено
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredKosgu.map((k) => (
                      <TableRow key={k.id}>
                        <TableCell>
                          <span className="font-mono font-semibold text-[#5e6ad2]">{k.code}</span>
                        </TableCell>
                        <TableCell className="text-sm text-gray-800">{k.name}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* KVR */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardTitle className="text-sm font-semibold text-gray-700">
                  КВР — Коды видов расходов
                </CardTitle>
                <p className="text-xs text-gray-400 mt-0.5">
                  Группируют расходы по направлениям деятельности
                </p>
              </div>
              {kvr.data && (
                <Badge variant="default">{kvr.data.length} записей</Badge>
              )}
            </div>
            <div className="pt-2">
              <Input
                placeholder="Поиск по коду или наименованию..."
                value={kvrSearch}
                onChange={(e) => setKvrSearch(e.target.value)}
                className="max-w-sm"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {kvr.isLoading ? (
              <div className="p-4 space-y-2">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-8 w-full" />
                ))}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-24">Код</TableHead>
                    <TableHead>Наименование</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredKvr.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={2} className="text-center text-gray-400 py-6">
                        Ничего не найдено
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredKvr.map((k) => (
                      <TableRow key={k.id}>
                        <TableCell>
                          <span className="font-mono font-semibold text-[#5e6ad2]">{k.code}</span>
                        </TableCell>
                        <TableCell className="text-sm text-gray-800">{k.name}</TableCell>
                      </TableRow>
                    ))
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
