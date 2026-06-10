import { useState, useEffect, useMemo } from 'react'
import { RefreshCw, Activity, Package, Cog, Send, CheckCircle, Eye, MousePointer, DollarSign } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@clerk/clerk-react'
import { createApi } from '@/api/client'

interface PipelineStatus {
  active_campaigns: number
  queue_depth: number
  workers_processing: number
  total_sent: number
  total_delivered: number
  total_opened: number
  total_clicked: number
  total_converted: number
}

interface PipelineEvent {
  id: string
  timestamp: string
  event_type: string
  description: string
  status: 'event' | 'ok' | 'retry' | 'failed'
}

export default function PipelineMonitor() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApi(getToken), [getToken])

  const [status, setStatus] = useState<PipelineStatus | null>(null)
  const [events, setEvents] = useState<PipelineEvent[]>([])
  const [, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  useEffect(() => {
    loadPipelineData()
    const interval = setInterval(loadPipelineData, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadPipelineData = async () => {
    try {
      const [statusRes, eventsRes] = await Promise.all([
        api.get('/pipeline/status'),
        api.get('/pipeline/events')
      ])
      setStatus(statusRes.data)
      setEvents(eventsRes.data)
      setLastRefresh(new Date())
    } catch (error) {
      console.error('Failed to load pipeline data:', error)
      setStatus(null)
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (statusType: string) => {
    const styles = {
      event: 'bg-gray-100 text-gray-600',
      ok: 'bg-green-100 text-green-600',
      retry: 'bg-yellow-100 text-yellow-600',
      failed: 'bg-red-100 text-red-600'
    }
    return (
      <span className={`badge ${styles[statusType as keyof typeof styles] || styles.event}`}>
        {statusType.charAt(0).toUpperCase() + statusType.slice(1)}
      </span>
    )
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-IN').format(num)
  }

  const statCards = status ? [
    { icon: Activity, label: 'Campaign', value: status.active_campaigns, color: '#3b82f6' },
    { icon: Package, label: 'Queue', value: status.queue_depth, color: '#f59e0b' },
    { icon: Cog, label: 'Worker', value: status.workers_processing, color: '#8b5cf6' },
    { icon: Send, label: 'Sent', value: status.total_sent, color: '#3b82f6' },
    { icon: CheckCircle, label: 'Delivered', value: status.total_delivered, color: '#10b981' },
    { icon: Eye, label: 'Opened', value: status.total_opened, color: '#0fd4b4' },
    { icon: MousePointer, label: 'Clicked', value: status.total_clicked, color: '#f59e0b' },
    { icon: DollarSign, label: 'Converted', value: status.total_converted, color: '#10b981' }
  ] : []

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pipeline Monitor</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time communication lifecycle visualization</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">Last updated: {lastRefresh.toLocaleTimeString()}</span>
          <Button variant="outline" onClick={loadPipelineData}>
            <RefreshCw size={16} className="mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Pipeline Status Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {statCards.slice(0, 4).map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${stat.color}20` }}
                  >
                    <Icon size={20} style={{ color: stat.color }} />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">{stat.label}</div>
                    <div className="text-xl font-bold text-gray-900">{formatNumber(stat.value)}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Event Timeline */}
        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Event Timeline</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.map((event) => (
                <div key={event.id} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                  <div className="text-xs text-gray-400 w-20 flex-shrink-0">{event.timestamp}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 text-sm">{event.event_type}</span>
                      {getStatusBadge(event.status)}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">{event.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Queue Depth Panel */}
        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Queue Status</h3>
            
            <div className="text-center mb-6">
              <div className="text-5xl font-bold" style={{ color: 'var(--color-accent-teal)' }}>
                {status?.queue_depth || 0}
              </div>
              <div className="text-sm text-gray-500 mt-1">Messages in Queue</div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{status?.workers_processing || 0}</div>
                <div className="text-xs text-gray-500 mt-1">Processing</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {(status?.queue_depth || 0) - (status?.workers_processing || 0)}
                </div>
                <div className="text-xs text-gray-500 mt-1">Pending</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">0</div>
                <div className="text-xs text-gray-500 mt-1">Retry</div>
              </div>
            </div>

            {/* Additional Stats */}
            <div className="mt-6 pt-4 border-t border-gray-100">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-gray-500">Delivered</div>
                  <div className="text-lg font-bold text-gray-900">{formatNumber(status?.total_delivered || 0)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Opened</div>
                  <div className="text-lg font-bold text-gray-900">{formatNumber(status?.total_opened || 0)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Clicked</div>
                  <div className="text-lg font-bold text-gray-900">{formatNumber(status?.total_clicked || 0)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Converted</div>
                  <div className="text-lg font-bold text-gray-900">{formatNumber(status?.total_converted || 0)}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}