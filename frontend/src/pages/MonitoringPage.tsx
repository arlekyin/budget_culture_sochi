import { useState, FormEvent } from 'react'
import { Loader2, Plus, TrendingUp, BookMarked } from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import { useInstitutions } from '@/hooks/useInstitutions'
import { useClassifiers } from '@/hooks/useReport'
import {
  useFactPayments,
  useReservations,
  useAddFactPayment,
  useAddReservation,
} from '@/hooks/useMonitoring'
import { formatCurrency, formatDate } from '@/lib/utils'

const YEARS = [2024, 2025, 2026, 2027]

const RESERVATION_STATUS_COLORS: Record<string, string> = {
  active: 'bg-blue-50 text-blue-700 border-blue-200',
  closed: 'bg-green-50 text-green-700 border-green-200',
  cancelled: 'bg-gray-50 text-gray-500 border-gray-200',
}

export default function MonitoringPage() {
  const { user } = useAuth()
  const [year, setYear] = useState(new Date().getFullYear())
  const [tab, setTab] = useState<'fact' | 'reservations'>('fact')

  const isAccountant = user?.role === 'accountant' || user?.role === 'admin'
  const isDirector = user?.role === 'director'

  const { data: payments = [], isLoading: paymentsLoading } = useFactPayments(year)
  const { data: reservations = [], isLoading: reservationsLoading } = useReservations(year)
  const { data: institutions = [] } = useInstitutions()
  const { kosgu } = useClassifiers()
  const addPayment = useAddFactPayment(year)
  const addReservation = useAddReservation(year)

  // Fact payment form
  const [fpInstitution, setFpInstitution] = useState('')
  const [fpKosgu, setFpKosgu] = useState('')
  const [fpAmount, setFpAmount] = useState('')
  const [fpDate, setFpDate] = useState('')
  const [fpDesc, setFpDesc] = useState('')
  const [fpDocNum, setFpDocNum] = useState('')
  const [fpError, setFpError] = useState('')

  // Reservation form
  const [rInstitution, setRInstitution] = useState('')
  const [rKosgu, setRKosgu] = useState('')
  const [rContractNum, setRContractNum] = useState('')
  const [rContractor, setRContractor] = useState('')
  const [rAmount, setRAmount] = useState('')
  const [rDate, setRDate] = useState('')
  const [rNote, setRNote] = useState('')
  const [rError, setRError] = useState('')

  const [showFactForm, setShowFactForm] = useState(false)
  const [showResForm, setShowResForm] = useState(false)

  const handleAddPayment = async (e: FormEvent) => {
    e.preventDefault()
    setFpError('')
    try {
      await addPayment.mutateAsync({
        institution: parseInt(fpInstitution),
        kosgu: parseInt(fpKosgu),
        year,
        amount: fpAmount,
        payment_date: fpDate,
        description: fpDesc,
        document_number: fpDocNum,
      })
      setFpInstitution('')
      setFpKosgu('')
      setFpAmount('')
      setFpDate('')
      setFpDesc('')
      setFpDocNum('')
      setShowFactForm(false)
    } catch (err: unknown) {
      const e = err as { response?: { data?: Record<string, string[]> } }
      setFpError(Object.values(e.response?.data ?? {}).flat().join('\n') || 'Ошибка')
    }
  }

  const handleAddReservation = async (e: FormEvent) => {
    e.preventDefault()
    setRError('')
    const institutionId = isDirector
      ? user?.institution?.id
      : parseInt(rInstitution)
    if (!institutionId) {
      setRError('Не удалось определить учреждение.')
      return
    }
    try {
      await addReservation.mutateAsync({
        institution: institutionId,
        kosgu: parseInt(rKosgu),
        year,
        contract_number: rContractNum,
        contractor: rContractor,
        amount: rAmount,
        contract_date: rDate,
        note: rNote,
      })
      setRInstitution('')
      setRKosgu('')
      setRContractNum('')
      setRContractor('')
      setRAmount('')
      setRDate('')
      setRNote('')
      setShowResForm(false)
    } catch (err: unknown) {
      const e = err as { response?: { data?: Record<string, string[]> } }
      setRError(Object.values(e.response?.data ?? {}).flat().join('\n') || 'Ошибка')
    }
  }

  return (
    <Layout>
      <TopBar title="Мониторинг исполнения">
        <Select value={String(year)} onValueChange={(v) => setYear(parseInt(v))}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {YEARS.map((y) => (
              <SelectItem key={y} value={String(y)}>
                {y} год
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TopBar>

      <div className="p-6 space-y-5">
        {/* Tab switcher */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          {[
            { key: 'fact', label: 'Кассовые расходы', icon: <TrendingUp size={14} /> },
            { key: 'reservations', label: 'Бронирования', icon: <BookMarked size={14} /> },
          ].map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key as 'fact' | 'reservations')}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                tab === t.key
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>

        {/* FACT PAYMENTS TAB */}
        {tab === 'fact' && (
          <>
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Оплаченные счета за {year} год — итого:{' '}
                <span className="font-semibold text-gray-900">
                  {formatCurrency(
                    payments.reduce((s, p) => s + parseFloat(p.amount), 0).toString()
                  )}
                </span>
              </p>
              {isAccountant && (
                <Button size="sm" onClick={() => setShowFactForm(!showFactForm)}>
                  <Plus size={14} />
                  Добавить расход
                </Button>
              )}
            </div>

            {showFactForm && isAccountant && (
              <Card>
                <CardHeader>
                  <CardTitle>Новый кассовый расход</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleAddPayment} className="space-y-4">
                    <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
                      <div className="space-y-1.5">
                        <Label>Учреждение *</Label>
                        <Select value={fpInstitution} onValueChange={setFpInstitution} required>
                          <SelectTrigger>
                            <SelectValue placeholder="Выберите учреждение" />
                          </SelectTrigger>
                          <SelectContent>
                            {institutions.map((inst) => (
                              <SelectItem key={inst.id} value={String(inst.id)}>
                                {inst.short_name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-1.5">
                        <Label>КОСГУ *</Label>
                        <Select value={fpKosgu} onValueChange={setFpKosgu} required>
                          <SelectTrigger>
                            <SelectValue placeholder="Выберите КОСГУ" />
                          </SelectTrigger>
                          <SelectContent>
                            {(kosgu.data ?? []).map((k) => (
                              <SelectItem key={k.id} value={String(k.id)}>
                                {k.code} — {k.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-1.5">
                        <Label>Сумма (руб.) *</Label>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                          value={fpAmount}
                          onChange={(e) => setFpAmount(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-1.5">
                        <Label>Дата платежа *</Label>
                        <Input
                          type="date"
                          value={fpDate}
                          onChange={(e) => setFpDate(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-1.5">
                        <Label>Номер документа</Label>
                        <Input
                          type="text"
                          placeholder="П-001"
                          value={fpDocNum}
                          onChange={(e) => setFpDocNum(e.target.value)}
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <Label>Назначение платежа *</Label>
                      <Input
                        type="text"
                        placeholder="Оплата услуг ..."
                        value={fpDesc}
                        onChange={(e) => setFpDesc(e.target.value)}
                        required
                      />
                    </div>

                    {fpError && (
                      <div className="rounded-lg bg-red-50 border border-red-100 px-3 py-2 text-sm text-red-700 whitespace-pre-line">
                        {fpError}
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button type="submit" disabled={addPayment.isPending}>
                        {addPayment.isPending && <Loader2 size={14} className="animate-spin" />}
                        Сохранить
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={() => setShowFactForm(false)}
                      >
                        Отмена
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardContent className="p-0">
                {paymentsLoading ? (
                  <div className="flex justify-center py-10">
                    <Loader2 size={20} className="animate-spin text-gray-400" />
                  </div>
                ) : payments.length === 0 ? (
                  <div className="text-center text-gray-400 text-sm py-10">
                    Нет данных за {year} год
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Дата</TableHead>
                        <TableHead>Учреждение</TableHead>
                        <TableHead>КОСГУ</TableHead>
                        <TableHead>Назначение</TableHead>
                        <TableHead>№ документа</TableHead>
                        <TableHead className="text-right">Сумма</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {payments.map((p) => (
                        <TableRow key={p.id}>
                          <TableCell className="text-xs text-gray-500 whitespace-nowrap">
                            {formatDate(p.payment_date)}
                          </TableCell>
                          <TableCell className="text-sm">{p.institution_name}</TableCell>
                          <TableCell className="font-mono text-xs">{p.kosgu_display}</TableCell>
                          <TableCell className="text-sm max-w-xs">
                            <span className="line-clamp-2">{p.description}</span>
                          </TableCell>
                          <TableCell className="text-xs text-gray-500">
                            {p.document_number || '—'}
                          </TableCell>
                          <TableCell className="text-right font-medium text-sm">
                            {formatCurrency(p.amount)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {/* RESERVATIONS TAB */}
        {tab === 'reservations' && (
          <>
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Зарезервированные средства за {year} год — итого:{' '}
                <span className="font-semibold text-gray-900">
                  {formatCurrency(
                    reservations
                      .filter((r) => r.status === 'active')
                      .reduce((s, r) => s + parseFloat(r.amount), 0)
                      .toString()
                  )}
                </span>{' '}
                <span className="text-gray-400">(активные)</span>
              </p>
              {(isAccountant || isDirector) && (
                <Button size="sm" onClick={() => setShowResForm(!showResForm)}>
                  <Plus size={14} />
                  Добавить бронирование
                </Button>
              )}
            </div>

            {showResForm && (
              <Card>
                <CardHeader>
                  <CardTitle>Новое бронирование</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleAddReservation} className="space-y-4">
                    <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
                      {isAccountant && (
                        <div className="space-y-1.5">
                          <Label>Учреждение *</Label>
                          <Select value={rInstitution} onValueChange={setRInstitution} required>
                            <SelectTrigger>
                              <SelectValue placeholder="Выберите учреждение" />
                            </SelectTrigger>
                            <SelectContent>
                              {institutions.map((inst) => (
                                <SelectItem key={inst.id} value={String(inst.id)}>
                                  {inst.short_name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      <div className="space-y-1.5">
                        <Label>КОСГУ *</Label>
                        <Select value={rKosgu} onValueChange={setRKosgu} required>
                          <SelectTrigger>
                            <SelectValue placeholder="Выберите КОСГУ" />
                          </SelectTrigger>
                          <SelectContent>
                            {(kosgu.data ?? []).map((k) => (
                              <SelectItem key={k.id} value={String(k.id)}>
                                {k.code} — {k.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-1.5">
                        <Label>№ договора *</Label>
                        <Input
                          type="text"
                          placeholder="2025/001"
                          value={rContractNum}
                          onChange={(e) => setRContractNum(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-1.5">
                        <Label>Контрагент *</Label>
                        <Input
                          type="text"
                          placeholder="ООО «Пример»"
                          value={rContractor}
                          onChange={(e) => setRContractor(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-1.5">
                        <Label>Сумма (руб.) *</Label>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                          value={rAmount}
                          onChange={(e) => setRAmount(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-1.5">
                        <Label>Дата договора *</Label>
                        <Input
                          type="date"
                          value={rDate}
                          onChange={(e) => setRDate(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <Label>Примечание</Label>
                      <Input
                        type="text"
                        placeholder="Необязательно"
                        value={rNote}
                        onChange={(e) => setRNote(e.target.value)}
                      />
                    </div>

                    {rError && (
                      <div className="rounded-lg bg-red-50 border border-red-100 px-3 py-2 text-sm text-red-700 whitespace-pre-line">
                        {rError}
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button type="submit" disabled={addReservation.isPending}>
                        {addReservation.isPending && (
                          <Loader2 size={14} className="animate-spin" />
                        )}
                        Сохранить
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={() => setShowResForm(false)}
                      >
                        Отмена
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardContent className="p-0">
                {reservationsLoading ? (
                  <div className="flex justify-center py-10">
                    <Loader2 size={20} className="animate-spin text-gray-400" />
                  </div>
                ) : reservations.length === 0 ? (
                  <div className="text-center text-gray-400 text-sm py-10">
                    Нет бронирований за {year} год
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Дата</TableHead>
                        <TableHead>Учреждение</TableHead>
                        <TableHead>КОСГУ</TableHead>
                        <TableHead>Контрагент</TableHead>
                        <TableHead>№ договора</TableHead>
                        <TableHead>Статус</TableHead>
                        <TableHead className="text-right">Сумма</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {reservations.map((r) => (
                        <TableRow key={r.id}>
                          <TableCell className="text-xs text-gray-500 whitespace-nowrap">
                            {formatDate(r.contract_date)}
                          </TableCell>
                          <TableCell className="text-sm">{r.institution_name}</TableCell>
                          <TableCell className="font-mono text-xs">{r.kosgu_display}</TableCell>
                          <TableCell className="text-sm max-w-[180px]">
                            <span className="line-clamp-1">{r.contractor}</span>
                          </TableCell>
                          <TableCell className="text-xs text-gray-500">{r.contract_number}</TableCell>
                          <TableCell>
                            <span
                              className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium border ${
                                RESERVATION_STATUS_COLORS[r.status] ?? ''
                              }`}
                            >
                              {r.status_display}
                            </span>
                          </TableCell>
                          <TableCell className="text-right font-medium text-sm">
                            {formatCurrency(r.amount)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </Layout>
  )
}
