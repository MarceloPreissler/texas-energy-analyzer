import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface GridStatus {
  timestamp: string;
  current_demand_mw: number;
  total_capacity_mw: number;
  available_reserve_mw: number;
  reserve_margin_percent: number;
}

interface FuelMix {
  timestamp: string;
  wind_mw: number;
  solar_mw: number;
  natural_gas_mw: number;
  coal_mw: number;
  nuclear_mw: number;
  hydro_mw: number;
  storage_mw: number;
  other_mw: number;
  total_mw: number;
  renewable_percent: number;
}

interface ZonePrices {
  timestamp: string;
  lz_houston: number;
  lz_north: number;
  lz_south: number;
  lz_west: number;
  hub_houston: number;
  hub_north: number;
  hub_west: number;
  hub_average: number;
}

interface ErcotSummary {
  grid_status: GridStatus;
  fuel_mix: FuelMix;
  zone_prices: ZonePrices;
  last_updated: string;
  data_source: string;
}

const API_BASE_URL = 'https://web-production-665ac.up.railway.app';

// Fallback data based on typical ERCOT grid conditions
const getFallbackData = (): ErcotSummary => {
  const now = new Date().toISOString();
  return {
    grid_status: {
      timestamp: now,
      current_demand_mw: 45000,
      total_capacity_mw: 85000,
      available_reserve_mw: 40000,
      reserve_margin_percent: 47.1
    },
    fuel_mix: {
      timestamp: now,
      wind_mw: 18000,
      solar_mw: 8000,
      natural_gas_mw: 25000,
      coal_mw: 5000,
      nuclear_mw: 5000,
      hydro_mw: 200,
      storage_mw: 500,
      other_mw: 300,
      total_mw: 62000,
      renewable_percent: 42.3
    },
    zone_prices: {
      timestamp: now,
      lz_houston: 28.50,
      lz_north: 27.20,
      lz_south: 29.10,
      lz_west: 25.80,
      hub_houston: 28.00,
      hub_north: 26.80,
      hub_west: 25.50,
      hub_average: 26.77
    },
    last_updated: now,
    data_source: 'Typical ERCOT values (API temporarily unavailable)'
  };
};

const fetchErcotSummary = async (): Promise<ErcotSummary> => {
  try {
    // Try our backend API first
    const response = await fetch(`${API_BASE_URL}/ercot/summary`);
    if (response.ok) {
      return response.json();
    }
  } catch (e) {
    console.log('Backend ERCOT API unavailable, using fallback data');
  }

  // Return fallback data if API is unavailable
  return getFallbackData();
};

const formatNumber = (num: number): string => {
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return num.toFixed(0);
};

const formatMW = (mw: number): string => {
  if (mw >= 1000) {
    return `${(mw / 1000).toFixed(1)} GW`;
  }
  return `${mw.toFixed(0)} MW`;
};

const ErcotDashboard: React.FC = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['ercot-summary'],
    queryFn: fetchErcotSummary,
    refetchInterval: 300000, // Refetch every 5 minutes
    staleTime: 240000, // Consider data stale after 4 minutes
  });

  if (isLoading) {
    return (
      <div className="ercot-dashboard">
        <div className="ercot-loading">
          <div className="loading-spinner"></div>
          <p>Loading ERCOT Grid Data...</p>
        </div>
      </div>
    );
  }

  // With fallback data, we should always have data - but keep a minimal error handler just in case
  if (!data) {
    return (
      <div className="ercot-dashboard">
        <div className="ercot-error">
          <h3>Loading ERCOT Data...</h3>
          <button onClick={() => refetch()} className="retry-btn">Refresh</button>
        </div>
      </div>
    );
  }

  const { grid_status, fuel_mix, zone_prices } = data;

  // Calculate grid health indicator
  const getGridHealthStatus = () => {
    if (grid_status.reserve_margin_percent >= 20) return { status: 'Excellent', color: '#10b981', icon: '🟢' };
    if (grid_status.reserve_margin_percent >= 15) return { status: 'Good', color: '#22c55e', icon: '🟢' };
    if (grid_status.reserve_margin_percent >= 10) return { status: 'Moderate', color: '#eab308', icon: '🟡' };
    if (grid_status.reserve_margin_percent >= 5) return { status: 'Tight', color: '#f97316', icon: '🟠' };
    return { status: 'Critical', color: '#ef4444', icon: '🔴' };
  };

  const gridHealth = getGridHealthStatus();

  // Fuel mix chart data
  const fuelMixChartData = {
    labels: ['Natural Gas', 'Wind', 'Solar', 'Coal', 'Nuclear', 'Other'],
    datasets: [
      {
        data: [
          fuel_mix.natural_gas_mw,
          fuel_mix.wind_mw,
          fuel_mix.solar_mw,
          fuel_mix.coal_mw,
          fuel_mix.nuclear_mw,
          fuel_mix.hydro_mw + fuel_mix.other_mw + Math.max(0, fuel_mix.storage_mw),
        ],
        backgroundColor: [
          '#3b82f6', // Natural Gas - Blue
          '#22c55e', // Wind - Green
          '#facc15', // Solar - Yellow
          '#6b7280', // Coal - Gray
          '#a855f7', // Nuclear - Purple
          '#06b6d4', // Other - Cyan
        ],
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  };

  // Zone prices bar chart
  const zonePricesChartData = {
    labels: ['Houston', 'North', 'South', 'West'],
    datasets: [
      {
        label: 'Load Zone ($/MWh)',
        data: [zone_prices.lz_houston, zone_prices.lz_north, zone_prices.lz_south, zone_prices.lz_west],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderRadius: 6,
      },
      {
        label: 'Hub ($/MWh)',
        data: [zone_prices.hub_houston, zone_prices.hub_north, zone_prices.hub_average, zone_prices.hub_west],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderRadius: 6,
      },
    ],
  };

  const lastUpdated = new Date(data.last_updated).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });

  const isFallbackData = data.data_source.includes('temporarily unavailable');

  return (
    <div className="ercot-dashboard">
      <div className="ercot-header">
        <div className="ercot-title-section">
          <h2 className="ercot-title">
            <span className="ercot-logo">⚡</span>
            ERCOT Grid Status
          </h2>
          <p className="ercot-subtitle">
            {isFallbackData
              ? 'Typical grid values (live data temporarily unavailable)'
              : 'Live data from the Electric Reliability Council of Texas'}
          </p>
        </div>
        <div className="ercot-meta">
          <span className="last-updated">{isFallbackData ? 'Sample Data' : `Updated: ${lastUpdated}`}</span>
          <a
            href="https://www.ercot.com/gridmktinfo/dashboards"
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
          >
            View Live Data: ERCOT.com
          </a>
        </div>
      </div>

      {/* Grid Status Hero Section */}
      <div className="grid-status-hero">
        <div className="grid-health-indicator" style={{ borderColor: gridHealth.color }}>
          <span className="health-icon">{gridHealth.icon}</span>
          <span className="health-status" style={{ color: gridHealth.color }}>{gridHealth.status}</span>
          <span className="health-label">Grid Status</span>
        </div>

        <div className="grid-metrics">
          <div className="metric-card demand">
            <div className="metric-icon">📊</div>
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.current_demand_mw)}</div>
              <div className="metric-label">Current Demand</div>
            </div>
          </div>

          <div className="metric-card capacity">
            <div className="metric-icon">🏭</div>
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.total_capacity_mw)}</div>
              <div className="metric-label">Total Capacity</div>
            </div>
          </div>

          <div className="metric-card reserves">
            <div className="metric-icon">🔋</div>
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.available_reserve_mw)}</div>
              <div className="metric-label">Available Reserves</div>
            </div>
          </div>

          <div className="metric-card margin">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <div className="metric-value">{grid_status.reserve_margin_percent.toFixed(1)}%</div>
              <div className="metric-label">Reserve Margin</div>
            </div>
          </div>
        </div>
      </div>

      {/* Fuel Mix and Prices Section */}
      <div className="ercot-charts-row">
        <div className="ercot-card fuel-mix-card">
          <h3 className="card-title">
            <span className="title-icon">⚡</span>
            Generation Fuel Mix
          </h3>
          <div className="fuel-mix-content">
            <div className="fuel-chart-container">
              <Doughnut
                data={fuelMixChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  cutout: '65%',
                  plugins: {
                    legend: {
                      position: 'right',
                      labels: {
                        color: '#64748b',
                        padding: 12,
                        font: { size: 11 },
                        usePointStyle: true,
                        pointStyle: 'circle',
                      },
                    },
                    tooltip: {
                      callbacks: {
                        label: (context) => {
                          const value = context.parsed;
                          const total = fuel_mix.total_mw;
                          const percent = ((value / total) * 100).toFixed(1);
                          return `${context.label}: ${formatMW(value)} (${percent}%)`;
                        },
                      },
                    },
                  },
                }}
              />
            </div>
            <div className="fuel-stats">
              <div className="fuel-stat renewable">
                <span className="fuel-stat-value">{fuel_mix.renewable_percent.toFixed(1)}%</span>
                <span className="fuel-stat-label">Renewable</span>
              </div>
              <div className="fuel-stat total">
                <span className="fuel-stat-value">{formatMW(fuel_mix.total_mw)}</span>
                <span className="fuel-stat-label">Total Generation</span>
              </div>
            </div>
          </div>
          <div className="fuel-breakdown">
            <div className="fuel-item">
              <span className="fuel-dot" style={{ background: '#22c55e' }}></span>
              <span className="fuel-name">Wind</span>
              <span className="fuel-value">{formatMW(fuel_mix.wind_mw)}</span>
            </div>
            <div className="fuel-item">
              <span className="fuel-dot" style={{ background: '#facc15' }}></span>
              <span className="fuel-name">Solar</span>
              <span className="fuel-value">{formatMW(fuel_mix.solar_mw)}</span>
            </div>
            <div className="fuel-item">
              <span className="fuel-dot" style={{ background: '#3b82f6' }}></span>
              <span className="fuel-name">Natural Gas</span>
              <span className="fuel-value">{formatMW(fuel_mix.natural_gas_mw)}</span>
            </div>
            <div className="fuel-item">
              <span className="fuel-dot" style={{ background: '#a855f7' }}></span>
              <span className="fuel-name">Nuclear</span>
              <span className="fuel-value">{formatMW(fuel_mix.nuclear_mw)}</span>
            </div>
          </div>
        </div>

        <div className="ercot-card prices-card">
          <h3 className="card-title">
            <span className="title-icon">💰</span>
            Real-Time Wholesale Prices ($/MWh)
          </h3>
          <div className="prices-chart-container">
            <Bar
              data={zonePricesChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    position: 'top',
                    labels: { color: '#64748b', font: { size: 11 } },
                  },
                },
                scales: {
                  x: {
                    grid: { color: 'rgba(100, 116, 139, 0.1)' },
                    ticks: { color: '#64748b' },
                  },
                  y: {
                    grid: { display: false },
                    ticks: { color: '#64748b' },
                  },
                },
              }}
            />
          </div>
          <div className="price-summary">
            <div className="price-item">
              <span className="price-label">Hub Average</span>
              <span className="price-value">${zone_prices.hub_average.toFixed(2)}/MWh</span>
            </div>
            <div className="price-item">
              <span className="price-label">Retail Equivalent</span>
              <span className="price-value highlight">~{((zone_prices.hub_average / 10) + 3).toFixed(1)}¢/kWh</span>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="ercot-info-banner">
        <div className="info-icon">ℹ️</div>
        <div className="info-content">
          <strong>About ERCOT:</strong> The Electric Reliability Council of Texas manages the flow of electric
          power to more than 26 million Texas customers, representing about 90% of the state's electric load.
          Wholesale prices shown above reflect real-time market conditions and influence retail electricity rates.
        </div>
      </div>
    </div>
  );
};

export default ErcotDashboard;
