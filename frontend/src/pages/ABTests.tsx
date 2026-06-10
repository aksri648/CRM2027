import { useState, useEffect } from 'react'
import { Sparkles, Trophy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import api from '@/api/client'

interface ABTest {
  id: string
  name: string
  status: string
  winner_campaign_id: string | null
  campaign_a: {
    id: string
    name: string
    message: string
    channel: string
    stats: {
      sent: number
      open_rate: number
      ctr: number
      conversion: number
      revenue: number
    }
  }
  campaign_b: {
    id: string
    name: string
    message: string
    channel: string
    stats: {
      sent: number
      open_rate: number
      ctr: number
      conversion: number
      revenue: number
    }
  }
  created_at: string
}

const channelColors: Record<string, string> = {
  whatsapp: 'channel-whatsapp',
  sms: 'channel-sms',
  email: 'channel-email',
  rcs: 'channel-rcs'
}

export default function ABTests() {
  const [tests, setTests] = useState<ABTest[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTests()
  }, [])

  const loadTests = async () => {
    try {
      const response = await api.get('/ab-tests')
      setTests(response.data)
    } catch (error) {
      console.error('Failed to load A/B tests:', error)
      setTests([])
    } finally {
      setLoading(false)
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

  const getStatusBadge = (status: string) => {
    const statusClass = status === 'completed' ? 'status-completed' : 
                        status === 'running' ? 'status-running' : 'status-draft'
    return <span className={`badge ${statusClass}`}>{status}</span>
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  }

  const renderVariantPanel = (variant: ABTest['campaign_a'] | ABTest['campaign_b'], isWinner: boolean, label: string) => (
    <div className={`flex-1 p-4 rounded-lg border-2 ${isWinner ? 'border-[#0fd4b4]' : 'border-gray-200'}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-gray-900">{label}</span>
          {getChannelBadge(variant.channel)}
        </div>
        {isWinner && (
          <span className="badge badge-teal flex items-center gap-1">
            <Trophy size={12} />
            WINNER
          </span>
        )}
      </div>
      
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{variant.message}</p>
      
      <div className="grid grid-cols-4 gap-3">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{variant.stats.open_rate.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Open Rate</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{variant.stats.ctr.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">CTR</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{variant.stats.conversion.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Conversion</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{formatCurrency(variant.stats.revenue)}</div>
          <div className="text-xs text-gray-500">Revenue</div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">A/B Tests</h1>
          <p className="text-sm text-gray-500 mt-1">Design and analyze campaign experiments</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Sparkles size={16} className="mr-2" />
            AI Generate Test
          </Button>
          <Button style={{ backgroundColor: 'var(--color-accent-teal)' }} className="text-white">
            Create Manual Test
          </Button>
        </div>
      </div>

      {/* Tests List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Loading A/B tests...</div>
        </div>
      ) : tests.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Sparkles size={48} className="text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No A/B tests yet</h3>
            <p className="text-gray-500 text-center">Create your first A/B test to optimize campaign performance</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {tests.map((test) => (
            <Card key={test.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-gray-900">{test.name}</h3>
                    {getStatusBadge(test.status)}
                  </div>
                </div>

                <div className="flex gap-4">
                  {renderVariantPanel(
                    test.campaign_a, 
                    test.winner_campaign_id === test.campaign_a.id, 
                    `A - ${test.campaign_a.name}`
                  )}
                  {renderVariantPanel(
                    test.campaign_b, 
                    test.winner_campaign_id === test.campaign_b.id, 
                    `B - ${test.campaign_b.name}`
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}