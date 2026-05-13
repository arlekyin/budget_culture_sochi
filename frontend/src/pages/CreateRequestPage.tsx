import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
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
import { useCreateRequest } from '@/hooks/useRequest'

export default function CreateRequestPage() {
  const navigate = useNavigate()
  const createMutation = useCreateRequest()

  const [periodYear, setPeriodYear] = useState(String(new Date().getFullYear()))
  const [periodType, setPeriodType] = useState('annual')
  const [periodQuarter, setPeriodQuarter] = useState('')
  const [fundingType, setFundingType] = useState('subsidy')
  const [deadline, setDeadline] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const req = await createMutation.mutateAsync({
        period_year: parseInt(periodYear),
        period_type: periodType,
        period_quarter: periodType === 'quarterly' && periodQuarter ? parseInt(periodQuarter) : null,
        funding_type: fundingType,
        deadline: deadline || undefined,
      })
      navigate(`/requests/${req.id}`)
    } catch (err: unknown) {
      const e = err as { response?: { data?: Record<string, string[]> | { detail?: string } } }
      const data = e.response?.data
      if (data && 'detail' in data) {
        setError(String(data.detail ?? 'Ошибка создания заявки'))
      } else if (data) {
        setError(Object.values(data).flat().join('\n'))
      } else {
        setError('Ошибка при создании заявки')
      }
    }
  }

  return (
    <Layout>
      <TopBar title="Новая заявка">
        <Button variant="ghost" size="sm" onClick={() => navigate('/requests')}>
          <ArrowLeft size={14} />
          Назад
        </Button>
      </TopBar>

      <div className="p-6 max-w-xl">
        <Card>
          <CardHeader>
            <CardTitle>Создание бюджетной заявки</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label>Год планирования *</Label>
                <Select value={periodYear} onValueChange={setPeriodYear}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[2024, 2025, 2026, 2027].map((y) => (
                      <SelectItem key={y} value={String(y)}>
                        {y}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Тип периода *</Label>
                <div className="flex gap-3">
                  {[
                    { value: 'annual', label: 'Годовая' },
                    { value: 'quarterly', label: 'Квартальная' },
                  ].map((opt) => (
                    <label
                      key={opt.value}
                      className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border cursor-pointer transition-colors ${
                        periodType === opt.value
                          ? 'border-[#5e6ad2] bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="periodType"
                        value={opt.value}
                        checked={periodType === opt.value}
                        onChange={() => setPeriodType(opt.value)}
                        className="sr-only"
                      />
                      <span className="text-sm font-medium text-gray-700">{opt.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {periodType === 'quarterly' && (
                <div className="space-y-1.5">
                  <Label>Квартал *</Label>
                  <Select value={periodQuarter} onValueChange={setPeriodQuarter} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Выберите квартал" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">I квартал</SelectItem>
                      <SelectItem value="2">II квартал</SelectItem>
                      <SelectItem value="3">III квартал</SelectItem>
                      <SelectItem value="4">IV квартал</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="space-y-1.5">
                <Label>Тип средств *</Label>
                <Select value={fundingType} onValueChange={setFundingType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="subsidy">Субсидия на выполнение задания</SelectItem>
                    <SelectItem value="paid">Платные услуги</SelectItem>
                    <SelectItem value="other">Иные цели</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1.5">
                <Label>Срок подачи</Label>
                <Input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 border border-red-100 px-3 py-2.5 text-sm text-red-700 whitespace-pre-line">
                  {error}
                </div>
              )}

              <Button type="submit" disabled={createMutation.isPending} className="w-full">
                {createMutation.isPending && <Loader2 size={14} className="animate-spin" />}
                Создать заявку
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
