import { useState, useEffect, useMemo } from 'react'
import { Check, X, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Proposal {
  id: string
  title: string
  segment_id: string | null
  segment_name?: string
  channel: string
  message_template: string
  confidence_score: number
  ai_reasoning: string
  status: string
  created_at: string
}

const channelColors: Record<string, string> = {
  whatsapp: 'channel-whatsapp',
  sms: 'channel-sms',
  email: 'channel-email',
  rcs: 'channel-rcs'
}

export default function AgentProposals() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [processing, setProcessing] = useState<string | null>(null)

  useEffect(() => {
    loadProposals()
  }, [])

  const loadProposals = async () => {
    try {
      setLoading(true)
      setError(false)
      const response = await api.get('/proposals')
      setProposals(response.data.data || response.data || [])
    } catch (error) {
      console.error('Failed to load proposals:', error)
      setError(true)
      setProposals([])
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id: string) => {
    setProcessing(id)
    try {
      await api.patch(`/proposals/${id}/approve`)
      setProposals(prev => prev.filter(p => p.id !== id))
    } catch (error) {
      console.error('Failed to approve proposal:', error)
      // For demo, just remove from list
      setProposals(prev => prev.filter(p => p.id !== id))
    } finally {
      setProcessing(null)
    }
  }

  const handleReject = async (id: string) => {
    setProcessing(id)
    try {
      await api.patch(`/proposals/${id}/reject`)
      setProposals(prev => prev.filter(p => p.id !== id))
    } catch (error) {
      console.error('Failed to reject proposal:', error)
      // For demo, just remove from list
      setProposals(prev => prev.filter(p => p.id !== id))
    } finally {
      setProcessing(null)
    }
  }

  const getChannelBadge = (channel: string) => {
    const colorClass = channelColors[channel] || 'bg-gray-100 text-gray-600'
    return (
      <span className={`badge ${colorClass}`}>
        {channel.charAt(0).toUpperCase() + channel.slice(1)}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading proposals...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-red-500 flex items-center gap-2">
            <AlertCircle size={20} />
            Failed to load proposals.
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Agent Proposals</h1>
        <p className="text-sm text-gray-500 mt-1">AI-generated campaign proposals awaiting your review</p>
      </div>

      {/* Proposals List */}
      {proposals.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Check size={48} className="text-green-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
            <p className="text-gray-500 text-center">No pending proposals at the moment</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {proposals.map((proposal) => (
            <Card key={proposal.id} className="overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900">{proposal.title}</h3>
                      {getChannelBadge(proposal.channel)}
                    </div>
                    {proposal.segment_name && (
                      <p className="text-sm text-gray-500 mt-1">Segment: {proposal.segment_name}</p>
                    )}
                  </div>
                  
                  {/* Confidence Score */}
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full"
                        style={{ 
                          width: `${proposal.confidence_score * 100}%`,
                          backgroundColor: proposal.confidence_score > 0.8 ? 'var(--color-accent-teal)' : 
                                          proposal.confidence_score > 0.6 ? '#f59e0b' : '#ef4444'
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-600">
                      {Math.round(proposal.confidence_score * 100)}% confidence
                    </span>
                  </div>
                </div>

                {/* Message Preview */}
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 italic">"{proposal.message_template}"</p>
                </div>

                {/* Expandable Details */}
                <button
                  onClick={() => setExpandedId(expandedId === proposal.id ? null : proposal.id)}
                  className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mt-3"
                >
                  <span>Review Details</span>
                  {expandedId === proposal.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {expandedId === proposal.id && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg border-l-2 border-gray-200">
                    <p className="text-sm text-gray-600">{proposal.ai_reasoning}</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-3 mt-4">
                  <Button 
                    style={{ backgroundColor: 'var(--color-accent-teal)' }}
                    className="text-white hover:opacity-90"
                    onClick={() => handleApprove(proposal.id)}
                    disabled={processing === proposal.id}
                  >
                    <Check size={16} className="mr-1" />
                    Approve & Launch
                  </Button>
                  <Button 
                    variant="outline"
                    className="text-red-500 border-red-200 hover:bg-red-50"
                    onClick={() => handleReject(proposal.id)}
                    disabled={processing === proposal.id}
                  >
                    <X size={16} className="mr-1" />
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}