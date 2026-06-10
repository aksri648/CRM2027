import { useState, useEffect, useMemo } from 'react'
import { Lightbulb, Sparkles, ChevronDown, ChevronUp, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Opportunity {
  id: string
  title: string
  description: string
  audience_description: string
  expected_revenue: number
  ai_reasoning: string
  status: string
  created_at: string
}

export default function Opportunities() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [dismissing, setDismissing] = useState<string | null>(null)

  useEffect(() => {
    loadOpportunities()
  }, [])

  const loadOpportunities = async () => {
    try {
      const response = await api.get('/opportunities')
      setOpportunities(response.data.data || response.data || [])
    } catch (error) {
      console.error('Failed to load opportunities:', error)
      setOpportunities([])
    } finally {
      setLoading(false)
    }
  }

  const handleDismiss = async (id: string) => {
    setDismissing(id)
    setTimeout(() => {
      setOpportunities(prev => prev.filter(o => o.id !== id))
      setDismissing(null)
    }, 300)
  }

  const handleGenerateCampaign = async (opportunity: Opportunity) => {
    try {
      await api.post(`/opportunities/${opportunity.id}/generate-campaign`)
      window.location.href = '/proposals'
    } catch (error) {
      console.error('Failed to generate campaign:', error)
    }
  }

  const handleScanOpportunities = async () => {
    try {
      await api.post('/opportunities/scan')
      loadOpportunities()
    } catch (error) {
      console.error('Failed to scan opportunities:', error)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Opportunities</h1>
          <p className="text-sm text-gray-500 mt-1">AI-discovered marketing opportunities for your business</p>
        </div>
        <Button variant="outline" onClick={handleScanOpportunities}>
          <Sparkles size={16} className="mr-2" />
          Scan for Opportunities
        </Button>
      </div>

      {/* Opportunities List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading opportunities...</div>
        </div>
      ) : opportunities.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Lightbulb size={48} className="text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No opportunities found</h3>
            <p className="text-gray-500 text-center">Click "Scan for Opportunities" to discover new marketing opportunities</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {opportunities.map((opportunity) => (
            <Card 
              key={opportunity.id}
              className={`transition-all duration-300 ${dismissing === opportunity.id ? 'opacity-0 transform scale-95' : ''}`}
            >
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
                    <Lightbulb size={20} className="text-yellow-600" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">{opportunity.title}</h3>
                        <p className="text-sm text-gray-500 mt-1">{opportunity.description}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6 mt-4">
                      <div>
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Audience</span>
                        <p className="text-sm font-medium text-gray-900">{opportunity.audience_description}</p>
                      </div>
                      <div>
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Expected Revenue</span>
                        <p className="text-sm font-bold" style={{ color: 'var(--color-accent-teal)' }}>
                          {formatCurrency(opportunity.expected_revenue)}
                        </p>
                      </div>
                    </div>

                    {/* AI Reasoning - Collapsible */}
                    <div className="mt-4 border-t border-gray-100 pt-4">
                      <button
                        onClick={() => setExpandedId(expandedId === opportunity.id ? null : opportunity.id)}
                        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
                      >
                        <span>🔺 AI Reasoning</span>
                        {expandedId === opportunity.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </button>
                      
                      {expandedId === opportunity.id && (
                        <p className="text-sm text-gray-600 mt-2 pl-4 border-l-2 border-gray-200">
                          {opportunity.ai_reasoning || 'No reasoning available.'}
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 mt-4">
                      <Button 
                        style={{ backgroundColor: 'var(--color-accent-teal)' }}
                        className="text-white hover:opacity-90"
                        onClick={() => handleGenerateCampaign(opportunity)}
                      >
                        Generate Campaign
                      </Button>
                      <Button variant="outline" onClick={() => window.location.href = '/proposals'}>
                        Review Proposal
                      </Button>
                      <Button 
                        variant="ghost" 
                        className="text-gray-400 hover:text-gray-600"
                        onClick={() => handleDismiss(opportunity.id)}
                      >
                        <X size={16} className="mr-1" />
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}