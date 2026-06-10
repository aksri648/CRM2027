import { useState, useEffect } from 'react'
import { Search, Plus, Download, Upload, ChevronLeft, ChevronRight } from 'lucide-react'
import api from '../api/client'

interface Customer {
  id: number
  email: string | null
  phone: string | null
  first_name: string | null
  last_name: string | null
  city: string | null
  state: string | null
  engagement_score: number
  created_at: string
}

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadCustomers()
  }, [page, search])

  const loadCustomers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/customers', {
        params: { skip: page * 50, limit: 50, search: search || undefined }
      })
      setCustomers(response.data.data || [])
      setTotal(response.data.total || 0)
    } catch (error) {
      console.error('Failed to load customers:', error)
      setCustomers([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const getEngagementColor = (score: number) => {
    if (score > 70) return 'bg-green-100 text-green-700'
    if (score > 40) return 'bg-yellow-100 text-yellow-700'
    return 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-sm text-gray-500 mt-1">{total.toLocaleString()} total customers</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors">
            <Upload size={16} />
            Import
          </button>
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors">
            <Download size={16} />
            Export
          </button>
          <button 
            className="px-4 py-2 text-sm text-white rounded-lg flex items-center gap-2 transition-colors"
            style={{ backgroundColor: 'var(--color-accent-teal)' }}
          >
            <Plus size={16} />
            Add Customer
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search by name, email, or phone..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0fd4b4] focus:border-transparent transition-all"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Phone</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Engagement</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0fd4b4]"></div>
                    </div>
                  </td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No customers found
                  </td>
                </tr>
              ) : (
                customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-medium" style={{ backgroundColor: 'var(--color-accent-teal)' }}>
                          {customer.first_name?.[0]}{customer.last_name?.[0]}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{customer.first_name} {customer.last_name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{customer.email || '-'}</td>
                    <td className="px-6 py-4 text-gray-600">{customer.phone || '-'}</td>
                    <td className="px-6 py-4 text-gray-600">
                      {[customer.city, customer.state].filter(Boolean).join(', ') || '-'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEngagementColor(customer.engagement_score)}`}>
                        {customer.engagement_score}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {new Date(customer.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {total > 50 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Showing {page * 50 + 1} to {Math.min((page + 1) * 50, total)} of {total.toLocaleString()} customers
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={20} />
            </button>
            <span className="px-4 py-2 text-sm text-gray-600">
              Page {page + 1}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={(page + 1) * 50 >= total}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}