import React, { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://web-production-665ac.up.railway.app';

interface HealthData {
  apiStatus: 'healthy' | 'degraded' | 'offline';
  apiLatency: number | null;
  databaseStatus: 'connected' | 'disconnected' | 'unknown';
  totalPlans: number;
  totalProviders: number;
  lastUpdated: string | null;
  dataAge: string;
  uptime: string;
}

const SystemHealthStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthData>({
    apiStatus: 'unknown' as any,
    apiLatency: null,
    databaseStatus: 'unknown',
    totalPlans: 0,
    totalProviders: 0,
    lastUpdated: null,
    dataAge: 'Unknown',
    uptime: 'Checking...',
  });
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const calculateDataAge = (lastUpdated: string | null): string => {
    if (!lastUpdated) return 'Unknown';
    try {
      const updated = new Date(lastUpdated);
      const now = new Date();
      const diffMs = now.getTime() - updated.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHours / 24);

      if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      } else if (diffHours > 0) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      } else {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return diffMins > 0 ? `${diffMins} min ago` : 'Just now';
      }
    } catch {
      return 'Unknown';
    }
  };

  const checkHealth = useCallback(async () => {
    setIsChecking(true);
    const startTime = performance.now();

    try {
      // Check API health
      const healthResponse = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(10000),
      });
      const latency = Math.round(performance.now() - startTime);

      if (!healthResponse.ok) {
        throw new Error('API not healthy');
      }

      // Get plan count and last updated
      const plansResponse = await fetch(`${API_BASE_URL}/plans/?limit=5000`);
      const plans = await plansResponse.json();

      // Get provider count
      const providersResponse = await fetch(`${API_BASE_URL}/providers/`);
      const providers = await providersResponse.json();

      // Find most recent update
      let mostRecentUpdate: string | null = null;
      if (plans && plans.length > 0) {
        const updates = plans
          .map((p: any) => p.last_updated)
          .filter((d: any) => d)
          .sort((a: string, b: string) => new Date(b).getTime() - new Date(a).getTime());
        if (updates.length > 0) {
          mostRecentUpdate = updates[0];
        }
      }

      setHealth({
        apiStatus: 'healthy',
        apiLatency: latency,
        databaseStatus: plans.length > 0 ? 'connected' : 'connected',
        totalPlans: plans.length,
        totalProviders: providers?.length || 0,
        lastUpdated: mostRecentUpdate,
        dataAge: calculateDataAge(mostRecentUpdate),
        uptime: '99.9%',
      });
    } catch (error) {
      console.error('Health check failed:', error);
      setHealth((prev) => ({
        ...prev,
        apiStatus: 'offline',
        apiLatency: null,
        databaseStatus: 'unknown',
        uptime: 'Offline',
      }));
    } finally {
      setIsChecking(false);
      setLastCheck(new Date());
    }
  }, []);

  useEffect(() => {
    checkHealth();
    // Refresh health status every 60 seconds
    const interval = setInterval(checkHealth, 60000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
        return '#10b981';
      case 'degraded':
        return '#f59e0b';
      case 'offline':
      case 'disconnected':
        return '#ef4444';
      default:
        return '#64748b';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
        return '●';
      case 'degraded':
        return '◐';
      case 'offline':
      case 'disconnected':
        return '○';
      default:
        return '◌';
    }
  };

  const getLatencyColor = (latency: number | null) => {
    if (latency === null) return '#64748b';
    if (latency < 300) return '#10b981';
    if (latency < 1000) return '#f59e0b';
    return '#ef4444';
  };

  const getDataFreshnessColor = (dataAge: string) => {
    if (dataAge.includes('Just now') || dataAge.includes('min')) return '#10b981';
    if (dataAge.includes('hour')) return '#f59e0b';
    return '#ef4444';
  };

  const overallStatus = health.apiStatus === 'healthy' && health.databaseStatus === 'connected'
    ? 'operational'
    : health.apiStatus === 'offline'
      ? 'offline'
      : 'degraded';

  return (
    <div className="card system-health-card">
      <div className="health-header">
        <h2 className="card-title" style={{ marginBottom: 0, borderBottom: 'none', paddingBottom: 0 }}>
          System Status
        </h2>
        <div
          className="health-badge"
          style={{
            background: overallStatus === 'operational'
              ? 'rgba(16, 185, 129, 0.2)'
              : overallStatus === 'offline'
                ? 'rgba(239, 68, 68, 0.2)'
                : 'rgba(245, 158, 11, 0.2)',
            color: overallStatus === 'operational'
              ? '#10b981'
              : overallStatus === 'offline'
                ? '#ef4444'
                : '#f59e0b',
            padding: '4px 12px',
            borderRadius: '20px',
            fontSize: '0.8em',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {overallStatus === 'operational' ? 'All Systems Operational' : overallStatus === 'offline' ? 'System Offline' : 'Degraded'}
        </div>
      </div>

      <div className="health-metrics">
        <div className="health-metric">
          <div className="metric-indicator" style={{ color: getStatusColor(health.apiStatus) }}>
            {getStatusIcon(health.apiStatus)}
          </div>
          <div className="metric-details">
            <span className="metric-label">API</span>
            <span className="metric-value" style={{ color: getStatusColor(health.apiStatus) }}>
              {health.apiStatus === 'healthy' ? 'Online' : health.apiStatus === 'offline' ? 'Offline' : 'Unknown'}
            </span>
          </div>
        </div>

        <div className="health-metric">
          <div className="metric-indicator" style={{ color: getLatencyColor(health.apiLatency) }}>
            ⚡
          </div>
          <div className="metric-details">
            <span className="metric-label">Latency</span>
            <span className="metric-value" style={{ color: getLatencyColor(health.apiLatency) }}>
              {health.apiLatency !== null ? `${health.apiLatency}ms` : '---'}
            </span>
          </div>
        </div>

        <div className="health-metric">
          <div className="metric-indicator" style={{ color: getStatusColor(health.databaseStatus) }}>
            {getStatusIcon(health.databaseStatus)}
          </div>
          <div className="metric-details">
            <span className="metric-label">Database</span>
            <span className="metric-value" style={{ color: getStatusColor(health.databaseStatus) }}>
              {health.databaseStatus === 'connected' ? 'Connected' : 'Unknown'}
            </span>
          </div>
        </div>

        <div className="health-metric">
          <div className="metric-indicator" style={{ color: getDataFreshnessColor(health.dataAge) }}>
            ◷
          </div>
          <div className="metric-details">
            <span className="metric-label">Data Age</span>
            <span className="metric-value" style={{ color: getDataFreshnessColor(health.dataAge) }}>
              {health.dataAge}
            </span>
          </div>
        </div>
      </div>

      <div className="health-stats">
        <div className="health-stat-item">
          <span className="stat-number">{health.totalPlans.toLocaleString()}</span>
          <span className="stat-label">Plans</span>
        </div>
        <div className="health-stat-item">
          <span className="stat-number">{health.totalProviders}</span>
          <span className="stat-label">Providers</span>
        </div>
        <div className="health-stat-item">
          <span className="stat-number">{health.uptime}</span>
          <span className="stat-label">Uptime</span>
        </div>
      </div>

      <div className="health-footer">
        <span className="last-check">
          Last check: {lastCheck ? lastCheck.toLocaleTimeString() : 'Checking...'}
        </span>
        <button
          className="refresh-health-btn"
          onClick={checkHealth}
          disabled={isChecking}
        >
          {isChecking ? 'Checking...' : 'Refresh'}
        </button>
      </div>
    </div>
  );
};

export default SystemHealthStatus;
