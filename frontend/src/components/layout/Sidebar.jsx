import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  ListBulletIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

const navItems = [
  { to: '/', label: '대시보드', icon: HomeIcon },
  { to: '/receipts', label: '지출 내역', icon: ListBulletIcon },
  { to: '/stats', label: '통계 분석', icon: ChartBarIcon },
]

export default function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white">
      <div className="flex h-16 items-center px-6 border-b border-gray-200">
        <span className="text-base font-bold text-indigo-600">Receipt AI</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
