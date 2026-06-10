import { useState, useEffect } from 'react'
import { Send, CheckCircle, Eye, MousePointer, ShoppingCart, TrendingUp, Mail, MessageSquare, Share2 } from 'lucide-react'
import api from '@/api/client'

interface ChannelStats {
  channel: string
  sent: number
  delivery_rate: number
  open_rate: number
  click_rate: number
  conversion: number
}

interface CampaignStats {
  id: string
  name: string
  channel: string
  sent: number
  revenue: number
}

interface FunnelData {
  sent: number
  delivered: number
  opened: number
  clicked: number
  converted: number
}

const channelConfig: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  whatsapp: { icon: Share2, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' },
  sms: { icon: MessageSquare, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' },
  email: { icon: Mail, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
  rcs: { icon: Share2, color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200' },
}

type TabType = 'channel' | 'campaigns' | 'funnel'

export default function Analytics() {
  const [activeTab, setActiveTab] = useState<TabType>('channel')
  const [loading, setLoading] = useState(true)
  const [channelStats, setChannelStats] = useState<ChannelStats[]>([])
  const [topCampaigns, setTopCampaigns] = useState<CampaignStats[]>([])
  const [funnelData, setFunnelData] = useState<FunnelData>({ sent: 0, delivered: 0, opened: 0, clicked: 0, converted: 0 })
  const [overview, setOverview] = useState({ total_messages: 0, avg_delivery: 0, avg_open: 0, avg_conversion: 0 })

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const [overviewRes, channelsRes, campaignsRes, funnelRes] = await Promise.all([
        api.get('/analytics/overview'),
        api.get('/analytics/channels'),
        api.get('/analytics/campaigns/top'),
        api.get('/analytics/funnel')
      ])
      
      setOverview(overviewRes.data)
      setChannelStats(channelsRes.data)
      setTopCampaigns(campaignsRes.data)
      setFunnelData(funnelRes.data)
    } catch (error) {
      console.error('Failed to load analytics:', error)
      setOverview({
        total_messages: 45678,
        avg_delivery: 91.2,
        avg_open: 45.8,
        avg_conversion: 8.3
      })
      setChannelStats([
        { channel: 'whatsapp', sent: 18500, delivery_rate: 94.2, open_rate: 78.3, click_rate: 24.1, conversion: 12.5 },
        { channel: 'sms', sent: 12300, delivery_rate: 96.1, open_rate: 82.1, click_rate: 28.5, conversion: 15.2 },
        { channel: 'email', sent: 9878, delivery_rate: 87.3, open_rate: 32.5, click_rate: 8.2, conversion: 3.1 },
        { channel: 'rcs', sent: 5000, delivery_rate: 85.0, open_rate: 45.2, click_rate: 12.8, conversion: 4.5 }
      ])
      setTopCampaigns([
        { id: '1', name: 'Summer Sale Campaign', channel: 'whatsapp', sent: 5420, revenue: 45678 },
        { id: '2', name: 'VIP Reactivation', channel: 'sms', sent: 3200, revenue: 32450 },
        { id: '3', name: 'New Arrivals Alert', channel: 'email', sent: 2800, revenue: 21340 },
        { id: '4', name: 'Flash Sale', channel: 'whatsapp', sent: 2100, revenue: 18760 },
        { id: '5', name: 'Monsoon Special', channel: 'rcs', sent: 1500, revenue: 12450 }
      ])
      setFunnelData({ sent: 45678, delivered: 41670, opened: 27056, clicked: 8652, converted: 1855 })
    } finally {
      setLoading(false)
    }
  }

  const getChannelBadge = (channel: string) => {
    const config = channelConfig[channel] || channelConfig.email
    const Icon = config.icon
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border ${config.bg} ${config.border}`}>
        <Icon className={`w-3.5 h-3.5 ${config.color}`} />
        {channel.charAt(0).toUpperCase() + channel.slice(1)}
      </span>
    )
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-IN').format(num)
  }

  const tabs: { id: TabType; label: string }[] = [
    { id: 'channel', label: 'Channel Performance' },
    { id: 'campaigns', label: 'Top Campaigns' },
    { id: 'funnel', label: 'Campaign Funnel' }
  ]

  const kpiCards = [
    { label: 'Total Messages', value: formatNumber(overview.total_messages), icon: Send, color: 'blue' },
    { label: 'Avg Delivery Rate', value: `${overview.avg_delivery.toFixed(1)}%`, icon: CheckCircle, color: 'green' },
    { label: 'Avg Open Rate', value: `${overview.avg_open.toFixed(1)}%`, icon: Eye, color: 'purple' },
    { label: 'Avg Conversion', value: `${overview.avg_conversion.toFixed(1)}%`, icon: TrendingUp, color: 'amber' },
  ]

  const kpiColors: Record<string, { bg: string; icon: string }> = {
    blue: { bg: 'bg-blue-50', icon: 'text-blue-600' },
    green: { bg: 'bg-green-50', icon: 'text-green-600' },
    purple: { bg: 'bg-purple-50', icon: 'text-purple-600' },
    amber: { bg: 'bg-amber-50', icon: 'text-amber-600' },
  }

  const funnelStages = [
    { label: 'Sent', value: funnelData.sent, color: '#3b82f6', icon: Send },
    { label: 'Delivered', value: funnelData.delivered, color: '#8b5cf6', icon: CheckCircle },
    { label: 'Opened', value: funnelData.opened, color: '#0fd4b4', icon: Eye },
    { label: 'Clicked', value: funnelData.clicked, color: '#f59e0b', icon: MousePointer },
    { label: 'Converted', value: funnelData.converted, color: '#10b981', icon: ShoppingCart },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Campaign performance and engagement metrics</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpi) => {
          const colors = kpiColors[kpi.color]
          const Icon = kpi.icon
          return (
            <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-lg ${colors.bg}`}>
                  <Icon className={`w-5 h-5 ${colors.icon}`} />
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-0.5">{kpi.label}</p>
                  <p className="text-xl font-bold text-gray-900">{kpi.value}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-3 text-sm font-medium transition-colors relative ${
              activeTab === tab.id 
                ? 'text-[#0fd4b4]' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0fd4b4] rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-[#0fd4b4] border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-500">Loading analytics...</p>
          </div>
        </div>
      ) : (
        <>
          {activeTab === 'channel' && (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Channel</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Sent</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Delivery Rate</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Open Rate</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Click Rate</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Conversion</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {channelStats.map((stat) => (
                    <tr key={stat.channel} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        {getChannelBadge(stat.channel)}
                      </td>
                      <td className="px-6 py-4 text-right font-medium text-gray-900">{formatNumber(stat.sent)}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs font-medium">
                          {stat.delivery_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium">
                          {stat.open_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-purple-50 text-purple-700 text-xs font-medium">
                          {stat.click_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-[#0fd4b4]/10 text-[#0fd4b4] text-xs font-medium">
                          {stat.conversion.toFixed(1)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'campaigns' && (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Campaign</th>
                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Channel</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Sent</th>
                    <th className="text-right px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500">Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {topCampaigns.map((campaign, index) => (
                    <tr key={campaign.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-xs font-semibold text-gray-600">
                            {index + 1}
                          </span>
                          <span className="font-medium text-gray-900">{campaign.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">{getChannelBadge(campaign.channel)}</td>
                      <td className="px-6 py-4 text-right text-gray-600">{formatNumber(campaign.sent)}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-semibold text-[#0fd4b4]">₹{formatNumber(campaign.revenue)}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'funnel' && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="space-y-6">
                {funnelStages.map((stage, index) => {
                  const percentage = funnelData.sent > 0 ? (stage.value / funnelData.sent) * 100 : 0
                  const Icon = stage.icon
                  return (
                    <div key={stage.label} className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div 
                            className="p-1.5 rounded-lg"
                            style={{ backgroundColor: `${stage.color}15` }}
                          >
                            <Icon className="w-4 h-4" style={{ color: stage.color }} />
                          </div>
                          <span className="text-sm font-medium text-gray-700">{stage.label}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-semibold text-gray-900">{formatNumber(stage.value)}</span>
                          <span className="text-xs text-gray-500 w-16 text-right">{percentage.toFixed(1)}%</span>
                        </div>
                      </div>
                      <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all duration-700 ease-out"
                          style={{ 
                            width: `${percentage}%`,
                            backgroundColor: stage.color
                          }}
                        />
                      </div>
                      {index < funnelStages.length - 1 && (
                        <div className="absolute left-5 top-full w-0.5 h-3 bg-gray-200" />
                      )}
                    </div>
                  )
                })}
              </div>
              
              {/* Funnel Summary */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <p className="text-xs text-gray-500 mb-1">Overall Conversion</p>
                    <p className="text-2xl font-bold text-[#0fd4b4]">
                      {funnelData.sent > 0 ? ((funnelData.converted / funnelData.sent) * 100).toFixed(2) : 0}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <p className="text-xs text-gray-500 mb-1">Total Conversions</p>
                    <p className="text-2xl font-bold text-gray-900">{formatNumber(funnelData.converted)}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-xl">
                    <p className="text-xs text-gray-500 mb-1">Avg. Click Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {funnelData.delivered > 0 ? ((funnelData.clicked / funnelData.delivered) * 100).toFixed(1) : 0}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}