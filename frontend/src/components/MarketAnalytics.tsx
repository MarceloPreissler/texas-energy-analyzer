import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  service_type?: string | null;
  zip_code?: string | null;
  contract_months?: number | null;
  rate_1000_cents?: number | null;
  renewable_percent?: number | null;
  special_features?: string | null;
}

interface Provider {
  id: number;
  name: string;
}

interface Props {
  plans: Plan[];
  providers: Provider[];
}

const MarketAnalytics: React.FC<Props> = ({ plans, providers }) => {
  const getProviderName = (providerId: number) => {
    return providers.find((p) => p.id === providerId)?.name || 'Unknown';
  };

  // Calculate comprehensive statistics
  const stats = useMemo(() => {
    const plansWithRates = plans.filter((p) => p.rate_1000_cents && p.rate_1000_cents > 0);
    if (!plansWithRates.length) return null;

    const rates = plansWithRates.map((p) => p.rate_1000_cents!).sort((a, b) => a - b);
    const n = rates.length;

    // Basic stats
    const min = rates[0];
    const max = rates[n - 1];
    const sum = rates.reduce((a, b) => a + b, 0);
    const mean = sum / n;
    const median = n % 2 === 0 ? (rates[n / 2 - 1] + rates[n / 2]) / 2 : rates[Math.floor(n / 2)];

    // Percentiles
    const p10 = rates[Math.floor(n * 0.1)];
    const p25 = rates[Math.floor(n * 0.25)];
    const p75 = rates[Math.floor(n * 0.75)];
    const p90 = rates[Math.floor(n * 0.9)];

    // Standard deviation
    const variance = rates.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);

    // By service type
    const residential = plansWithRates.filter((p) => p.service_type === 'Residential');
    const commercial = plansWithRates.filter((p) => p.service_type === 'Commercial');

    const residentialAvg = residential.length
      ? residential.reduce((a, p) => a + (p.rate_1000_cents || 0), 0) / residential.length
      : 0;
    const commercialAvg = commercial.length
      ? commercial.reduce((a, p) => a + (p.rate_1000_cents || 0), 0) / commercial.length
      : 0;

    // By plan type
    const fixed = plansWithRates.filter((p) => p.plan_type?.toLowerCase().includes('fixed'));
    const variable = plansWithRates.filter((p) => p.plan_type?.toLowerCase().includes('variable'));

    // Provider stats
    const providerStats = new Map<string, { count: number; total: number; min: number }>();
    plansWithRates.forEach((plan) => {
      const name = getProviderName(plan.provider_id);
      const rate = plan.rate_1000_cents!;
      const existing = providerStats.get(name) || { count: 0, total: 0, min: Infinity };
      providerStats.set(name, {
        count: existing.count + 1,
        total: existing.total + rate,
        min: Math.min(existing.min, rate),
      });
    });

    const topProviders = Array.from(providerStats.entries())
      .map(([name, data]) => ({
        name,
        count: data.count,
        avgRate: data.total / data.count,
        bestRate: data.min,
      }))
      .sort((a, b) => a.bestRate - b.bestRate)
      .slice(0, 10);

    // Contract term distribution
    const termDistribution = new Map<number, number>();
    plansWithRates.forEach((plan) => {
      const term = plan.contract_months || 0;
      termDistribution.set(term, (termDistribution.get(term) || 0) + 1);
    });

    return {
      total: n,
      min,
      max,
      mean,
      median,
      stdDev,
      p10,
      p25,
      p75,
      p90,
      residential: residential.length,
      commercial: commercial.length,
      residentialAvg,
      commercialAvg,
      fixed: fixed.length,
      variable: variable.length,
      topProviders,
      termDistribution: Array.from(termDistribution.entries()).sort((a, b) => a[0] - b[0]),
      rateSpread: max - min,
    };
  }, [plans, providers]);

  if (!stats) {
    return (
      <div className="analytics-card glass">
        <p>No data available for analysis</p>
      </div>
    );
  }

  // Price distribution histogram
  const priceHistogram = useMemo(() => {
    const plansWithRates = plans.filter((p) => p.rate_1000_cents);
    const buckets = [
      { label: '<6¢', min: 0, max: 6, count: 0, color: '#10b981' },
      { label: '6-8¢', min: 6, max: 8, count: 0, color: '#22c55e' },
      { label: '8-10¢', min: 8, max: 10, count: 0, color: '#84cc16' },
      { label: '10-12¢', min: 10, max: 12, count: 0, color: '#eab308' },
      { label: '12-15¢', min: 12, max: 15, count: 0, color: '#f97316' },
      { label: '>15¢', min: 15, max: Infinity, count: 0, color: '#ef4444' },
    ];

    plansWithRates.forEach((plan) => {
      const rate = plan.rate_1000_cents!;
      const bucket = buckets.find((b) => rate >= b.min && rate < b.max);
      if (bucket) bucket.count++;
    });

    return {
      labels: buckets.map((b) => b.label),
      datasets: [
        {
          label: 'Number of Plans',
          data: buckets.map((b) => b.count),
          backgroundColor: buckets.map((b) => b.color),
          borderRadius: 8,
        },
      ],
    };
  }, [plans]);

  // Provider comparison chart
  const providerChart = useMemo(() => {
    return {
      labels: stats.topProviders.map((p) => p.name),
      datasets: [
        {
          label: 'Best Rate (¢/kWh)',
          data: stats.topProviders.map((p) => p.bestRate),
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderRadius: 6,
        },
        {
          label: 'Average Rate (¢/kWh)',
          data: stats.topProviders.map((p) => p.avgRate),
          backgroundColor: 'rgba(59, 130, 246, 0.6)',
          borderRadius: 6,
        },
      ],
    };
  }, [stats]);

  // Service type comparison
  const serviceTypeChart = useMemo(() => {
    return {
      labels: ['Residential', 'Commercial'],
      datasets: [
        {
          data: [stats.residential, stats.commercial],
          backgroundColor: ['rgba(59, 130, 246, 0.8)', 'rgba(16, 185, 129, 0.8)'],
          borderWidth: 0,
        },
      ],
    };
  }, [stats]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: '#64748b', font: { size: 12 } },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#64748b' },
      },
      y: {
        grid: { color: 'rgba(100, 116, 139, 0.1)' },
        ticks: { color: '#64748b' },
      },
    },
  };

  return (
    <div className="analytics-dashboard">
      <h2 className="section-title">
        <span className="icon">📊</span> Market Analytics Dashboard
      </h2>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card glass green">
          <div className="kpi-icon">💰</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.min.toFixed(2)}¢</div>
            <div className="kpi-label">Lowest Rate</div>
          </div>
        </div>
        <div className="kpi-card glass blue">
          <div className="kpi-icon">📈</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.mean.toFixed(2)}¢</div>
            <div className="kpi-label">Average Rate</div>
          </div>
        </div>
        <div className="kpi-card glass purple">
          <div className="kpi-icon">📊</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.median.toFixed(2)}¢</div>
            <div className="kpi-label">Median Rate</div>
          </div>
        </div>
        <div className="kpi-card glass orange">
          <div className="kpi-icon">📉</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats.max.toFixed(2)}¢</div>
            <div className="kpi-label">Highest Rate</div>
          </div>
        </div>
      </div>

      {/* Statistical Summary */}
      <div className="stats-grid">
        <div className="analytics-card glass">
          <h3 className="card-header">📐 Statistical Summary</h3>
          <div className="stat-rows">
            <div className="stat-row">
              <span className="stat-label">Total Plans Analyzed</span>
              <span className="stat-value">{stats.total}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Rate Spread</span>
              <span className="stat-value">{stats.rateSpread.toFixed(2)}¢</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Standard Deviation</span>
              <span className="stat-value">±{stats.stdDev.toFixed(2)}¢</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">10th Percentile</span>
              <span className="stat-value">{stats.p10.toFixed(2)}¢</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">25th Percentile</span>
              <span className="stat-value">{stats.p25.toFixed(2)}¢</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">75th Percentile</span>
              <span className="stat-value">{stats.p75.toFixed(2)}¢</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">90th Percentile</span>
              <span className="stat-value">{stats.p90.toFixed(2)}¢</span>
            </div>
          </div>
        </div>

        <div className="analytics-card glass">
          <h3 className="card-header">🏠 Residential vs Commercial</h3>
          <div className="comparison-grid">
            <div className="comparison-item residential">
              <div className="comparison-value">{stats.residential}</div>
              <div className="comparison-label">Residential Plans</div>
              <div className="comparison-avg">{stats.residentialAvg.toFixed(2)}¢ avg</div>
            </div>
            <div className="comparison-divider">vs</div>
            <div className="comparison-item commercial">
              <div className="comparison-value">{stats.commercial}</div>
              <div className="comparison-label">Commercial Plans</div>
              <div className="comparison-avg">{stats.commercialAvg.toFixed(2)}¢ avg</div>
            </div>
          </div>
          <div className="chart-container small">
            <Doughnut
              data={serviceTypeChart}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'bottom', labels: { color: '#64748b' } },
                },
              }}
            />
          </div>
        </div>

        <div className="analytics-card glass">
          <h3 className="card-header">📋 Plan Type Breakdown</h3>
          <div className="type-breakdown">
            <div className="type-item">
              <div className="type-bar" style={{ width: `${(stats.fixed / stats.total) * 100}%` }}>
                <span className="type-count">{stats.fixed}</span>
              </div>
              <span className="type-label">Fixed Rate</span>
            </div>
            <div className="type-item">
              <div
                className="type-bar variable"
                style={{ width: `${(stats.variable / stats.total) * 100}%` }}
              >
                <span className="type-count">{stats.variable}</span>
              </div>
              <span className="type-label">Variable Rate</span>
            </div>
            <div className="type-item">
              <div
                className="type-bar other"
                style={{
                  width: `${((stats.total - stats.fixed - stats.variable) / stats.total) * 100}%`,
                }}
              >
                <span className="type-count">{stats.total - stats.fixed - stats.variable}</span>
              </div>
              <span className="type-label">Other Types</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        <div className="analytics-card glass wide">
          <h3 className="card-header">📊 Price Distribution</h3>
          <div className="chart-container">
            <Bar data={priceHistogram} options={chartOptions} />
          </div>
        </div>

        <div className="analytics-card glass wide">
          <h3 className="card-header">🏆 Provider Comparison (Top 10)</h3>
          <div className="chart-container">
            <Bar
              data={providerChart}
              options={{
                ...chartOptions,
                indexAxis: 'y' as const,
              }}
            />
          </div>
        </div>
      </div>

      {/* Provider Rankings */}
      <div className="analytics-card glass full-width">
        <h3 className="card-header">🥇 Provider Performance Rankings</h3>
        <div className="rankings-table">
          <div className="rankings-header">
            <span>Rank</span>
            <span>Provider</span>
            <span>Best Rate</span>
            <span>Avg Rate</span>
            <span>Plans</span>
          </div>
          {stats.topProviders.map((provider, index) => (
            <div className="rankings-row" key={provider.name}>
              <span className={`rank rank-${index + 1}`}>
                {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
              </span>
              <span className="provider-name">{provider.name}</span>
              <span className="best-rate">{provider.bestRate.toFixed(2)}¢</span>
              <span className="avg-rate">{provider.avgRate.toFixed(2)}¢</span>
              <span className="plan-count">{provider.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Contract Term Distribution */}
      <div className="analytics-card glass full-width">
        <h3 className="card-header">📅 Contract Term Distribution</h3>
        <div className="term-distribution">
          {stats.termDistribution.map(([term, count]) => (
            <div className="term-item" key={term}>
              <div className="term-bar" style={{ height: `${(count / stats.total) * 300}px` }}>
                <span className="term-count">{count}</span>
              </div>
              <span className="term-label">{term === 0 ? 'MTM' : `${term}mo`}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketAnalytics;
