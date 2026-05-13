import { cn } from '@/lib/utils'

interface TopBarProps {
  title: string
  children?: React.ReactNode
  className?: string
}

export function TopBar({ title, children, className }: TopBarProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-white',
        className
      )}
    >
      <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </div>
  )
}
