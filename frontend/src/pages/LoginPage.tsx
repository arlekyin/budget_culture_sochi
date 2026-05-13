import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building, Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard', { replace: true })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(
        axiosErr.response?.data?.detail ??
          'Ошибка при входе. Проверьте логин и пароль.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center font-sans"
      style={{
        background: 'linear-gradient(135deg, #0f0f10 0%, #16161f 50%, #0f0f10 100%)',
      }}
    >
      <div className="w-full max-w-sm">
        {/* Card */}
        <div
          className="rounded-2xl border p-8"
          style={{
            background: 'rgba(255,255,255,0.04)',
            borderColor: 'rgba(255,255,255,0.08)',
            backdropFilter: 'blur(20px)',
          }}
        >
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div
              className="flex items-center justify-center rounded-xl mb-4"
              style={{ width: 48, height: 48, background: '#5e6ad2' }}
            >
              <Building size={24} className="text-white" />
            </div>
            <h1 className="text-white text-xl font-semibold text-center">
              Бюджет-Культура Сочи
            </h1>
            <p className="text-sm text-center mt-1" style={{ color: '#8b8b9e' }}>
              МКУ «ЦБ УК г. Сочи»
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="username" className="text-white/70 text-xs">
                Логин
              </Label>
              <Input
                id="username"
                type="text"
                autoComplete="username"
                placeholder="Введите логин"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="bg-white/[0.06] border-white/10 text-white placeholder:text-white/30 focus:ring-[#5e6ad2]"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-white/70 text-xs">
                Пароль
              </Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="Введите пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-white/[0.06] border-white/10 text-white placeholder:text-white/30 focus:ring-[#5e6ad2]"
              />
            </div>

            {error && (
              <div
                className="rounded-lg px-3 py-2.5 text-sm"
                style={{
                  background: 'rgba(239,68,68,0.12)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  color: '#fca5a5',
                }}
              >
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="w-full mt-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Входим...
                </>
              ) : (
                'Войти в систему'
              )}
            </Button>
          </form>
        </div>

        <p className="text-center text-xs mt-6" style={{ color: '#4a4a5a' }}>
          © 2026 Управление культуры Администрации г. Сочи
        </p>
      </div>
    </div>
  )
}
