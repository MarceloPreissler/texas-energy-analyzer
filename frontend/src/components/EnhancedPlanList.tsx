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
  website?: string | null;
}

const EnhancedPlanList: React.FC = () => {
  // Filter state (temporary, not applied until search)
  const [tempProviderFilter, setTempProviderFilter] = useState<string>('');
  const [tempPlanTypeFilter, setTempPlanTypeFilter] = useState<string>('');
  const [tempContractFilter, setTempContractFilter] = useState<string>('');

  // Applied filters (used for API query)
  const [providerFilter, setProviderFilter] = useState<string | undefined>(undefined);
  const [planTypeFilter, setPlanTypeFilter] = useState<string | undefined>(undefined);
  const [contractFilter, setContractFilter] = useState<number | undefined>(undefined);

  const [selectedPlans, setSelectedPlans] = useState<Plan[]>([]);
  const [usage, setUsage] = useState<number>(1146); // Texas average
  const [baseFee, setBaseFee] = useState<number>(9.95); // Default base fee
  const [useCustomBaseFee, setUseCustomBaseFee] = useState<boolean>(false);

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
    return (usage * rate / 100) + (useCustomBaseFee ? baseFee : 9.95);
  };

  const handleSearch = () => {
    setProviderFilter(tempProviderFilter || undefined);
    setPlanTypeFilter(tempPlanTypeFilter || undefined);
    setContractFilter(tempContractFilter ? Number(tempContractFilter) : undefined);
  };

  const handleReset = () => {
    setTempProviderFilter('');
    setTempPlanTypeFilter('');
    setTempContractFilter('');
    setProviderFilter(undefined);
    setPlanTypeFilter(undefined);
    setContractFilter(undefined);
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
              value={tempProviderFilter}
              onChange={(e) => setTempProviderFilter(e.target.value)}
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
              value={tempPlanTypeFilter}
              onChange={(e) => setTempPlanTypeFilter(e.target.value)}
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
              value={tempContractFilter}
              onChange={(e) => setTempContractFilter(e.target.value)}
              placeholder="e.g. 12"
            />
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button
            onClick={handleSearch}
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              flex: 1
            }}
          >
            🔍 Search Plans
          </button>
          <button
            onClick={handleReset}
            style={{
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              flex: 1
            }}
          >
            🔄 Reset Filters
          </button>
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
                  <td>
                    {(() => {
                      const provider = providers?.find((p) => p.id === plan.provider_id);
                      return provider?.website ? (
                        <a
                          href={provider.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: '#2196F3',
                            textDecoration: 'none',
                            fontWeight: 'bold'
                          }}
                        >
                          {provider.name} 🔗
                        </a>
                      ) : (
                        <strong>{provider?.name}</strong>
                      );
                    })()}
                  </td>
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
          *Based on usage of {usage} kWh/month. Includes {useCustomBaseFee ? `$${baseFee.toFixed(2)}` : '$9.95 (estimated)'} base charge.
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
        <div className="input-group" style={{ marginTop: '15px' }}>
          <label>Base Fee Calculation</label>
          <select
            value={useCustomBaseFee ? 'custom' : 'estimated'}
            onChange={(e) => setUseCustomBaseFee(e.target.value === 'custom')}
          >
            <option value="estimated">Estimated ($9.95/month)</option>
            <option value="custom">Custom Base Fee</option>
          </select>
        </div>
        {useCustomBaseFee && (
          <div className="input-group" style={{ marginTop: '15px' }}>
            <label>Custom Base Fee ($/month)</label>
            <input
              type="number"
              value={baseFee}
              onChange={(e) => setBaseFee(Number(e.target.value))}
              min="0"
              max="50"
              step="0.01"
            />
          </div>
        )}
        <p style={{ fontSize: '0.85em', color: '#666', marginTop: '10px' }}>
          Texas residential average: 1,146 kWh/month. Base fee: Most plans charge $5-$15/month in fixed charges.
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
