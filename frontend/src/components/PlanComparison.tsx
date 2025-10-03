import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Plan {
  id: number;
  plan_name: string;
  rate_1000_cents?: number | null;
  monthly_bill_1000?: number | null;
  rate_500_cents?: number | null;
  rate_2000_cents?: number | null;
}

const PlanComparison: React.FC<{ plans: Plan[] }> = ({ plans }) => {
  if (plans.length === 0) {
    return null;
  }

  const chartData = {
    labels: plans.map(p => p.plan_name),
    datasets: [
      {
        label: 'Rate @ 1,000 kWh (¢/kWh)',
        data: plans.map(p => p.rate_1000_cents ?? 0),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Plan Rate Comparison',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: '¢/kWh',
        },
      },
    },
  };

  return (
    <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd' }}>
      <h2>Plan Comparison</h2>
      <Bar data={chartData} options={options} />
      <div style={{ marginTop: '1rem' }}>
        <h3>Details</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Plan</th>
              <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Rate @ 500 kWh</th>
              <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Rate @ 1,000 kWh</th>
              <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Rate @ 2,000 kWh</th>
              <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Est. Bill @ 1,000 kWh</th>
            </tr>
          </thead>
          <tbody>
            {plans.map(plan => (
              <tr key={plan.id} style={{ borderBottom: '1px solid #eee' }}>
                <td>{plan.plan_name}</td>
                <td>{plan.rate_500_cents ? `${plan.rate_500_cents}¢` : '-'}</td>
                <td>{plan.rate_1000_cents ? `${plan.rate_1000_cents}¢` : '-'}</td>
                <td>{plan.rate_2000_cents ? `${plan.rate_2000_cents}¢` : '-'}</td>
                <td>{plan.monthly_bill_1000 ? `$${plan.monthly_bill_1000}` : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlanComparison;