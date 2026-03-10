import { useState } from 'react'
import { Zap, BarChart3, FileText, Settings, LogOut, Menu, X, Bell, User, Search, ShoppingCart, Wallet, TrendingUp, MessageSquare, CheckSquare, ClipboardList } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { usePendingApprovalsCount } from '../hooks/useApprovals'

interface LayoutProps {
  children: React.ReactNode
}

type NavItem =
  | { icon: React.ComponentType<any>; label: string; href: string; color: string; divider?: false }
  | { divider: true }

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const navigate = useNavigate()
  const pendingApprovalsCount = usePendingApprovalsCount()

  const navItems: NavItem[] = [
    { icon: BarChart3, label: 'Dashboard', href: '/dashboard', color: 'text-blue-400' },
    { icon: Zap, label: 'Energy', href: '/energy', color: 'text-yellow-400' },
    { icon: FileText, label: 'Reports', href: '/reports', color: 'text-green-400' },
    { icon: ClipboardList, label: 'Compliance', href: '/compliance', color: 'text-violet-400' },
    { divider: true },
    { icon: ShoppingCart, label: 'Marketplace', href: '/marketplace', color: 'text-cyan-400' },
    { icon: Wallet, label: 'Portfolio', href: '/portfolio', color: 'text-emerald-400' },
    { icon: TrendingUp, label: 'Trading', href: '/trading', color: 'text-orange-400' },
    { divider: true },
    { icon: CheckSquare, label: 'Approvals', href: '/approvals', color: 'text-indigo-400' },
    { icon: MessageSquare, label: 'Copilot', href: '/copilot', color: 'text-pink-400' },
    { icon: Settings, label: 'Settings', href: '/settings', color: 'text-purple-400' },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Left Sidebar Navigation */}
      <aside role="navigation" aria-label="Main navigation"
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
        <nav className="p-4 space-y-2" aria-label="Sidebar navigation">
          {navItems.map((item, index) => {
            if ('divider' in item && item.divider) {
              return <div key={`divider-${index}`} className="my-2 border-t border-slate-700/50" />
            }
            const Icon = item.icon
            return (
              <button
                key={item.href}
                onClick={() => navigate(item.href)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition group focus:outline-none focus:ring-2 focus:ring-primary-500/50 ${
                  isActive(item.href)
                    ? 'bg-blue-600/20 border border-blue-500/50 text-white'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                }`}
                aria-current={isActive(item.href) ? 'page' : undefined}
              >
                <Icon className={`w-5 h-5 ${item.color} group-hover:scale-110 transition`} />
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </button>
            )
          })}
        </nav>

        {/* Bottom User Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800/50">
          <button
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800/50 transition text-slate-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50"
            aria-label="View profile settings"
          >
            <User className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm font-medium">Profile</span>}
          </button>
          <button
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-900/20 hover:text-red-400 transition text-slate-400 mt-2 focus:outline-none focus:ring-2 focus:ring-danger-500/50"
            aria-label="Sign out of your account"
          >
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content - Full width on mobile, margin on md+ */}
      <div className={`transition-all duration-300 flex flex-col min-h-screen ${sidebarOpen ? 'md:ml-64' : 'md:ml-20'}`}>
        {/* Top Header */}
        <header className="h-20 bg-gradient-to-r from-slate-900/80 to-slate-900/80 backdrop-blur-xl border-b border-slate-800/50 flex items-center justify-between px-4 sm:px-6 sticky top-0 z-30" role="banner">
          {/* Mobile Menu Button - Show only on mobile */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 hover:bg-slate-800 rounded-lg transition"
            aria-label="Toggle sidebar menu"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-4 flex-1">
            {/* Search bar - Hidden on mobile to save space */}
            <div className="hidden sm:flex flex-1 max-w-md">
              <div className="relative w-full">
                <Search className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:border-blue-500/50 focus:outline-none transition"
                  aria-label="Search"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {/* Notifications */}
            <button
              onClick={() => navigate('/approvals')}
              className="relative p-2 hover:bg-slate-800 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              aria-label="View pending approvals"
            >
              <Bell className="w-5 h-5 text-slate-400 hover:text-white transition" />
              {pendingApprovalsCount > 0 && (
                <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 rounded-full text-white text-xs font-bold flex items-center justify-center">
                  {pendingApprovalsCount}
                </span>
              )}
            </button>

            {/* User Menu - Hidden text on mobile, show avatar only */}
            <div className="flex items-center gap-2 sm:gap-3 pl-2 sm:pl-4 border-l border-slate-700/50">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-white">John Doe</p>
                <p className="text-xs text-slate-400">Admin</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center text-white font-bold text-sm">
                JD
              </div>
            </div>
          </div>
        </header>

        {/* Skip to content link for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 bg-primary-600 text-white px-4 py-2 rounded-br z-50"
        >
          Skip to main content
        </a>

        {/* Page Content - Responsive padding */}
        <main id="main-content" className="p-4 sm:p-6 flex-1">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>

        {/* Bottom Footer */}
        <footer className="bg-gradient-to-r from-slate-900/50 to-slate-900/50 backdrop-blur-xl border-t border-slate-800/50 px-6 py-4 mt-auto" role="contentinfo">
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
