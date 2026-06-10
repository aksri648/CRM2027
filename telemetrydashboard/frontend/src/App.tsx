import { useState } from 'react';
import { Activity, Server, AlertCircle, CheckCircle, Clock, Filter } from 'lucide-react';
import { useMetrics, useLogs } from './hooks/useTelemetry';

type TabType = 'overview' | 'logs' | 'metrics';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [logServiceFilter, setLogServiceFilter] = useState<string>('');
  const [logLevelFilter, setLogLevelFilter] = useState<string>('');
  
  const { metrics, loading: metricsLoading, error: metricsError } = useMetrics(5000);
  const { logs, loading: logsLoading } = useLogs(logServiceFilter || undefined, 3000);

  const filteredLogs = logLevelFilter
    ? logs.filter(log => log.level === logLevelFilter)
    : logs;

  const getStatusIcon = (status: string) => {
    if (status === 'healthy') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'unreachable') return <AlertCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'bg-red-100 text-red-700';
      case 'warning': return 'bg-yellow-100 text-yellow-700';
      case 'info': return 'bg-blue-100 text-blue-700';
      case 'debug': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent/10 rounded-lg">
                <Activity className="w-6 h-6 text-accent" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Telemetry Dashboard</h1>
                <p className="text-sm text-gray-500">Real-time observability for Xeno AI CRM</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Last updated:</span>
              <span className="text-sm font-medium text-gray-700">
                {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-1">
            {(['overview', 'logs', 'metrics'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-accent text-accent'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Status Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Overall Status</p>
                    <p className={`text-2xl font-bold mt-1 ${
                      metrics?.summary?.healthy_count === 2 ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {metrics?.summary?.healthy_count === 2 ? 'Healthy' : 'Degraded'}
                    </p>
                  </div>
                  {metrics?.summary?.healthy_count === 2 ? (
                    <CheckCircle className="w-10 h-10 text-green-500" />
                  ) : (
                    <AlertCircle className="w-10 h-10 text-yellow-500" />
                  )}
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Services Online</p>
                    <p className="text-2xl font-bold mt-1 text-gray-900">
                      {metrics?.summary?.healthy_count || 0}/{metrics?.summary?.total_services || 0}
                    </p>
                  </div>
                  <Server className="w-10 h-10 text-accent" />
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Recent Logs</p>
                    <p className="text-2xl font-bold mt-1 text-gray-900">{logs.length}</p>
                  </div>
                  <Clock className="w-10 h-10 text-purple-500" />
                </div>
              </div>
            </div>

            {/* Service Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* App Service */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-gray-400" />
                    <h3 className="font-semibold text-gray-900">App Service</h3>
                  </div>
                  {getStatusIcon(metrics?.services?.app_service?.status || 'unknown')}
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">URL</span>
                      <span className="font-mono text-gray-700">{metrics?.services?.app_service?.url || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Status</span>
                      <span className={`font-medium ${
                        metrics?.services?.app_service?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metrics?.services?.app_service?.status || 'unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Last Check</span>
                      <span className="text-gray-700">
                        {metrics?.services?.app_service?.timestamp
                          ? new Date(metrics.services.app_service.timestamp).toLocaleTimeString()
                          : 'N/A'}
                      </span>
                    </div>
                    {metrics?.services?.app_service?.error && (
                      <div className="mt-3 p-3 bg-red-50 rounded-lg">
                        <p className="text-sm text-red-700">{metrics.services.app_service.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Channel Service */}
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-gray-400" />
                    <h3 className="font-semibold text-gray-900">Channel Service</h3>
                  </div>
                  {getStatusIcon(metrics?.services?.channel_service?.status || 'unknown')}
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">URL</span>
                      <span className="font-mono text-gray-700">{metrics?.services?.channel_service?.url || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Status</span>
                      <span className={`font-medium ${
                        metrics?.services?.channel_service?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {metrics?.services?.channel_service?.status || 'unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Last Check</span>
                      <span className="text-gray-700">
                        {metrics?.services?.channel_service?.timestamp
                          ? new Date(metrics.services.channel_service.timestamp).toLocaleTimeString()
                          : 'N/A'}
                      </span>
                    </div>
                    {metrics?.services?.channel_service?.stats && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-500 mb-2">Stats</p>
                        <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(metrics.services.channel_service.stats, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-4">
                <Filter className="w-5 h-5 text-gray-400" />
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-500">Service:</label>
                  <select
                    value={logServiceFilter}
                    onChange={(e) => setLogServiceFilter(e.target.value)}
                    className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                  >
                    <option value="">All Services</option>
                    <option value="app_service">App Service</option>
                    <option value="channel_service">Channel Service</option>
                    <option value="telemetry_dashboard">Telemetry Dashboard</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-500">Level:</label>
                  <select
                    value={logLevelFilter}
                    onChange={(e) => setLogLevelFilter(e.target.value)}
                    className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent/50"
                  >
                    <option value="">All Levels</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="debug">Debug</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Logs List */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {logsLoading ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-12 text-center text-gray-500">Loading logs...</td>
                      </tr>
                    ) : filteredLogs.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-12 text-center text-gray-500">No logs found</td>
                      </tr>
                    ) : (
                      filteredLogs.map((log, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded ${getLogLevelColor(log.level)}`}>
                              {log.level.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-700">{log.service}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{log.message}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h3>
              {metricsLoading ? (
                <p className="text-gray-500">Loading metrics...</p>
              ) : metricsError ? (
                <p className="text-red-500">{metricsError}</p>
              ) : (
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                  {JSON.stringify(metrics, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;