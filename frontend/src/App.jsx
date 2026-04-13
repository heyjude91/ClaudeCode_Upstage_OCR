import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import UploadPage from './pages/UploadPage'
import ReceiptList from './pages/ReceiptList'
import ReceiptDetail from './pages/ReceiptDetail'
import StatsPage from './pages/StatsPage'
import Sidebar from './components/layout/Sidebar'
import Navbar from './components/layout/Navbar'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50 font-sans">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto px-6 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/receipts" element={<ReceiptList />} />
              <Route path="/receipts/:id" element={<ReceiptDetail />} />
              <Route path="/stats" element={<StatsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
