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
import { Bar, Line } from 'react-chartjs-2';

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
  cancellation_fee?: number | null;
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

    // Renewable Energy Premium Analysis
    const greenPlans = plansWithRates.filter((p) => (p.renewable_percent || 0) >= 90);
    const nonGreenPlans = plansWithRates.filter((p) => (p.renewable_percent || 0) < 50);
    const greenAvg = greenPlans.length
      ? greenPlans.reduce((a, p) => a + (p.rate_1000_cents || 0), 0) / greenPlans.length
      : 0;
    const nonGreenAvg = nonGreenPlans.length
      ? nonGreenPlans.reduce((a, p) => a + (p.rate_1000_cents || 0), 0) / nonGreenPlans.length
      : 0;
    const greenPremium = greenAvg > 0 && nonGreenAvg > 0 ? ((greenAvg - nonGreenAvg) / nonGreenAvg) * 100 : 0;

    // Provider Plan Portfolio Analysis (plan variety by provider)
    const providerPlanCounts: Record<string, { total: number; fixed: number; variable: number; renewable: number }> = {};
    plansWithRates.forEach((plan) => {
      const name = getProviderName(plan.provider_id);
      if (!providerPlanCounts[name]) {
        providerPlanCounts[name] = { total: 0, fixed: 0, variable: 0, renewable: 0 };
      }
      providerPlanCounts[name].total++;
      if (plan.plan_type?.toLowerCase().includes('fixed')) providerPlanCounts[name].fixed++;
      if (plan.plan_type?.toLowerCase().includes('variable')) providerPlanCounts[name].variable++;
      if ((plan.renewable_percent || 0) >= 90) providerPlanCounts[name].renewable++;
    });

    const providerPortfolio = Object.entries(providerPlanCounts)
      .map(([name, counts]) => ({ name, ...counts }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10); // Top 10 providers by plan count

    const totalProviders = Object.keys(providerPlanCounts).length;
    const avgPlansPerProvider = plansWithRates.length / totalProviders;

    // Contract term vs rate analysis
    const termRateAnalysis: Record<string, { count: number; totalRate: number; minRate: number }> = {};
    plansWithRates.forEach((plan) => {
      const term = plan.contract_months || 0;
      let termLabel: string;
      if (term === 0) termLabel = 'MTM';
      else if (term <= 6) termLabel = '1-6 mo';
      else if (term <= 12) termLabel = '7-12 mo';
      else if (term <= 24) termLabel = '13-24 mo';
      else termLabel = '24+ mo';

      if (!termRateAnalysis[termLabel]) {
        termRateAnalysis[termLabel] = { count: 0, totalRate: 0, minRate: Infinity };
      }
      termRateAnalysis[termLabel].count++;
      termRateAnalysis[termLabel].totalRate += plan.rate_1000_cents!;
      termRateAnalysis[termLabel].minRate = Math.min(termRateAnalysis[termLabel].minRate, plan.rate_1000_cents!);
    });

    // Provider rate consistency (std dev of rates per provider)
    const providerConsistency: { name: string; avgRate: number; stdDev: number; count: number }[] = [];
    const providerRates: Record<string, number[]> = {};
    plansWithRates.forEach((plan) => {
      const name = getProviderName(plan.provider_id);
      if (!providerRates[name]) providerRates[name] = [];
      providerRates[name].push(plan.rate_1000_cents!);
    });

    Object.entries(providerRates).forEach(([name, pRates]) => {
      if (pRates.length >= 2) {
        const avg = pRates.reduce((a, b) => a + b, 0) / pRates.length;
        const variance = pRates.reduce((acc, val) => acc + Math.pow(val - avg, 2), 0) / pRates.length;
        providerConsistency.push({
          name,
          avgRate: avg,
          stdDev: Math.sqrt(variance),
          count: pRates.length,
        });
      }
    });
    providerConsistency.sort((a, b) => a.stdDev - b.stdDev); // Most consistent first

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
      greenPlans: greenPlans.length,
      nonGreenPlans: nonGreenPlans.length,
      greenAvg,
      nonGreenAvg,
      greenPremium,
      providerPortfolio,
      totalProviders,
      avgPlansPerProvider,
      termRateAnalysis,
      providerConsistency: providerConsistency.slice(0, 8),
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

  // Renewable vs Non-Renewable chart
  const renewableComparisonData = {
    labels: ['90%+ Renewable', 'Under 50% Renewable'],
    datasets: [
      {
        label: 'Average Rate (¢/kWh)',
        data: [stats.greenAvg, stats.nonGreenAvg],
        backgroundColor: ['rgba(16, 185, 129, 0.8)', 'rgba(100, 116, 139, 0.6)'],
        borderRadius: 8,
      },
    ],
  };

  // Provider Plan Portfolio chart (stacked bar)
  const providerPortfolioData = {
    labels: stats.providerPortfolio.map((p) => p.name),
    datasets: [
      {
        label: 'Fixed Rate',
        data: stats.providerPortfolio.map((p) => p.fixed),
        backgroundColor: 'rgba(59, 130, 246, 0.85)',
        borderRadius: 4,
      },
      {
        label: 'Variable Rate',
        data: stats.providerPortfolio.map((p) => p.variable),
        backgroundColor: 'rgba(251, 146, 60, 0.85)',
        borderRadius: 4,
      },
      {
        label: 'Other',
        data: stats.providerPortfolio.map((p) => p.total - p.fixed - p.variable),
        backgroundColor: 'rgba(139, 92, 246, 0.85)',
        borderRadius: 4,
      },
    ],
  };

  // Contract term vs rate chart
  const termOrder = ['MTM', '1-6 mo', '7-12 mo', '13-24 mo', '24+ mo'];
  const orderedTermAnalysis = termOrder
    .filter((t) => stats.termRateAnalysis[t])
    .map((t) => ({ label: t, ...stats.termRateAnalysis[t] }));

  const termRateData = {
    labels: orderedTermAnalysis.map((t) => t.label),
    datasets: [
      {
        label: 'Avg Rate',
        data: orderedTermAnalysis.map((t) => t.totalRate / t.count),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Best Rate',
        data: orderedTermAnalysis.map((t) => t.minRate),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Provider consistency chart
  const consistencyData = {
    labels: stats.providerConsistency.map((p) => p.name),
    datasets: [
      {
        label: 'Rate Variability (±¢/kWh)',
        data: stats.providerConsistency.map((p) => p.stdDev),
        backgroundColor: stats.providerConsistency.map((_, i) =>
          i < 3 ? 'rgba(16, 185, 129, 0.8)' : i < 6 ? 'rgba(251, 191, 36, 0.8)' : 'rgba(239, 68, 68, 0.8)'
        ),
        borderRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: '#94a3b8', font: { size: 12 } },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#94a3b8' },
      },
      y: {
        grid: { color: 'rgba(100, 116, 139, 0.1)' },
        ticks: { color: '#94a3b8' },
      },
    },
  };

  return (
    <div className="analytics-dashboard">
      <h2 className="section-title">
        Advanced Market Insights
      </h2>
      <p className="section-subtitle">Deep analysis of {stats.total} electricity plans</p>

      {/* Statistical Summary */}
      <div className="stats-grid">
        <div className="analytics-card glass">
          <h3 className="card-header">Statistical Summary</h3>
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
          <h3 className="card-header">Green Energy Premium</h3>
          <div className="comparison-grid">
            <div className="comparison-item" style={{ background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05))', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <div className="comparison-value" style={{ fontSize: '2em' }}>{stats.greenPlans}</div>
              <div className="comparison-label">90%+ Renewable</div>
              <div className="comparison-avg">{stats.greenAvg.toFixed(2)}¢ avg</div>
            </div>
            <div className="comparison-divider">vs</div>
            <div className="comparison-item" style={{ background: 'linear-gradient(135deg, rgba(100, 116, 139, 0.15), rgba(100, 116, 139, 0.05))', border: '1px solid rgba(100, 116, 139, 0.3)' }}>
              <div className="comparison-value" style={{ fontSize: '2em' }}>{stats.nonGreenPlans}</div>
              <div className="comparison-label">Under 50% Renewable</div>
              <div className="comparison-avg">{stats.nonGreenAvg.toFixed(2)}¢ avg</div>
            </div>
          </div>
          <div style={{ textAlign: 'center', marginTop: '16px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
            <span style={{ color: stats.greenPremium > 0 ? '#f97316' : '#10b981', fontWeight: 600, fontSize: '1.1em' }}>
              {stats.greenPremium > 0 ? `+${stats.greenPremium.toFixed(1)}%` : `${stats.greenPremium.toFixed(1)}%`}
            </span>
            <span style={{ color: '#94a3b8', marginLeft: '8px' }}>
              {stats.greenPremium > 0 ? 'green premium' : 'green discount'}
            </span>
          </div>
        </div>

        <div className="analytics-card glass">
          <h3 className="card-header">Provider Plan Portfolio (Top 10)</h3>
          <div className="chart-container">
            <Bar
              data={providerPortfolioData}
              options={{
                ...chartOptions,
                indexAxis: 'y' as const,
                scales: {
                  x: {
                    stacked: true,
                    grid: { color: 'rgba(100, 116, 139, 0.1)' },
                    ticks: { color: '#94a3b8' },
                  },
                  y: {
                    stacked: true,
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                  },
                },
                plugins: {
                  legend: {
                    position: 'top' as const,
                    labels: { color: '#94a3b8', font: { size: 10 }, padding: 8 },
                  },
                },
              }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '12px', padding: '12px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '8px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#f1f5f9', fontWeight: 600, fontSize: '1.2em' }}>{stats.totalProviders}</div>
              <div style={{ color: '#94a3b8', fontSize: '0.8em' }}>Active Providers</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#f1f5f9', fontWeight: 600, fontSize: '1.2em' }}>{stats.avgPlansPerProvider.toFixed(1)}</div>
              <div style={{ color: '#94a3b8', fontSize: '0.8em' }}>Avg Plans/Provider</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        <div className="analytics-card glass wide">
          <h3 className="card-header">Contract Length vs Rate</h3>
          <div className="chart-container">
            <Line data={termRateData} options={chartOptions} />
          </div>
          <p className="chart-footnote">
            Longer terms often lock in better rates
          </p>
        </div>

        <div className="analytics-card glass wide">
          <h3 className="card-header">Provider Rate Consistency</h3>
          <div className="chart-container">
            <Bar
              data={consistencyData}
              options={{
                ...chartOptions,
                indexAxis: 'y' as const,
                plugins: {
                  ...chartOptions.plugins,
                  legend: { display: false },
                },
              }}
            />
          </div>
          <p className="chart-footnote">
            Lower variability = more consistent pricing across plans
          </p>
        </div>
      </div>

      {/* Plan Type Breakdown */}
      <div className="analytics-card glass full-width">
        <h3 className="card-header">Plan Type Breakdown</h3>
        <div className="type-breakdown">
          <div className="type-item">
            <div className="type-bar" style={{ width: `${Math.max((stats.fixed / stats.total) * 100, 10)}%` }}>
              <span className="type-count">{stats.fixed}</span>
            </div>
            <span className="type-label">Fixed Rate</span>
          </div>
          <div className="type-item">
            <div
              className="type-bar variable"
              style={{ width: `${Math.max((stats.variable / stats.total) * 100, 10)}%` }}
            >
              <span className="type-count">{stats.variable}</span>
            </div>
            <span className="type-label">Variable Rate</span>
          </div>
          <div className="type-item">
            <div
              className="type-bar other"
              style={{
                width: `${Math.max(((stats.total - stats.fixed - stats.variable) / stats.total) * 100, 10)}%`,
              }}
            >
              <span className="type-count">{stats.total - stats.fixed - stats.variable}</span>
            </div>
            <span className="type-label">Other Types</span>
          </div>
        </div>
      </div>

      {/* Contract Term Distribution */}
      <div className="analytics-card glass full-width">
        <h3 className="card-header">Contract Term Distribution</h3>
        <div className="term-distribution">
          {stats.termDistribution.map(([term, count]) => (
            <div className="term-item" key={term}>
              <div className="term-bar" style={{ height: `${Math.max((count / stats.total) * 300, 30)}px` }}>
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
