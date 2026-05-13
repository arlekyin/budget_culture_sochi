import { useState, FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  AlertTriangle,
  Trash2,
  Plus,
  Loader2,
  ExternalLink,
  MessageSquare,
  History,
} from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { TopBar } from '@/components/layout/TopBar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import {
  useRequest,
  useSubmitRequest,
  useReviewRequest,
  useAddLine,
  useDeleteLine,
  useLineLogs,
} from '@/hooks/useRequest'
import { useClassifiers } from '@/hooks/useReport'
import { formatCurrency, formatDate, getStatusColor, getStatusLabel } from '@/lib/utils'

export default function RequestDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()

  const { data: req, isLoading } = useRequest(id!)
  const submitMutation = useSubmitRequest(id!)
  const reviewMutation = useReviewRequest(id!)
  const addLineMutation = useAddLine(id!)
  const deleteLineMutation = useDeleteLine(id!)
  const { data: lineLogs = [] } = useLineLogs(id!)
  const { kosgu, kvr } = useClassifiers()

  // Review form state
  const [reviewAction, setReviewAction] = useState<'approve' | 'return' | 'reject'>('approve')
  const [approvedAmount, setApprovedAmount] = useState('')
  const [reviewComment, setReviewComment] = useState('')

  // Add line form state
  const [lineKosgu, setLineKosgu] = useState('')
  const [lineKvr, setLineKvr] = useState('')
  const [lineDesc, setLineDesc] = useState('')
  const [linePrice, setLinePrice] = useState('')
  const [lineQty, setLineQty] = useState('1')
  const [lineFile, setLineFile] = useState<File | null>(null)
  const [lineNote, setLineNote] = useState('')

  if (isLoading) {
    return (
      <Layout>
        <TopBar title="Загрузка..." />
        <div className="p-6 space-y-4">
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </Layout>
    )
  }

  if (!req) {
    return (
      <Layout>
        <TopBar title="Заявка не найдена" />
        <div className="p-6">
          <p className="text-gray-500">Заявка не найдена или у вас нет доступа.</p>
        </div>
      </Layout>
    )
  }

  const statusColors = getStatusColor(req.status)
  const isDirector = user?.role === 'director'
  const isAccountant = user?.role === 'accountant' || user?.role === 'admin'
  const canEdit = isDirector && (req.status === 'draft' || req.status === 'returned')
  const canSubmit = isDirector && (req.status === 'draft' || req.status === 'returned')
  const canReview = isAccountant && req.status === 'submitted'

  const handleSubmit = async () => {
    try {
      await submitMutation.mutateAsync()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      alert(e.response?.data?.detail ?? 'Ошибка при отправке заявки')
    }
  }

  const handleReview = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await reviewMutation.mutateAsync({
        action: reviewAction,
        approved_amount: reviewAction === 'approve' ? approvedAmount : undefined,
        comment: reviewComment,
      })
    } catch (err: unknown) {
      const e = err as { response?: { data?: Record<string, string[]> } }
      const errs = e.response?.data
      if (errs) {
        alert(Object.values(errs).flat().join('\n'))
      }
    }
  }

  const handleAddLine = async (e: FormEvent) => {
    e.preventDefault()
    const formData = new FormData()
    formData.append('kosgu', lineKosgu)
    if (lineKvr && lineKvr !== '__none__') formData.append('kvr', lineKvr)
    formData.append('description', lineDesc)
    formData.append('unit_price', linePrice)
    formData.append('quantity', lineQty)
    if (lineNote) formData.append('note', lineNote)
    if (lineFile) formData.append('attachment', lineFile)

    try {
      await addLineMutation.mutateAsync(formData)
      setLineKosgu('')
      setLineKvr('')
      setLineDesc('')
      setLinePrice('')
      setLineQty('1')
      setLineFile(null)
      setLineNote('')
    } catch (err: unknown) {
      const e = err as { response?: { data?: Record<string, string[]> } }
      const errs = e.response?.data
      if (errs) {
        alert(Object.values(errs).flat().join('\n'))
      }
    }
  }

  const handleDeleteLine = async (lineId: number) => {
    if (!confirm('Удалить строку из заявки?')) return
    try {
      await deleteLineMutation.mutateAsync(lineId)
    } catch {
      alert('Ошибка при удалении строки')
    }
  }

  return (
    <Layout>
      <TopBar
        title={`Заявка #${req.id}`}
      >
        <Button variant="ghost" size="sm" onClick={() => navigate('/requests')}>
          <ArrowLeft size={14} />
          Назад
        </Button>
      </TopBar>

      <div className="p-6 space-y-5">
        {/* Header card */}
        <Card>
          <CardContent className="pt-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-1">
                  Заявка #{req.id}
                </h2>
                <p className="text-gray-500 text-sm">{req.institution_name}</p>
              </div>
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium border ${statusColors.bg} ${statusColors.text} ${statusColors.border}`}
              >
                {getStatusLabel(req.status)}
              </span>
            </div>

            {/* Info grid */}
            <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm lg:grid-cols-4">
              <InfoItem label="Период" value={`${req.period_year} (${req.period_type_display})`} />
              <InfoItem label="Тип средств" value={req.funding_type_display} />
              <InfoItem
                label="Дедлайн"
                value={req.deadline ? formatDate(req.deadline) : '—'}
              />
              <InfoItem
                label="Проверил"
                value={req.reviewed_by_name || '—'}
              />
              {req.reviewed_at && (
                <InfoItem label="Дата проверки" value={formatDate(req.reviewed_at)} />
              )}
              {req.created_by_name && (
                <InfoItem label="Создал" value={req.created_by_name} />
              )}
            </div>
          </CardContent>
        </Card>

        {/* Comment alert */}
        {req.comment && (
          <div className="flex items-start gap-3 rounded-xl border border-orange-100 bg-orange-50 px-4 py-3">
            <MessageSquare size={16} className="text-orange-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800 mb-0.5">Комментарий бухгалтера</p>
              <p className="text-sm text-orange-700">{req.comment}</p>
            </div>
          </div>
        )}

        {/* Amounts */}
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardContent className="pt-5">
              <p className="text-xs text-gray-500 mb-1">Заявленная сумма</p>
              <p className="text-2xl font-semibold text-blue-600">
                {formatCurrency(req.total_amount)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-5">
              <p className="text-xs text-gray-500 mb-1">Согласованная сумма</p>
              <p className="text-2xl font-semibold text-green-600">
                {req.approved_amount ? formatCurrency(req.approved_amount) : '—'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Director actions */}
        {canSubmit && (
          <Card>
            <CardContent className="pt-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Отправить на согласование</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {req.lines.length === 0
                      ? 'Добавьте хотя бы одну строку перед отправкой'
                      : `Заявка содержит ${req.lines.length} строк(у)`}
                  </p>
                </div>
                <Button
                  onClick={handleSubmit}
                  disabled={submitMutation.isPending || req.lines.length === 0}
                >
                  {submitMutation.isPending && <Loader2 size={14} className="animate-spin" />}
                  Отправить
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Accountant review */}
        {canReview && (
          <Card>
            <CardHeader>
              <CardTitle>Действие по заявке</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleReview} className="space-y-4">
                <div className="flex gap-3">
                  {[
                    { value: 'approve', label: 'Согласовать', color: 'text-green-600' },
                    { value: 'return', label: 'Вернуть', color: 'text-orange-600' },
                    { value: 'reject', label: 'Отклонить', color: 'text-red-600' },
                  ].map((opt) => (
                    <label
                      key={opt.value}
                      className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border cursor-pointer transition-colors ${
                        reviewAction === opt.value
                          ? 'border-[#5e6ad2] bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="action"
                        value={opt.value}
                        checked={reviewAction === opt.value}
                        onChange={() =>
                          setReviewAction(opt.value as 'approve' | 'return' | 'reject')
                        }
                        className="sr-only"
                      />
                      <span className={`text-sm font-medium ${opt.color}`}>{opt.label}</span>
                    </label>
                  ))}
                </div>

                {reviewAction === 'approve' && (
                  <div className="space-y-1.5">
                    <Label>Согласованная сумма (руб.)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder={req.total_amount}
                      value={approvedAmount}
                      onChange={(e) => setApprovedAmount(e.target.value)}
                      required
                      className="max-w-xs"
                    />
                  </div>
                )}

                <div className="space-y-1.5">
                  <Label>Комментарий</Label>
                  <textarea
                    className="flex w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#5e6ad2] min-h-[80px] resize-none"
                    placeholder="Необязательный комментарий..."
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                  />
                </div>

                <Button type="submit" disabled={reviewMutation.isPending}>
                  {reviewMutation.isPending && <Loader2 size={14} className="animate-spin" />}
                  Подтвердить
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Lines table */}
        <Card>
          <CardHeader>
            <CardTitle>Строки заявки</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>КОСГУ</TableHead>
                  <TableHead>КВР</TableHead>
                  <TableHead>Детализация</TableHead>
                  <TableHead>Цена</TableHead>
                  <TableHead>Кол-во</TableHead>
                  <TableHead>Итого</TableHead>
                  <TableHead>Файл</TableHead>
                  {canEdit && <TableHead></TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {req.lines.map((line) => (
                  <TableRow key={line.id}>
                    <TableCell className="font-mono text-xs">{line.kosgu_display}</TableCell>
                    <TableCell className="font-mono text-xs">{line.kvr_display ?? '—'}</TableCell>
                    <TableCell className="max-w-xs">
                      <span className="line-clamp-2 text-sm">{line.description}</span>
                      {line.note && (
                        <span className="text-xs text-gray-400 block mt-0.5">{line.note}</span>
                      )}
                    </TableCell>
                    <TableCell>{formatCurrency(line.unit_price)}</TableCell>
                    <TableCell>{line.quantity}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(line.amount)}</TableCell>
                    <TableCell>
                      {line.attachment_url ? (
                        <a
                          href={line.attachment_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#5e6ad2] hover:underline flex items-center gap-1 text-xs"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink size={12} />
                          Файл
                        </a>
                      ) : (
                        <span className="text-gray-300 text-xs">—</span>
                      )}
                    </TableCell>
                    {canEdit && (
                      <TableCell>
                        <button
                          onClick={() => handleDeleteLine(line.id)}
                          className="text-red-400 hover:text-red-600 transition-colors p-1 rounded"
                          disabled={deleteLineMutation.isPending}
                        >
                          <Trash2 size={14} />
                        </button>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
                {req.lines.length === 0 && (
                  <TableRow>
                    <TableCell
                      colSpan={canEdit ? 8 : 7}
                      className="text-center text-gray-400 py-10"
                    >
                      Строк пока нет
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Attachments section */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <ExternalLink size={14} className="text-[#5e6ad2]" />
              Файлы-обоснования
            </CardTitle>
          </CardHeader>
          <CardContent>
            {req.lines.filter((l) => l.attachment_url).length === 0 ? (
              <p className="text-sm text-gray-400">
                {canEdit
                  ? 'Прикрепите файл при добавлении строки ниже.'
                  : 'Файлы не прикреплены.'}
              </p>
            ) : (
              <ul className="space-y-2">
                {req.lines
                  .filter((l) => l.attachment_url)
                  .map((l) => (
                    <li key={l.id} className="flex items-center gap-3 text-sm">
                      <span className="text-gray-500 flex-1 truncate">{l.description}</span>
                      <a
                        href={l.attachment_url!}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-[#5e6ad2] hover:underline whitespace-nowrap"
                      >
                        <ExternalLink size={12} />
                        Открыть файл
                      </a>
                    </li>
                  ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Change log */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <History size={14} className="text-[#5e6ad2]" />
              История изменений строк
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {lineLogs.length === 0 ? (
              <p className="text-sm text-gray-400 px-6 py-4">Изменений не зафиксировано.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Строка</TableHead>
                    <TableHead>Было</TableHead>
                    <TableHead>Стало</TableHead>
                    <TableHead>Изменил</TableHead>
                    <TableHead>Дата</TableHead>
                    <TableHead>Комментарий</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lineLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="text-sm max-w-[180px]">
                        <span className="line-clamp-1">{log.line_description}</span>
                      </TableCell>
                      <TableCell className="font-mono text-sm text-red-600">
                        {formatCurrency(log.old_amount)}
                      </TableCell>
                      <TableCell className="font-mono text-sm text-green-700">
                        {formatCurrency(log.new_amount)}
                      </TableCell>
                      <TableCell className="text-xs text-gray-600">{log.changed_by_name}</TableCell>
                      <TableCell className="text-xs text-gray-400 whitespace-nowrap">
                        {formatDate(log.changed_at)}
                      </TableCell>
                      <TableCell className="text-xs text-gray-500">{log.comment || '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Add line form */}
        {canEdit && (
          <Card>
            <CardHeader>
              <CardTitle>Добавить строку</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddLine} className="space-y-4">
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                  <div className="space-y-1.5">
                    <Label>КОСГУ *</Label>
                    <Select value={lineKosgu} onValueChange={setLineKosgu} required>
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
                    <Label>КВР</Label>
                    <Select value={lineKvr} onValueChange={setLineKvr}>
                      <SelectTrigger>
                        <SelectValue placeholder="Выберите КВР" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__none__">Не указан</SelectItem>
                        {(kvr.data ?? []).map((k) => (
                          <SelectItem key={k.id} value={String(k.id)}>
                            {k.code} — {k.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-1.5">
                    <Label>Цена (руб.) *</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="0.00"
                      value={linePrice}
                      onChange={(e) => setLinePrice(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label>Количество *</Label>
                    <Input
                      type="number"
                      step="0.001"
                      min="0"
                      placeholder="1"
                      value={lineQty}
                      onChange={(e) => setLineQty(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <Label>Детализация / Обоснование *</Label>
                  <Input
                    type="text"
                    placeholder="Описание расхода"
                    value={lineDesc}
                    onChange={(e) => setLineDesc(e.target.value)}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>Примечание</Label>
                    <Input
                      type="text"
                      placeholder="Необязательно"
                      value={lineNote}
                      onChange={(e) => setLineNote(e.target.value)}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Файл-обоснование</Label>
                    <Input
                      type="file"
                      onChange={(e) => setLineFile(e.target.files?.[0] ?? null)}
                      className="cursor-pointer"
                    />
                  </div>
                </div>

                <Button type="submit" disabled={addLineMutation.isPending || !lineKosgu}>
                  {addLineMutation.isPending ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Plus size={14} />
                  )}
                  Добавить строку
                </Button>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-400 mb-0.5">{label}</p>
      <p className="text-sm text-gray-800 font-medium">{value}</p>
    </div>
  )
}
