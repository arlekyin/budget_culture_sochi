import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-white font-sans">
      {/* Dark sidebar */}
      <aside className="flex-shrink-0 h-full overflow-hidden">
        <Sidebar />
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden bg-white">
        <div className="flex-1 overflow-y-auto">{children}</div>
      </main>
    </div>
  )
}
