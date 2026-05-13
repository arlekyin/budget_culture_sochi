import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  BarChart2,
  Building2,
  List,
  Settings,
  LogOut,
  Building,
  Plus,
  Activity,
  BookOpen,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

interface NavItem {
  to: string
  icon: React.ReactNode
  label: string
  roles?: string[]
  external?: boolean
}

const navItems: NavItem[] = [
  {
    to: '/dashboard',
    icon: <LayoutDashboard size={16} />,
    label: 'Дашборд',
  },
  {
    to: '/requests',
    icon: <FileText size={16} />,
    label: 'Заявки',
  },
  {
    to: '/monitoring',
    icon: <Activity size={16} />,
    label: 'Мониторинг',
  },
  {
    to: '/reports/consolidated',
    icon: <BarChart2 size={16} />,
    label: 'Сводная ведомость',
  },
  {
    to: '/institutions',
    icon: <Building2 size={16} />,
    label: 'Учреждения',
  },
  {
    to: '/classifiers',
    icon: <BookOpen size={16} />,
    label: 'Классификаторы',
  },
  {
    to: '/admin/',
    icon: <Settings size={16} />,
    label: 'Администрирование',
    roles: ['admin'],
    external: true,
  },
]

export function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const initials = user
    ? (user.firstName?.[0] ?? '') + (user.lastName?.[0] ?? user.username?.[0] ?? '')
    : '?'

  const filteredNav = navItems.filter((item) => {
    if (!item.roles) return true
    return user?.role && item.roles.includes(user.role)
  })

  return (
    <div
      className="flex flex-col h-full"
      style={{ width: 220, minWidth: 220, background: '#0f0f10' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b" style={{ borderColor: '#1f1f26' }}>
        <div
          className="flex items-center justify-center rounded-lg"
          style={{ width: 28, height: 28, background: '#5e6ad2' }}
        >
          <Building size={14} className="text-white" />
        </div>
        <div>
          <div className="text-white text-[13px] font-semibold leading-tight">Бюджет-Культура</div>
          <div className="text-[11px] leading-tight" style={{ color: '#8b8b9e' }}>
            г. Сочи
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {filteredNav.map((item) => (
          <SidebarNavItem key={item.to} item={item} />
        ))}

        {/* New request button for directors */}
        {user?.role === 'director' && (
          <div className="pt-2 pb-1">
            <NavLink
              to="/requests/new"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-colors group w-full',
                  isActive
                    ? 'bg-[#5e6ad2] text-white'
                    : 'text-[#8b8b9e] hover:bg-[#1a1a1f] hover:text-white'
                )
              }
            >
              <Plus size={14} />
              Новая заявка
            </NavLink>
          </div>
        )}
      </nav>

      {/* User info + Logout */}
      <div className="px-3 py-3 border-t" style={{ borderColor: '#1f1f26' }}>
        <div className="flex items-center gap-2.5 mb-2.5">
          <Avatar className="h-7 w-7 shrink-0">
            <AvatarFallback className="text-[10px]">{initials.toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <div className="text-white text-[12px] font-medium truncate leading-tight">
              {user?.firstName
                ? `${user.firstName} ${user.lastName ?? ''}`
                : user?.username}
            </div>
            <div className="text-[11px] truncate leading-tight" style={{ color: '#8b8b9e' }}>
              {user?.roleDisplay}
            </div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md text-[12px] w-full transition-colors"
          style={{ color: '#8b8b9e' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#1a1a1f'
            e.currentTarget.style.color = '#ffffff'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.color = '#8b8b9e'
          }}
        >
          <LogOut size={13} />
          Выйти
        </button>
      </div>
    </div>
  )
}

function SidebarNavItem({ item }: { item: NavItem }) {
  if (item.external) {
    return (
      <a
        href={item.to}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-colors"
        style={{ color: '#8b8b9e' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#1a1a1f'
          e.currentTarget.style.color = '#ffffff'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'transparent'
          e.currentTarget.style.color = '#8b8b9e'
        }}
      >
        {item.icon}
        {item.label}
      </a>
    )
  }

  return (
    <NavLink
      to={item.to}
      end={item.to === '/dashboard'}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-2.5 px-3 py-1.5 rounded-md text-[13px] font-medium transition-colors',
          isActive
            ? 'bg-[#1a1a1f] text-white'
            : 'text-[#8b8b9e] hover:bg-[#1a1a1f] hover:text-white'
        )
      }
    >
      {item.icon}
      {item.label}
    </NavLink>
  )
}
