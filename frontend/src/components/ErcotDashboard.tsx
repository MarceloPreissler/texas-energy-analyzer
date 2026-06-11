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
import SystemHealthStatus from './SystemHealthStatus';

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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://texas-energy-backend.onrender.com';

const fetchErcotSummary = async (): Promise<ErcotSummary> => {
  const now = new Date().toISOString();

  // Try our backend API first
  try {
    const response = await fetch(`${API_BASE_URL}/ercot/summary`);
    if (response.ok) {
      const data = await response.json();
      if (data.grid_status?.current_demand_mw > 0) {
        return data;
      }
    }
  } catch (e) {
    console.log('Backend ERCOT API unavailable');
  }

  // Throw error - we'll show market stats fallback in the component
  throw new Error('ERCOT API unavailable');
};

// Fetch market stats from our plans database
const fetchMarketStats = async () => {
  try {
    // Fetch plans and providers in parallel
    const [plansResponse, providersResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/plans/?limit=5000`),
      fetch(`${API_BASE_URL}/plans/providers`)
    ]);

    if (plansResponse.ok) {
      const plans = await plansResponse.json();
      const providersData = providersResponse.ok ? await providersResponse.json() : [];

      // Create provider lookup map
      const providerMap: Record<number, string> = {};
      providersData.forEach((p: any) => {
        providerMap[p.id] = p.name;
      });

      // Calculate real statistics from our database
      const plansWithRates = plans.filter((p: any) => p.rate_1000_cents && p.rate_1000_cents > 0);
      if (plansWithRates.length === 0) return null;

      const rates = plansWithRates.map((p: any) => p.rate_1000_cents);
      const avgRate = rates.reduce((a: number, b: number) => a + b, 0) / rates.length;
      const minRate = Math.min(...rates);
      const maxRate = Math.max(...rates);

      // Find best plan (lowest rate)
      const bestPlan = plansWithRates.reduce((best: any, plan: any) => {
        if (!best || plan.rate_1000_cents < best.rate_1000_cents) return plan;
        return best;
      }, null);

      // Count by service type
      const residential = plansWithRates.filter((p: any) => p.service_type === 'Residential').length;
      const commercial = plansWithRates.filter((p: any) => p.service_type === 'Commercial').length;

      // Count renewable plans
      const renewablePlans = plansWithRates.filter((p: any) => (p.renewable_percent || 0) >= 50).length;
      const renewablePercent = (renewablePlans / plansWithRates.length) * 100;

      // Provider count - filter out null/undefined provider_ids
      const providerIds = plansWithRates
        .map((p: any) => p.provider_id)
        .filter((id: any) => id != null && id !== undefined);
      const providers = new Set(providerIds).size;

      return {
        totalPlans: plansWithRates.length,
        avgRate: avgRate.toFixed(2),
        minRate: minRate.toFixed(2),
        maxRate: maxRate.toFixed(2),
        residential,
        commercial,
        renewablePercent: renewablePercent.toFixed(1),
        providers,
        bestPlan: bestPlan ? {
          planName: bestPlan.plan_name,
          providerName: providerMap[bestPlan.provider_id] || 'Unknown',
          rate: bestPlan.rate_1000_cents,
          contractMonths: bestPlan.contract_months,
        } : null,
        lastUpdated: new Date().toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          timeZoneName: 'short',
        }),
      };
    }
  } catch (e) {
    console.log('Failed to fetch market stats');
  }
  return null;
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
    refetchInterval: 300000,
    staleTime: 240000,
    retry: 1,
  });

  const { data: marketStats } = useQuery({
    queryKey: ['market-stats'],
    queryFn: fetchMarketStats,
    staleTime: 60000,
  });

  // Show Texas Market Stats when ERCOT is unavailable
  if (error || !data) {
    if (isLoading) {
      return (
        <div className="ercot-dashboard">
          <div className="ercot-loading">
            <div className="loading-spinner"></div>
            <p>Loading Grid Data...</p>
          </div>
        </div>
      );
    }

    // Show market stats from our database
    return (
      <div className="ercot-dashboard">
        <div className="ercot-header">
          <div className="ercot-title-section">
            <h2 className="ercot-title">Texas Electricity Market</h2>
            <p className="ercot-subtitle">
              Real-time market statistics from our plans database
            </p>
          </div>
          <div className="ercot-meta">
            <span className="last-updated">Updated: {marketStats?.lastUpdated || 'Just now'}</span>
            <a
              href="https://www.ercot.com/gridmktinfo/dashboards"
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
            >
              View ERCOT Grid: ercot.com
            </a>
          </div>
        </div>

        {marketStats ? (
          <>
            {/* Top Row: System Status and Best Plan */}
            <div className="top-cards-row">
              <SystemHealthStatus />

              <div className="card best-plan-card">
                <h2 className="card-title">Best Plan</h2>
                {marketStats.bestPlan ? (
                  <>
                    <div className="summary-stat">
                      <div>Provider</div>
                      <strong>{marketStats.bestPlan.providerName}</strong>
                    </div>
                    <div className="summary-stat">
                      <div>Plan</div>
                      <strong style={{ fontSize: '1em' }}>{marketStats.bestPlan.planName}</strong>
                    </div>
                    <div className="summary-stat">
                      <div>Rate</div>
                      <strong>{marketStats.bestPlan.rate.toFixed(1)}¢/kWh</strong>
                    </div>
                    {marketStats.bestPlan.contractMonths && (
                      <div className="summary-stat">
                        <div>Term</div>
                        <strong>{marketStats.bestPlan.contractMonths} months</strong>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="summary-stat">
                    <div style={{ color: '#94a3b8' }}>No plans with rate data available</div>
                  </div>
                )}
              </div>
            </div>

            <div className="ercot-charts-row">
              <div className="ercot-card fuel-mix-card">
                <div className="analyzer-header">
                  <h3 className="card-title">Analyzer Breakdown</h3>
                  <div className="analyzer-stats-right">
                    <div className="analyzer-stat">
                      <span className="analyzer-stat-value green">{marketStats.renewablePercent}%</span>
                      <span className="analyzer-stat-label">Green Plans</span>
                    </div>
                    <div className="analyzer-stat">
                      <span className="analyzer-stat-value">{marketStats.totalPlans}</span>
                      <span className="analyzer-stat-label">Total Plans</span>
                    </div>
                  </div>
                </div>
                <div className="mckinsey-chart-container">
                  <div className="mckinsey-pie-wrapper">
                    <Doughnut
                      data={{
                        labels: ['Residential', 'Commercial'],
                        datasets: [{
                          data: [marketStats.residential, marketStats.commercial],
                          backgroundColor: ['#3B82F6', '#10B981'],
                          borderColor: 'rgba(3, 8, 6, 0.97)',
                          borderWidth: 3,
                          hoverBorderWidth: 0,
                          hoverOffset: 4,
                        }],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '0%',
                        plugins: {
                          legend: {
                            display: false,
                          },
                          tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 12, weight: 600 },
                            bodyFont: { size: 11 },
                            padding: 10,
                            cornerRadius: 6,
                          },
                        },
                      }}
                    />
                  </div>
                  <div className="mckinsey-legend">
                    <div className="mckinsey-legend-item">
                      <div className="mckinsey-legend-color" style={{ background: '#3B82F6' }}></div>
                      <div className="mckinsey-legend-text">
                        <span className="mckinsey-legend-label">Residential</span>
                        <span className="mckinsey-legend-value">{marketStats.residential} plans</span>
                        <span className="mckinsey-legend-percent">
                          {marketStats.totalPlans > 0
                            ? Math.round((marketStats.residential / marketStats.totalPlans) * 100)
                            : 0}%
                        </span>
                      </div>
                    </div>
                    <div className="mckinsey-legend-item">
                      <div className="mckinsey-legend-color" style={{ background: '#10B981' }}></div>
                      <div className="mckinsey-legend-text">
                        <span className="mckinsey-legend-label">Commercial</span>
                        <span className="mckinsey-legend-value">{marketStats.commercial} plans</span>
                        <span className="mckinsey-legend-percent">
                          {marketStats.totalPlans > 0
                            ? Math.round((marketStats.commercial / marketStats.totalPlans) * 100)
                            : 0}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="ercot-card prices-card">
                <h3 className="card-title">Rate Range (¢/kWh at 1000 kWh)</h3>
                <div className="prices-chart-container">
                  <Bar
                    data={{
                      labels: ['Lowest', 'Average', 'Highest'],
                      datasets: [{
                        label: 'Rate (¢/kWh)',
                        data: [
                          parseFloat(marketStats.minRate),
                          parseFloat(marketStats.avgRate),
                          parseFloat(marketStats.maxRate)
                        ],
                        backgroundColor: ['#4ade80', '#60a5fa', '#fb923c'],
                        borderRadius: 6,
                      }],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false },
                      },
                      scales: {
                        x: {
                          grid: { display: false },
                          ticks: { color: '#ffffff' },
                        },
                        y: {
                          grid: { color: 'rgba(255, 255, 255, 0.1)' },
                          ticks: { color: '#ffffff' },
                        },
                      },
                    }}
                  />
                </div>
                <div className="price-summary">
                  <div className="price-item">
                    <span className="price-label">Rate Spread</span>
                    <span className="price-value">{(parseFloat(marketStats.maxRate) - parseFloat(marketStats.minRate)).toFixed(1)}¢</span>
                  </div>
                  <div className="price-item">
                    <span className="price-label">Best Value</span>
                    <span className="price-value highlight">{marketStats.minRate}¢/kWh</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="ercot-info-banner">
              <div className="info-content">
                <strong>About This Data:</strong> These statistics are calculated from {marketStats.totalPlans} real electricity plans
                currently available in the Texas deregulated market. Rates shown are at 1,000 kWh usage level.
                For live ERCOT grid conditions, visit ercot.com.
              </div>
            </div>
          </>
        ) : (
          <div className="ercot-error">
            <h3>Loading Market Data...</h3>
            <button onClick={() => refetch()} className="retry-btn">Refresh</button>
          </div>
        )}
      </div>
    );
  }

  const { grid_status, fuel_mix, zone_prices } = data;

  const getGridHealthStatus = () => {
    if (grid_status.reserve_margin_percent >= 20) return { status: 'Excellent', color: '#10b981', icon: '●' };
    if (grid_status.reserve_margin_percent >= 15) return { status: 'Good', color: '#22c55e', icon: '●' };
    if (grid_status.reserve_margin_percent >= 10) return { status: 'Moderate', color: '#eab308', icon: '●' };
    if (grid_status.reserve_margin_percent >= 5) return { status: 'Tight', color: '#f97316', icon: '●' };
    return { status: 'Critical', color: '#ef4444', icon: '●' };
  };

  const gridHealth = getGridHealthStatus();

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
          '#3b82f6',
          '#22c55e',
          '#facc15',
          '#6b7280',
          '#a855f7',
          '#06b6d4',
        ],
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  };

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

  return (
    <div className="ercot-dashboard">
      <div className="ercot-header">
        <div className="ercot-title-section">
          <h2 className="ercot-title">ERCOT Grid Status</h2>
          <p className="ercot-subtitle">
            Live data from the Electric Reliability Council of Texas
          </p>
        </div>
        <div className="ercot-meta">
          <span className="last-updated">Updated: {lastUpdated}</span>
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

      <div className="grid-status-hero">
        <div className="grid-health-indicator" style={{ borderColor: gridHealth.color }}>
          <span className="health-icon">{gridHealth.icon}</span>
          <span className="health-status" style={{ color: gridHealth.color }}>{gridHealth.status}</span>
          <span className="health-label">Grid Status</span>
        </div>

        <div className="grid-metrics">
          <div className="metric-card demand">
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.current_demand_mw)}</div>
              <div className="metric-label">Current Demand</div>
            </div>
          </div>

          <div className="metric-card capacity">
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.total_capacity_mw)}</div>
              <div className="metric-label">Total Capacity</div>
            </div>
          </div>

          <div className="metric-card reserves">
            <div className="metric-content">
              <div className="metric-value">{formatMW(grid_status.available_reserve_mw)}</div>
              <div className="metric-label">Available Reserves</div>
            </div>
          </div>

          <div className="metric-card margin">
            <div className="metric-content">
              <div className="metric-value">{grid_status.reserve_margin_percent.toFixed(1)}%</div>
              <div className="metric-label">Reserve Margin</div>
            </div>
          </div>
        </div>
      </div>

      <div className="ercot-charts-row">
        <div className="ercot-card fuel-mix-card">
          <h3 className="card-title">Generation Fuel Mix</h3>
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
                        color: '#ffffff',
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
          <h3 className="card-title">Real-Time Wholesale Prices ($/MWh)</h3>
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
                    labels: { color: '#ffffff', font: { size: 11 } },
                  },
                },
                scales: {
                  x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#ffffff' },
                  },
                  y: {
                    grid: { display: false },
                    ticks: { color: '#ffffff' },
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

      <div className="ercot-info-banner">
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
