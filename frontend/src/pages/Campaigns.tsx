import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Mail, MessageSquare, Share2, Send, CheckCircle, Clock, XCircle } from 'lucide-react'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface Campaign {
  id: number
  name: string
  channel: string
  status: string
  sent_count: number
  delivered_count: number
  opened_count: number
  clicked_count: number
  sent_at: string | null
  created_at: string
}

const channelConfig: Record<string, { icon: any; color: string; bg: string }> = {
  email: { icon: Mail, color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200' },
  sms: { icon: MessageSquare, color: 'text-purple-600', bg: 'bg-purple-50 border-purple-200' },
  whatsapp: { icon: Share2, color: 'text-green-600', bg: 'bg-green-50 border-green-200' },
  rcs: { icon: Share2, color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200' },
}

const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
  draft: { icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100 text-gray-700' },
  scheduled: { icon: Clock, color: 'text-blue-600', bg: 'bg-blue-100 text-blue-700' },
  sending: { icon: Send, color: 'text-amber-600', bg: 'bg-amber-100 text-amber-700' },
  sent: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100 text-green-700' },
  completed: { icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-100 text-emerald-700' },
  failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100 text-red-700' },
}

export default function Campaigns() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCampaigns()
  }, [])

  const loadCampaigns = async () => {
    try {
      const response = await api.get('/campaigns')
      setCampaigns(response.data.data || [])
    } catch (error) {
      console.error('Failed to load campaigns:', error)
    } finally {
      setLoading(false)
    }
  }

  const getChannelIcon = (channel: string) => {
    const config = channelConfig[channel] || channelConfig.email
    const Icon = config.icon
    return <Icon className={`w-5 h-5 ${config.color}`} />
  }

  const getStatusBadge = (status: string) => {
    const config = statusConfig[status] || statusConfig.draft
    const Icon = config.icon
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${config.bg}`}>
        <Icon className="w-3 h-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const getDeliveryRate = (campaign: Campaign) => {
    if (!campaign.sent_count) return 0
    return Math.round((campaign.delivered_count / campaign.sent_count) * 100)
  }

  const getOpenRate = (campaign: Campaign) => {
    if (!campaign.delivered_count) return 0
    return Math.round((campaign.opened_count / campaign.delivered_count) * 100)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-sm text-gray-500 mt-1">Create and manage your marketing campaigns</p>
        </div>
        <Link
          to="/campaigns/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#0fd4b4] text-white rounded-lg font-medium text-sm hover:bg-[#0bbfa1] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Create Campaign
        </Link>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-50 rounded-lg">
              <Send className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{campaigns.length}</p>
              <p className="text-xs text-gray-500">Total Campaigns</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-green-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {campaigns.filter(c => c.status === 'completed' || c.status === 'sent').length}
              </p>
              <p className="text-xs text-gray-500">Completed</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-amber-50 rounded-lg">
              <Clock className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {campaigns.filter(c => c.status === 'scheduled' || c.status === 'sending').length}
              </p>
              <p className="text-xs text-gray-500">In Progress</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-purple-50 rounded-lg">
              <Share2 className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {campaigns.reduce((sum, c) => sum + (c.sent_count || 0), 0).toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">Total Sent</p>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign List */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-4 border-[#0fd4b4] border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-500">Loading campaigns...</p>
            </div>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 px-4">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Send className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">No campaigns yet</h3>
            <p className="text-sm text-gray-500 mb-4">Create your first campaign to start engaging with your audience</p>
            <Link
              to="/campaigns/new"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#0fd4b4] text-white rounded-lg font-medium text-sm hover:bg-[#0bbfa1] transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Campaign
            </Link>
          </div>
        ) : (
          campaigns.map((campaign) => {
            const channel = channelConfig[campaign.channel] || channelConfig.email
            return (
              <Link
                key={campaign.id}
                to={`/campaigns/${campaign.id}`}
                className="block bg-white rounded-xl border border-gray-200 p-5 hover:border-[#0fd4b4] hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${channel.bg}`}>
                      {getChannelIcon(campaign.channel)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{campaign.name}</h3>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-500 capitalize">{campaign.channel}</span>
                        <span className="w-1 h-1 bg-gray-300 rounded-full" />
                        {getStatusBadge(campaign.status)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <p className="text-lg font-bold text-gray-900">{campaign.sent_count || 0}</p>
                      <p className="text-xs text-gray-500">Sent</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-gray-900">{getDeliveryRate(campaign)}%</p>
                      <p className="text-xs text-gray-500">Delivery</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-gray-900">{getOpenRate(campaign)}%</p>
                      <p className="text-xs text-gray-500">Open Rate</p>
                    </div>
                    <div className="text-center">
                      <p className="text-lg font-bold text-[#0fd4b4]">{campaign.clicked_count || 0}</p>
                      <p className="text-xs text-gray-500">Clicks</p>
                    </div>
                  </div>
                </div>
              </Link>
            )
          })
        )}
      </div>
    </div>
  )
}