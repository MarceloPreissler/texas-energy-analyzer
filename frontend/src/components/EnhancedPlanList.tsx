import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchPlans, fetchProviders } from '../services/api';
import PlanComparison from './PlanComparison';

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  contract_months?: number | null;
  rate_500_cents?: number | null;
  rate_1000_cents?: number | null;
  rate_2000_cents?: number | null;
  monthly_bill_1000?: number | null;
  special_features?: string | null;
}

interface Provider {
  id: number;
  name: string;
}

const EnhancedPlanList: React.FC = () => {
  const [providerFilter, setProviderFilter] = useState<string | undefined>(undefined);
  const [planTypeFilter, setPlanTypeFilter] = useState<string | undefined>(undefined);
  const [contractFilter, setContractFilter] = useState<number | undefined>(undefined);
  const [selectedPlans, setSelectedPlans] = useState<Plan[]>([]);
  const [usage, setUsage] = useState<number>(1146); // Texas average

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: fetchProviders,
  });

  const { data: plans, isLoading } = useQuery({
    queryKey: ['plans', providerFilter, planTypeFilter, contractFilter],
    queryFn: () => fetchPlans(providerFilter, planTypeFilter, contractFilter),
  });

  const getRateClass = (rate: number | null | undefined): string => {
    if (!rate) return '';
    if (rate < 12) return 'rate-good';
    if (rate < 15) return 'rate-warning';
    return 'rate-high';
  };

  const calculateMonthlyCost = (rate: number | null | undefined): number => {
    if (!rate) return 0;
    return (usage * rate / 100) + 9.95; // Base charge estimate
  };

  const handleSelect = (plan: Plan) => {
    setSelectedPlans((prev) => {
      if (prev.some((p) => p.id === plan.id)) {
        return prev.filter((p) => p.id !== plan.id);
      }
      if (prev.length >= 5) {
        alert('Maximum 5 plans can be selected for comparison');
        return prev;
      }
      return [...prev, plan];
    });
  };

  // Calculate summary stats
  const summaryStats = useMemo(() => {
    if (!plans || plans.length === 0) return null;

    const plansWithRates = plans.filter(p => p.rate_1000_cents);
    if (plansWithRates.length === 0) return null;

    const rates = plansWithRates.map(p => p.rate_1000_cents!);
    const lowestRate = Math.min(...rates);
    const highestRate = Math.max(...rates);
    const avgRate = rates.reduce((a, b) => a + b, 0) / rates.length;

    const bestPlan = plansWithRates.find(p => p.rate_1000_cents === lowestRate);
    const worstPlan = plansWithRates.find(p => p.rate_1000_cents === highestRate);

    return {
      lowestRate,
      highestRate,
      avgRate: avgRate.toFixed(2),
      bestPlan,
      worstPlan,
      totalPlans: plans.length,
      potentialSavings: calculateMonthlyCost(highestRate) - calculateMonthlyCost(lowestRate)
    };
  }, [plans, usage]);

  // Generate recommendations
  const getRecommendations = (): string => {
    if (!summaryStats) return '';

    const { lowestRate, avgRate, bestPlan, potentialSavings } = summaryStats;
    const providerName = providers?.find(p => p.id === bestPlan?.provider_id)?.name || 'Unknown';

    return `Based on ${summaryStats.totalPlans} plans analyzed, the best rate is ${lowestRate.toFixed(1)}¢/kWh from ${providerName} (${bestPlan?.plan_name}).

The market average is ${avgRate}¢/kWh. If you're currently paying above ${avgRate}¢/kWh, you could save up to $${(potentialSavings * 12).toFixed(0)}/year by switching to the best available plan.

With your usage of ${usage} kWh/month, your estimated bill with the best plan would be $${calculateMonthlyCost(lowestRate).toFixed(2)}/month.`;
  };

  if (isLoading) {
    return <div className="card"><div className="loading">Loading plans...</div></div>;
  }

  return (
    <>
      <div className="dashboard">
        {summaryStats && (
          <>
            <div className="card">
              <h2 className="card-title">📊 Market Overview</h2>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>Lowest Rate:</div>
                <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#4CAF50' }}>
                  {summaryStats.lowestRate.toFixed(1)}¢/kWh
                </div>
              </div>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>Average Rate:</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#2c5364' }}>
                  {summaryStats.avgRate}¢/kWh
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>Plans Available:</div>
                <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: '#2c5364' }}>
                  {summaryStats.totalPlans}
                </div>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">💰 Savings Potential</h2>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>Monthly Savings:</div>
                <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#4CAF50' }}>
                  ${summaryStats.potentialSavings.toFixed(0)}
                </div>
              </div>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>Annual Savings:</div>
                <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#4CAF50' }}>
                  ${(summaryStats.potentialSavings * 12).toFixed(0)}
                </div>
              </div>
              <div className="savings-badge">
                Switch to save up to ${(summaryStats.potentialSavings * 12).toFixed(0)}/year
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">🔍 Best Plan</h2>
              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '0.9em', color: '#666' }}>Provider:</div>
                <div style={{ fontSize: '1.2em', fontWeight: 'bold', color: '#2c5364' }}>
                  {providers?.find(p => p.id === summaryStats.bestPlan?.provider_id)?.name}
                </div>
              </div>
              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '0.9em', color: '#666' }}>Plan:</div>
                <div style={{ fontSize: '1em', color: '#555' }}>
                  {summaryStats.bestPlan?.plan_name}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.9em', color: '#666' }}>Rate:</div>
                <div style={{ fontSize: '1.8em', fontWeight: 'bold', color: '#4CAF50' }}>
                  {summaryStats.lowestRate.toFixed(1)}¢/kWh
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="card">
        <h2 className="card-title">🔍 Filter Plans</h2>
        <div className="filter-controls">
          <div className="filter-group">
            <label>Provider:</label>
            <select
              value={providerFilter ?? ''}
              onChange={(e) => setProviderFilter(e.target.value || undefined)}
            >
              <option value="">All Providers</option>
              {providers?.map((provider) => (
                <option key={provider.id} value={provider.name}>{provider.name}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Plan Type:</label>
            <select
              value={planTypeFilter ?? ''}
              onChange={(e) => setPlanTypeFilter(e.target.value || undefined)}
            >
              <option value="">All Types</option>
              <option value="Fixed">Fixed</option>
              <option value="Variable">Variable</option>
              <option value="Solar">Solar</option>
              <option value="Free Nights/Weekends">Free Nights/Weekends</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Contract Term (months):</label>
            <input
              type="number"
              value={contractFilter ?? ''}
              onChange={(e) => setContractFilter(e.target.value ? Number(e.target.value) : undefined)}
              placeholder="e.g. 12"
            />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">📋 Available Plans ({plans?.length || 0})</h2>
        <div style={{ overflowX: 'auto' }}>
          <table className="plans-table">
            <thead>
              <tr>
                <th>Select</th>
                <th>Provider</th>
                <th>Plan</th>
                <th>Type</th>
                <th>Term (mo)</th>
                <th>Rate @1,000 kWh</th>
                <th>Est. Monthly Bill*</th>
                <th>Features</th>
              </tr>
            </thead>
            <tbody>
              {plans?.map((plan) => (
                <tr key={plan.id}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedPlans.some((p) => p.id === plan.id)}
                      onChange={() => handleSelect(plan)}
                    />
                  </td>
                  <td><strong>{providers?.find((p) => p.id === plan.provider_id)?.name}</strong></td>
                  <td>{plan.plan_name}</td>
                  <td>{plan.plan_type ?? '-'}</td>
                  <td>{plan.contract_months ?? '-'}</td>
                  <td className={getRateClass(plan.rate_1000_cents)}>
                    {plan.rate_1000_cents ? `${plan.rate_1000_cents}¢` : '-'}
                  </td>
                  <td>
                    {plan.rate_1000_cents
                      ? `$${calculateMonthlyCost(plan.rate_1000_cents).toFixed(2)}`
                      : '-'
                    }
                  </td>
                  <td style={{ fontSize: '0.85em', maxWidth: '300px' }}>
                    {plan.special_features ?? '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ marginTop: '10px', fontSize: '0.85em', color: '#666' }}>
          *Based on usage of {usage} kWh/month. Includes estimated $9.95 base charge.
        </p>
      </div>

      {selectedPlans.length > 0 && (
        <PlanComparison plans={selectedPlans} />
      )}

      <div className="card calculator-section">
        <h2 className="card-title">🧮 Cost Calculator</h2>
        <div className="input-group">
          <label>Monthly Usage (kWh)</label>
          <input
            type="number"
            value={usage}
            onChange={(e) => setUsage(Number(e.target.value))}
            min="0"
            max="5000"
          />
        </div>
        <p style={{ fontSize: '0.85em', color: '#666', marginTop: '10px' }}>
          Texas residential average: 1,146 kWh/month. Adjust to see personalized estimates.
        </p>
      </div>

      {summaryStats && (
        <div className="card summary-section">
          <h2 className="card-title">📋 Your Personalized Summary</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <p className="summary-label">Plans Analyzed</p>
              <p className="summary-value">{summaryStats.totalPlans}</p>
            </div>
            <div className="summary-item">
              <p className="summary-label">Best Rate</p>
              <p className="summary-value" style={{ color: '#4CAF50' }}>{summaryStats.lowestRate.toFixed(1)}¢</p>
            </div>
            <div className="summary-item">
              <p className="summary-label">Market Average</p>
              <p className="summary-value">{summaryStats.avgRate}¢</p>
            </div>
            <div className="summary-item">
              <p className="summary-label">Potential Savings</p>
              <p className="summary-value" style={{ color: '#4CAF50' }}>
                ${(summaryStats.potentialSavings * 12).toFixed(0)}/yr
              </p>
            </div>
          </div>

          <div className="recommendations">
            <h3>💡 Recommendations</h3>
            <p>{getRecommendations()}</p>
            <p style={{ marginTop: '15px', fontSize: '0.9em', color: '#666' }}>
              <strong>Next Steps:</strong> Review the plans above, select 2-3 to compare, and consider contract terms
              that match your needs. Longer terms (24-36 months) typically offer better rates but less flexibility.
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export default EnhancedPlanList;
