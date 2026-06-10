import { useState, useEffect, useMemo } from 'react'
import { Plus, Sparkles, Layers, Users } from 'lucide-react'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Segment {
  id: number
  name: string
  description: string | null
  customer_count: number
  is_active: boolean
  created_at: string
  created_by?: string
}

export default function Segments() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [segments, setSegments] = useState<Segment[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'ai' | 'manual'>('ai')

  useEffect(() => {
    loadSegments()
  }, [])

  const loadSegments = async () => {
    try {
      const response = await api.get('/segments')
      setSegments(response.data.data || [])
    } catch (error) {
      console.error('Failed to load segments:', error)
      setSegments([])
    } finally {
      setLoading(false)
    }
  }

  const aiSegments = segments.filter(s => s.created_by === 'agent')
  const manualSegments = segments.filter(s => s.created_by === 'human')

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Segments</h1>
          <p className="text-sm text-gray-500 mt-1">Build and manage audience segments</p>
        </div>
        <div className="flex gap-3">
          <button 
            className="px-4 py-2 text-sm text-white rounded-lg flex items-center gap-2 transition-colors"
            style={{ backgroundColor: 'var(--color-accent-teal)' }}
          >
            <Sparkles size={16} />
            AI Segment Builder
          </button>
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors">
            <Plus size={16} />
            Create Segment
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('ai')}
          className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
            activeTab === 'ai' 
              ? 'text-[#0fd4b4]' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          AI-Suggested
          {activeTab === 'ai' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0fd4b4]" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('manual')}
          className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
            activeTab === 'manual' 
              ? 'text-[#0fd4b4]' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Manual Segments
          {activeTab === 'manual' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0fd4b4]" />
          )}
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0fd4b4]"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(activeTab === 'ai' ? aiSegments : manualSegments).map((segment) => (
            <div 
              key={segment.id} 
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#0fd4b4]/10 rounded-lg">
                    <Layers size={20} className="text-[#0fd4b4]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-[#0fd4b4] transition-colors">
                      {segment.name}
                    </h3>
                    {segment.created_by === 'agent' && (
                      <span className="text-xs text-[#0fd4b4] flex items-center gap-1 mt-0.5">
                        <Sparkles size={10} />
                        AI Powered
                      </span>
                    )}
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  segment.is_active 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {segment.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                {segment.description || 'No description'}
              </p>
              
              <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-500">
                  <Users size={16} />
                  <span className="text-sm">{segment.customer_count.toLocaleString()} customers</span>
                </div>
                <button className="text-sm text-[#0fd4b4] hover:underline">
                  Use →
                </button>
              </div>
            </div>
          ))}
          
          {((activeTab === 'ai' ? aiSegments : manualSegments).length === 0) && (
            <div className="col-span-full text-center py-12">
              <Layers size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No segments found</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}