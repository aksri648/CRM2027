import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

interface ServiceMetrics {
  service: string;
  url: string;
  status: string;
  health?: any;
  stats?: any;
  timestamp: string;
  error?: string;
}

interface MetricsData {
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

export function useMetrics(refreshInterval = 5000) {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      const data = await api.getMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  return { metrics, loading, error, refetch: fetchMetrics };
}

export function useLogs(service?: string, refreshInterval = 5000) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const data = service 
        ? await api.getServiceLogs(service)
        : await api.getLogs();
      setLogs(data.logs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  }, [service]);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchLogs, refreshInterval]);

  return { logs, loading, error, refetch: fetchLogs };
}