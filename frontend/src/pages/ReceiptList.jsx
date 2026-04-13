import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getReceipts } from '../api/receiptApi'
import { getCategories } from '../api/categoryApi'

const CATEGORY_COLORS = {
  '식료품': 'bg-indigo-100 text-indigo-700',
  '외식':   'bg-orange-100 text-orange-700',
  '쇼핑':   'bg-pink-100 text-pink-700',
  '교통':   'bg-teal-100 text-teal-700',
  '의료':   'bg-red-100 text-red-700',
  '문화/여가': 'bg-purple-100 text-purple-700',
  '기타':   'bg-gray-100 text-gray-600',
}

export default function ReceiptList() {
  const [receipts, setReceipts] = useState([])
  const [meta, setMeta]         = useState({ page: 1, total: 0, total_pages: 1 })
  const [categories, setCategories] = useState([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const [filters, setFilters] = useState({
    store_name: '',
    category:   '',
    date_from:  '',
    date_to:    '',
    page:       1,
    limit:      20,
  })

  // 카테고리 목록 로딩
  useEffect(() => {
    getCategories().then(r => setCategories(r.data)).catch(() => {})
  }, [])

  // 목록 조회
  const fetchList = useCallback(async (params) => {
    setLoading(true)
    setError(null)
    try {
      const clean = Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== '' && v !== null)
      )
      const res = await getReceipts(clean)
      setReceipts(res.data.data)
      setMeta(res.data.meta)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchList(filters) }, [filters, fetchList])

  const handleFilter = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value, page: 1 }))
  }

  const handleReset = () => {
    setFilters({ store_name: '', category: '', date_from: '', date_to: '', page: 1, limit: 20 })
  }

  const handlePage = (p) => setFilters(prev => ({ ...prev, page: p }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">지출 내역</h2>
        <span className="text-sm text-gray-500">총 {meta.total}건</span>
      </div>

      {/* ── 필터 바 ── */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {/* 가게명 검색 */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">가게명</label>
            <input
              type="text"
              name="store_name"
              value={filters.store_name}
              onChange={handleFilter}
              placeholder="가게명 검색..."
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* 카테고리 */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">카테고리</label>
            <select
              name="category"
              value={filters.category}
              onChange={handleFilter}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">전체</option>
              {categories.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* 시작일 */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">시작일</label>
            <input
              type="date"
              name="date_from"
              value={filters.date_from}
              onChange={handleFilter}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* 종료일 */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">종료일</label>
            <input
              type="date"
              name="date_to"
              value={filters.date_to}
              onChange={handleFilter}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="mt-3 flex justify-end">
          <button
            onClick={handleReset}
            className="rounded-lg border border-gray-300 px-4 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
          >
            필터 초기화
          </button>
        </div>
      </div>

      {/* ── 테이블 ── */}
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
        {loading && (
          <div className="flex items-center justify-center py-16 text-gray-400 text-sm">
            불러오는 중...
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center py-16 text-red-500 text-sm">
            오류: {error}
          </div>
        )}

        {!loading && !error && receipts.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <p className="text-sm">조건에 맞는 지출 내역이 없습니다.</p>
          </div>
        )}

        {!loading && !error && receipts.length > 0 && (
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-500">날짜</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">가게명</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">카테고리</th>
                <th className="px-4 py-3 text-right font-medium text-gray-500">금액</th>
                <th className="px-4 py-3 text-center font-medium text-gray-500">상세</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {receipts.map(r => (
                <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-600">{r.date}</td>
                  <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate">{r.store_name}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${CATEGORY_COLORS[r.category] ?? 'bg-gray-100 text-gray-600'}`}>
                      {r.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-gray-900">
                    {r.total_amount.toLocaleString()}원
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Link
                      to={`/receipts/${r.id}`}
                      className="text-indigo-600 hover:underline text-xs"
                    >
                      보기
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── 페이지네이션 ── */}
      {meta.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            disabled={meta.page <= 1}
            onClick={() => handlePage(meta.page - 1)}
            className="rounded-lg border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-gray-50"
          >
            이전
          </button>
          <span className="text-sm text-gray-600">
            {meta.page} / {meta.total_pages}
          </span>
          <button
            disabled={meta.page >= meta.total_pages}
            onClick={() => handlePage(meta.page + 1)}
            className="rounded-lg border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-gray-50"
          >
            다음
          </button>
        </div>
      )}
    </div>
  )
}
