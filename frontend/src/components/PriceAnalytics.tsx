import React, { useMemo, useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
);

// API base URL for fetching all plans
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://web-production-665ac.up.railway.app';

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  service_type?: string | null;
  contract_months?: number | null;
  rate_1000_cents?: number | null;
  renewable_percent?: number | null;
  special_features?: string | null;
}

// TDU patterns for extraction
const TDU_PATTERNS = [
  { pattern: /Oncor|Dallas/i, name: 'Oncor' },
  { pattern: /CenterPoint|Houston/i, name: 'CenterPoint' },
  { pattern: /AEP.*Central|Corpus/i, name: 'AEP Central' },
  { pattern: /AEP.*North|Abilene/i, name: 'AEP North' },
  { pattern: /TNMP|Midland/i, name: 'TNMP' },
  { pattern: /Lubbock/i, name: 'Lubbock P&L' },
];

const extractTDU = (features: string | null | undefined): string => {
  if (!features) return 'Unknown';
  for (const { pattern, name } of TDU_PATTERNS) {
    if (pattern.test(features)) return name;
  }
  return 'Unknown';
};

interface Provider {
  id: number;
  name: string;
}

interface Props {
  plans: Plan[];
  providers: Provider[];
}

interface TDUDistribution {
  [key: string]: number;
}

const PriceAnalytics: React.FC<Props> = ({ plans, providers }) => {
  // State for TDU distribution (all plans)
  const [tduDistribution, setTduDistribution] = useState<TDUDistribution>({});
  const [totalPlansCount, setTotalPlansCount] = useState<number>(0);

  // Fetch all plans for TDU Distribution (ignores filters)
  useEffect(() => {
    const fetchAllPlans = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/plans/?limit=10000`);
        if (response.ok) {
          const allPlans: Plan[] = await response.json();
          const tduCounts: TDUDistribution = {};

          allPlans.forEach((plan) => {
            const tdu = extractTDU(plan.special_features);
            tduCounts[tdu] = (tduCounts[tdu] || 0) + 1;
          });

          setTduDistribution(tduCounts);
          setTotalPlansCount(allPlans.length);
        }
      } catch (error) {
        console.error('Failed to fetch all plans for TDU distribution:', error);
      }
    };

    fetchAllPlans();
  }, []);

  const analytics = useMemo(() => {
    const plansWithRates = plans.filter(p => p.rate_1000_cents && p.rate_1000_cents > 0);

    if (plansWithRates.length === 0) {
      return null;
    }

    // Calculate statistics
    const rates = plansWithRates.map(p => p.rate_1000_cents!).sort((a, b) => a - b);
    const n = rates.length;
    const min = rates[0];
    const max = rates[n - 1];
    const sum = rates.reduce((a, b) => a + b, 0);
    const mean = sum / n;
    const median = n % 2 === 0 ? (rates[n / 2 - 1] + rates[n / 2]) / 2 : rates[Math.floor(n / 2)];

    // Price distribution with finer granularity
    const priceRanges = [
      { label: '< 6¢', min: 0, max: 6, count: 0, color: '#10b981' },
      { label: '6-8¢', min: 6, max: 8, count: 0, color: '#22c55e' },
      { label: '8-10¢', min: 8, max: 10, count: 0, color: '#84cc16' },
      { label: '10-12¢', min: 10, max: 12, count: 0, color: '#eab308' },
      { label: '12-14¢', min: 12, max: 14, count: 0, color: '#f97316' },
      { label: '> 14¢', min: 14, max: Infinity, count: 0, color: '#ef4444' },
    ];

    plansWithRates.forEach(plan => {
      const rate = plan.rate_1000_cents!;
      const bucket = priceRanges.find(b => rate >= b.min && rate < b.max);
      if (bucket) bucket.count++;
    });

    // Provider comparison (average and best rate by provider)
    const providerRates: Record<string, { rates: number[], planCount: number }> = {};
    plansWithRates.forEach(plan => {
      const provider = providers.find(p => p.id === plan.provider_id);
      if (provider) {
        if (!providerRates[provider.name]) {
          providerRates[provider.name] = { rates: [], planCount: 0 };
        }
        providerRates[provider.name].rates.push(plan.rate_1000_cents!);
        providerRates[provider.name].planCount++;
      }
    });

    const providerAvgs = Object.entries(providerRates)
      .map(([name, data]) => ({
        name,
        avgRate: data.rates.reduce((a, b) => a + b, 0) / data.rates.length,
        minRate: Math.min(...data.rates),
        maxRate: Math.max(...data.rates),
        count: data.planCount,
      }))
      .filter(p => p.count >= 1)
      .sort((a, b) => a.minRate - b.minRate)
      .slice(0, 12);

    // Plan type distribution
    const planTypes: Record<string, number> = {};
    plansWithRates.forEach(plan => {
      const type = plan.plan_type || 'Other';
      planTypes[type] = (planTypes[type] || 0) + 1;
    });

    // Contract term analysis
    const contractTerms: Record<string, { count: number, avgRate: number }> = {};
    plansWithRates.forEach(plan => {
      const term = plan.contract_months || 0;
      const termLabel = term === 0 ? 'Month-to-Month' : `${term} Months`;
      if (!contractTerms[termLabel]) {
        contractTerms[termLabel] = { count: 0, avgRate: 0 };
      }
      contractTerms[termLabel].count++;
      contractTerms[termLabel].avgRate += plan.rate_1000_cents!;
    });

    Object.keys(contractTerms).forEach(key => {
      contractTerms[key].avgRate = contractTerms[key].avgRate / contractTerms[key].count;
    });

    return {
      total: n,
      min,
      max,
      mean,
      median,
      priceRanges,
      providerAvgs,
      planTypes,
      contractTerms,
    };
  }, [plans, providers]);

  if (!analytics) {
    return (
      <div className="price-analytics-container">
        <div className="analytics-card glass">
          <p>No rate data available for analysis</p>
        </div>
      </div>
    );
  }

  const priceDistributionData = {
    labels: analytics.priceRanges.map(r => r.label),
    datasets: [
      {
        label: 'Number of Plans',
        data: analytics.priceRanges.map(r => r.count),
        backgroundColor: analytics.priceRanges.map(r => r.color),
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  const providerComparisonData = {
    labels: analytics.providerAvgs.map(p => p.name),
    datasets: [
      {
        label: 'Best Rate',
        data: analytics.providerAvgs.map(p => p.minRate),
        backgroundColor: 'rgba(16, 185, 129, 0.85)',
        borderRadius: 6,
      },
      {
        label: 'Average Rate',
        data: analytics.providerAvgs.map(p => p.avgRate),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderRadius: 6,
      },
    ],
  };

  const planTypeColors = [
    '#3b82f6', '#10b981', '#f97316', '#8b5cf6', '#ec4899', '#06b6d4'
  ];

  const planTypeData = {
    labels: Object.keys(analytics.planTypes),
    datasets: [
      {
        data: Object.values(analytics.planTypes),
        backgroundColor: planTypeColors.slice(0, Object.keys(analytics.planTypes).length),
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  };

  // TDU Distribution data (all plans)
  const tduColors = ['#3b82f6', '#10b981', '#f97316', '#8b5cf6', '#ec4899', '#06b6d4', '#eab308'];
  const tduLabels = Object.keys(tduDistribution).sort((a, b) => tduDistribution[b] - tduDistribution[a]);
  const tduData = {
    labels: tduLabels,
    datasets: [
      {
        data: tduLabels.map(label => tduDistribution[label]),
        backgroundColor: tduColors.slice(0, tduLabels.length),
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
          font: { size: 12 },
          padding: 16,
        },
      },
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
  };

  const horizontalChartOptions = {
    ...chartOptions,
    indexAxis: 'y' as const,
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: '#ffffff' },
      },
      y: {
        grid: { display: false },
        ticks: { color: '#ffffff', font: { size: 11 } },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '60%',
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#ffffff',
          font: { size: 11 },
          padding: 12,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
    },
  };

  return (
    <div className="price-analytics-section">
      <h2 className="section-title">
        Retail Plan Analytics
      </h2>
      <p className="section-subtitle">
        Statistical analysis of {analytics.total} electricity plans from database
      </p>

      {/* Quick Stats Row */}
      <div className="quick-stats-row">
        <div className="quick-stat">
          <span className="quick-stat-value green">{analytics.min.toFixed(2)}¢</span>
          <span className="quick-stat-label">Lowest Rate</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value blue">{analytics.mean.toFixed(2)}¢</span>
          <span className="quick-stat-label">Average Rate</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value purple">{analytics.median.toFixed(2)}¢</span>
          <span className="quick-stat-label">Median Rate</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value orange">{analytics.max.toFixed(2)}¢</span>
          <span className="quick-stat-label">Highest Rate</span>
        </div>
        <div className="quick-stat">
          <span className="quick-stat-value">{analytics.total}</span>
          <span className="quick-stat-label">Total Plans</span>
        </div>
      </div>

      {/* Price Distribution (2/3) + TDU Distribution (1/3) */}
      <div className="analytics-charts-row">
        <div className="analytics-card glass two-thirds">
          <h3 className="analytics-card-title">Price Distribution</h3>
          <div className="chart-wrapper">
            <Bar data={priceDistributionData} options={chartOptions} />
          </div>
        </div>

        <div className="analytics-card glass one-third">
          <h3 className="analytics-card-title">TDU Distribution</h3>
          <div className="mckinsey-pie-container">
            <div className="mckinsey-pie-chart">
              <Doughnut
                data={tduData}
                options={{
                  responsive: true,
                  maintainAspectRatio: true,
                  cutout: '0%',
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      callbacks: {
                        label: (context) => {
                          const value = context.parsed;
                          const percentage = ((value / totalPlansCount) * 100).toFixed(1);
                          return `${context.label}: ${value} (${percentage}%)`;
                        }
                      }
                    }
                  },
                }}
              />
            </div>
            <div className="mckinsey-legend-vertical">
              {tduLabels.map((tdu, index) => (
                <div key={tdu} className="mckinsey-legend-item">
                  <div className="mckinsey-legend-left">
                    <span
                      className="mckinsey-legend-dot"
                      style={{ backgroundColor: tduColors[index % tduColors.length] }}
                    />
                    <span className="mckinsey-legend-label">{tdu}</span>
                  </div>
                  <span className="mckinsey-legend-value">{tduDistribution[tdu]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Provider Rate Comparison */}
      <div className="analytics-charts-grid">
        <div className="analytics-card glass full-width">
          <h3 className="analytics-card-title">Provider Rate Comparison (Top 12)</h3>
          <div className="chart-wrapper-tall">
            <Bar data={providerComparisonData} options={horizontalChartOptions} />
          </div>
          <p className="chart-footnote">
            Rates shown in ¢/kWh at 1,000 kWh usage level
          </p>
        </div>
      </div>
    </div>
  );
};

export default PriceAnalytics;
