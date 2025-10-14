import React, { useMemo } from 'react';
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
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  rate_1000_cents?: number | null;
}

interface Provider {
  id: number;
  name: string;
}

interface Props {
  plans: Plan[];
  providers: Provider[];
}

const PriceAnalytics: React.FC<Props> = ({ plans, providers }) => {
  const analytics = useMemo(() => {
    const plansWithRates = plans.filter(p => p.rate_1000_cents);

    // Price distribution (histogram)
    const priceRanges = {
      '< 10¢': 0,
      '10-12¢': 0,
      '12-14¢': 0,
      '14-16¢': 0,
      '> 16¢': 0,
    };

    plansWithRates.forEach(plan => {
      const rate = plan.rate_1000_cents!;
      if (rate < 10) priceRanges['< 10¢']++;
      else if (rate < 12) priceRanges['10-12¢']++;
      else if (rate < 14) priceRanges['12-14¢']++;
      else if (rate < 16) priceRanges['14-16¢']++;
      else priceRanges['> 16¢']++;
    });

    // Provider comparison (average rate by provider)
    const providerRates: Record<string, number[]> = {};
    plansWithRates.forEach(plan => {
      const provider = providers.find(p => p.id === plan.provider_id);
      if (provider) {
        if (!providerRates[provider.name]) {
          providerRates[provider.name] = [];
        }
        providerRates[provider.name].push(plan.rate_1000_cents!);
      }
    });

    const providerAvgs = Object.entries(providerRates)
      .map(([name, rates]) => ({
        name,
        avgRate: rates.reduce((a, b) => a + b, 0) / rates.length,
        minRate: Math.min(...rates),
        count: rates.length,
      }))
      .sort((a, b) => a.avgRate - b.avgRate)
      .slice(0, 10); // Top 10 providers

    // Plan type distribution
    const planTypes: Record<string, number> = {};
    plans.forEach(plan => {
      const type = plan.plan_type || 'Unknown';
      planTypes[type] = (planTypes[type] || 0) + 1;
    });

    return {
      priceRanges,
      providerAvgs,
      planTypes,
    };
  }, [plans, providers]);

  const priceDistributionData = {
    labels: Object.keys(analytics.priceRanges),
    datasets: [
      {
        label: 'Number of Plans',
        data: Object.values(analytics.priceRanges),
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 99, 132, 0.6)',
        ],
      },
    ],
  };

  const providerComparisonData = {
    labels: analytics.providerAvgs.map(p => p.name),
    datasets: [
      {
        label: 'Average Rate (¢/kWh)',
        data: analytics.providerAvgs.map(p => p.avgRate),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: 'Best Rate (¢/kWh)',
        data: analytics.providerAvgs.map(p => p.minRate),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const planTypeData = {
    labels: Object.keys(analytics.planTypes),
    datasets: [
      {
        data: Object.values(analytics.planTypes),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  };

  return (
    <div className="analytics-container">
      <div className="card">
        <h2 className="card-title">📊 Price Distribution</h2>
        <div style={{ height: '300px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
          <Bar data={priceDistributionData} options={chartOptions} />
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">🏢 Provider Comparison (Top 10)</h2>
        <div style={{ height: '400px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
          <Bar
            data={providerComparisonData}
            options={{
              ...chartOptions,
              indexAxis: 'y' as const,
            }}
          />
        </div>
        <p style={{ marginTop: '10px', fontSize: '0.85em', color: '#666' }}>
          Showing average and best rates for providers with the most plans
        </p>
      </div>

      <div className="card">
        <h2 className="card-title">📋 Plan Type Distribution</h2>
        <div style={{ height: '300px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
          <Pie data={planTypeData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
};

export default PriceAnalytics;
