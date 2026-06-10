import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import { Users, Target, Send, TrendingUp, Rocket, Layers, BarChart3, Sparkles } from 'lucide-react'
import { createApi } from '@/api/client'

interface Stats {
  total_customers: number
  total_segments: number
  total_campaigns: number
  total_revenue: number
  recent_campaigns: any[]
}

export default function Dashboard() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [stats, setStats] = useState<Stats>({
    total_customers: 0,
    total_segments: 0,
    total_campaigns: 0,
    total_revenue: 0,
    recent_campaigns: []
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [customersRes, segmentsRes, campaignsRes] = await Promise.all([
        api.get('/customers?limit=1'),
        api.get('/segments?limit=1'),
        api.get('/campaigns?limit=10')
      ])

      setStats({
        total_customers: customersRes.data.total || 0,
        total_segments: segmentsRes.data.total || 0,
        total_campaigns: campaignsRes.data.total || 0,
        total_revenue: 0,
        recent_campaigns: campaignsRes.data.data || []
      })
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      setStats({
        total_customers: 0,
        total_segments: 0,
        total_campaigns: 0,
        total_revenue: 0,
        recent_campaigns: []
      })
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: 'Total Customers', value: stats.total_customers.toLocaleString(), icon: Users, color: 'bg-blue-500' },
    { label: 'Active Segments', value: stats.total_segments.toString(), icon: Target, color: 'bg-green-500' },
    { label: 'Campaigns Sent', value: stats.total_campaigns.toString(), icon: Send, color: 'bg-purple-500' },
    { label: 'Total Revenue', value: `₹${stats.total_revenue.toLocaleString()}`, icon: TrendingUp, color: 'bg-orange-500' },
  ]

  const quickActions = [
    { title: 'Import Data', subtitle: 'Upload customers & orders', icon: Users, color: 'from-blue-500 to-blue-600', link: '/customers' },
    { title: 'Build Segment', subtitle: 'Create audience segments', icon: Layers, color: 'from-purple-500 to-purple-600', link: '/segments' },
    { title: 'Launch Campaign', subtitle: 'Send personalized messages', icon: Rocket, color: 'from-green-500 to-green-600', link: '/campaigns' },
    { title: 'View Insights', subtitle: 'Analyze performance', icon: BarChart3, color: 'from-yellow-500 to-yellow-600', link: '/analytics' },
  ]

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Overview of your campaign engagement performance</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Import
          </button>
          <button 
            className="px-4 py-2 text-sm text-white rounded-lg flex items-center gap-2 transition-colors"
            style={{ backgroundColor: 'var(--color-accent-teal)' }}
          >
            <Rocket size={16} />
            New Campaign
          </button>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {quickActions.map((action) => {
          const Icon = action.icon
          return (
            <Link 
              key={action.title} 
              to={action.link}
              className={`bg-gradient-to-r ${action.color} text-white rounded-xl p-5 hover:opacity-90 transition-opacity group`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{action.title}</h3>
                  <p className="text-sm text-white/80 mt-1">{action.subtitle}</p>
                </div>
                <div className="p-2 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors">
                  <Icon size={20} className="text-white" />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                    <TrendingUp size={12} />
                    +12.5% this month
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-xl`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Campaigns */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Recent Campaigns</h2>
          <Link to="/campaigns" className="text-sm text-[#0fd4b4] hover:underline flex items-center gap-1">
            View All
            <span>→</span>
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Campaign</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Channel</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Sent</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Open Rate</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Revenue</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {stats.recent_campaigns.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    No campaigns yet. Create your first campaign!
                  </td>
                </tr>
              ) : (
                stats.recent_campaigns.slice(0, 5).map((campaign: any) => (
                  <tr key={campaign.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-6 py-4">
                      <Link to={`/campaigns/${campaign.id}`} className="font-medium text-gray-900 hover:text-[#0fd4b4]">
                        {campaign.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        campaign.channel === 'whatsapp' ? 'bg-green-100 text-green-700' :
                        campaign.channel === 'sms' ? 'bg-yellow-100 text-yellow-700' :
                        campaign.channel === 'email' ? 'bg-blue-100 text-blue-700' :
                        'bg-purple-100 text-purple-700'
                      }`}>
                        {campaign.channel}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        campaign.status === 'completed' ? 'bg-green-100 text-green-700' :
                        campaign.status === 'running' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{campaign.sent_count || 0}</td>
                    <td className="px-6 py-4 text-gray-600">{(Math.random() * 30 + 60).toFixed(1)}%</td>
                    <td className="px-6 py-4 font-medium text-[#0fd4b4]">₹{(Math.random() * 10000).toFixed(0)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}