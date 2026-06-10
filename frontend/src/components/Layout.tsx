import { Outlet, Link, useLocation } from 'react-router-dom'
import { useUser } from '@clerk/clerk-react'
import {
  LayoutDashboard,
  Sparkles,
  Lightbulb,
  FileText,
  Users,
  Layers,
  Send,
  FlaskConical,
  BarChart3,
  Activity,
  Bot,
  Settings,
  LogOut,
  LucideIcon
} from 'lucide-react'

interface NavItem {
  path: string
  label: string
  icon: LucideIcon
  badge?: string | number
  badgeType?: 'new' | 'count' | 'live'
  isModal?: boolean
}

const mainNav: NavItem[] = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/ai-studio', label: 'AI Campaign Studio', icon: Sparkles, badge: 'New', badgeType: 'new' },
  { path: '/opportunities', label: 'Opportunities', icon: Lightbulb },
  { path: '/proposals', label: 'Agent Proposals', icon: FileText },
]

const audienceNav: NavItem[] = [
  { path: '/customers', label: 'Customers', icon: Users },
  { path: '/segments', label: 'Segments', icon: Layers },
]

const engageNav: NavItem[] = [
  { path: '/campaigns', label: 'Campaigns', icon: Send },
  { path: '/ab-tests', label: 'A/B Tests', icon: FlaskConical },
]

const analyzeNav: NavItem[] = [
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/pipeline', label: 'Pipeline Monitor', icon: Activity },
]

const systemNav: NavItem[] = [
  { path: '/ai-command', label: 'AI Command Centre', icon: Bot, badge: 'Live', badgeType: 'live', isModal: true },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
  const { user } = useUser()
  const location = useLocation()

  const handleLogout = () => {
    // App uses Clerk for authentication, no localStorage token to clear
    window.location.href = '/login'
  }

  const handleOpenAICommandCentre = () => {
    window.dispatchEvent(new CustomEvent('open-ai-command-centre'))
  }

  const renderNavItem = (item: NavItem) => {
    const Icon = item.icon
    const isActive = location.pathname === item.path
    
    const content = (
      <button
        className={`sidebar-item w-full ${isActive ? 'active' : ''}`}
        onClick={item.isModal ? handleOpenAICommandCentre : undefined}
      >
        <Icon size={18} />
        <span className="flex-1 text-left">{item.label}</span>
        {item.badge && (
          <span className={`badge ${
            item.badgeType === 'new' ? 'badge-new' : 
            item.badgeType === 'live' ? 'badge-live' : 
            'bg-gray-600 text-white'
          }`}>
            {item.badge}
          </span>
        )}
      </button>
    )

    if (item.isModal) {
      return <div key={item.path}>{content}</div>
    }

    return (
      <Link key={item.path} to={item.path}>
        {content}
      </Link>
    )
  }

  const renderNavSection = (title: string, items: NavItem[]) => (
    <div className="mb-6">
      <div className="px-4 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
        {title}
      </div>
      <div className="space-y-1">
        {items.map(renderNavItem)}
      </div>
    </div>
  )

  return (
    <div className="flex min-h-screen" style={{ backgroundColor: 'var(--color-main-bg)' }}>
      {/* Sidebar */}
      <aside 
        className="w-[260px] min-h-screen flex flex-col border-r"
        style={{ backgroundColor: 'var(--color-sidebar-bg)' }}
      >
        {/* Logo */}
        <div className="p-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--color-accent-teal)' }}>
              <span className="text-white font-bold text-lg">X</span>
            </div>
            <span className="text-white font-bold text-lg">Xeno AI</span>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          {renderNavSection('MAIN', mainNav)}
          {renderNavSection('AUDIENCE', audienceNav)}
          {renderNavSection('ENGAGE', engageNav)}
          {renderNavSection('ANALYZE', analyzeNav)}
          {renderNavSection('SYSTEM', systemNav)}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-medium" style={{ backgroundColor: 'var(--color-accent-teal)' }}>
              {user?.firstName?.charAt(0) || user?.emailAddresses?.[0]?.emailAddress?.charAt(0) || 'U'}
            </div>
            <div className="flex-1">
              <div className="text-white text-sm font-medium">{user?.fullName || 'User'}</div>
              <div className="text-gray-400 text-xs">{user?.primaryEmailAddress?.emailAddress || ''}</div>
            </div>
            <button
              onClick={handleLogout}
              className="text-gray-400 hover:text-white transition-colors"
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}