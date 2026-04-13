import { Link } from 'react-router-dom'
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline'

export default function Navbar() {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 shadow-sm">
      <h1 className="text-lg font-semibold text-gray-800">AI 영수증 지출 관리</h1>
      <Link
        to="/upload"
        className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
      >
        <ArrowUpTrayIcon className="h-4 w-4" />
        영수증 업로드
      </Link>
    </header>
  )
}
