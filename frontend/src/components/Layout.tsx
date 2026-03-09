import { useState } from 'react'
import { Zap, BarChart3, FileText, Settings, LogOut, Menu, X, Bell, User, Search } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    { icon: BarChart3, label: 'Dashboard', href: '/dashboard', color: 'text-blue-400' },
    { icon: Zap, label: 'Energy', href: '/energy', color: 'text-yellow-400' },
    { icon: FileText, label: 'Reports', href: '/reports', color: 'text-green-400' },
    { icon: Settings, label: 'Settings', href: '/settings', color: 'text-purple-400' },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Left Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen bg-gradient-to-b from-slate-900 to-slate-950 border-r border-slate-800/50 backdrop-blur-xl transition-all duration-300 z-40 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        {/* Logo */}
        <div className="h-20 flex items-center justify-between px-6 border-b border-slate-800/50">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <Zap className="w-8 h-8 text-blue-400" />
              <span className="font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                iNetZero
              </span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-800 rounded-lg transition"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.href}
                onClick={() => navigate(item.href)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition group ${
                  isActive(item.href)
                    ? 'bg-blue-600/20 border border-blue-500/50 text-white'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                }`}
              >
                <Icon className={`w-5 h-5 ${item.color} group-hover:scale-110 transition`} />
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </button>
            )
          })}
        </nav>

        {/* Bottom User Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800/50">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800/50 transition text-slate-400 hover:text-white">
            <User className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm font-medium">Profile</span>}
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-900/20 hover:text-red-400 transition text-slate-400 mt-2">
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Top Header */}
        <header className="h-20 bg-gradient-to-r from-slate-900/80 to-slate-900/80 backdrop-blur-xl border-b border-slate-800/50 flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center gap-4 flex-1">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:border-blue-500/50 focus:outline-none transition"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications */}
            <button className="relative p-2 hover:bg-slate-800 rounded-lg transition">
              <Bell className="w-5 h-5 text-slate-400 hover:text-white transition" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* User Menu */}
            <div className="flex items-center gap-3 pl-4 border-l border-slate-700/50">
              <div className="text-right">
                <p className="text-sm font-medium text-white">John Doe</p>
                <p className="text-xs text-slate-400">Admin</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center text-white font-bold">
                JD
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6 min-h-[calc(100vh-80px)]">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>

        {/* Bottom Footer */}
        <footer className="bg-gradient-to-r from-slate-900/50 to-slate-900/50 backdrop-blur-xl border-t border-slate-800/50 px-6 py-4">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="text-sm text-slate-400">
              © 2026 iNetZero ESG Platform. All rights reserved.
            </div>
            <div className="flex gap-6 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition">
                Security
              </a>
              <a href="#" className="hover:text-white transition">
                Compliance
              </a>
              <a href="#" className="hover:text-white transition">
                Support
              </a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
