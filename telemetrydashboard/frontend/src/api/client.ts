const API_BASE = '/api/v1';

interface ServiceMetrics {
  service: string;
  url: string;
  status: string;
  health?: any;
  stats?: any;
  timestamp: string;
  error?: string;
}

interface MetricsResponse {
  timestamp: string;
  services: {
    app_service: ServiceMetrics;
    channel_service: ServiceMetrics;
  };
  summary: {
    total_services: number;
    healthy_count: number;
    unhealthy_count: number;
  };
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  service: string;
  metadata?: any;
}

interface LogsResponse {
  timestamp: string;
  logs: LogEntry[];
}

export const api = {
  async getMetrics(): Promise<MetricsResponse> {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    return res.json();
  },

  async getStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  async getLogs(service?: string, level?: string, limit = 100): Promise<LogsResponse> {
    let url = `${API_BASE}/logs?limit=${limit}`;
    if (service) url += `&service=${service}`;
    if (level) url += `&level=${level}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch logs');
    return res.json();
  },

  async getServiceLogs(service: string, limit = 100): Promise<LogsResponse> {
    const res = await fetch(`${API_BASE}/logs/services/${service}?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch service logs');
    return res.json();
  }
};