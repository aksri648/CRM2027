import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send } from 'lucide-react'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Campaign {
  id: number
  name: string
  subject: string | null
  channel: string
  status: string
  message_content: string | null
  segment_id: number | null
  target_count: number
  sent_count: number
  delivered_count: number
  opened_count: number
  clicked_count: number
  converted_count: number
  failed_count: number
  revenue: number
  sent_at: string | null
  created_at: string
}

export default function CampaignDetail() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const { id } = useParams()
  const navigate = useNavigate()
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    if (id) loadCampaign(parseInt(id))
  }, [id])

  const loadCampaign = async (campaignId: number) => {
    try {
      const response = await api.get(`/campaigns/${campaignId}`)
      setCampaign(response.data)
    } catch (error) {
      console.error('Failed to load campaign:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!campaign) return
    setSending(true)
    try {
      await api.post(`/campaigns/${campaign.id}/send`, {})
      alert('Campaign sending started!')
      loadCampaign(campaign.id)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to send campaign')
    } finally {
      setSending(false)
    }
  }

  if (loading) return <div>Loading...</div>
  if (!campaign) return <div>Campaign not found</div>

  const deliveryRate = campaign.sent_count > 0 ? (campaign.delivered_count / campaign.sent_count * 100).toFixed(1) : 0
  const openRate = campaign.delivered_count > 0 ? (campaign.opened_count / campaign.delivered_count * 100).toFixed(1) : 0
  const clickRate = campaign.opened_count > 0 ? (campaign.clicked_count / campaign.opened_count * 100).toFixed(1) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/campaigns')} className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
          <p className="text-gray-600">{campaign.channel} • {campaign.status}</p>
        </div>
        {campaign.status === 'draft' && (
          <button
            onClick={handleSend}
            disabled={sending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            <Send size={18} />
            {sending ? 'Sending...' : 'Send Campaign'}
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-100">
          <p className="text-sm text-gray-500">Sent</p>
          <p className="text-2xl font-bold text-gray-900">{campaign.sent_count}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100">
          <p className="text-sm text-gray-500">Delivered</p>
          <p className="text-2xl font-bold text-gray-900">{deliveryRate}%</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100">
          <p className="text-sm text-gray-500">Opened</p>
          <p className="text-2xl font-bold text-gray-900">{openRate}%</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100">
          <p className="text-sm text-gray-500">Clicked</p>
          <p className="text-2xl font-bold text-gray-900">{clickRate}%</p>
        </div>
      </div>

      {/* Message Content */}
      <div className="bg-white p-6 rounded-xl border border-gray-100">
        <h2 className="font-semibold text-gray-900 mb-4">Message Content</h2>
        <div className="bg-gray-50 p-4 rounded-lg">
          {campaign.subject && <p className="font-medium text-gray-900 mb-2">Subject: {campaign.subject}</p>}
          <p className="text-gray-700 whitespace-pre-wrap">{campaign.message_content || 'No content'}</p>
        </div>
      </div>
    </div>
  )
}