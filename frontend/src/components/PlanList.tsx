import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchPlans, fetchProviders } from '../services/api';
import PlanComparison from './PlanComparison';

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  contract_months?: number | null;
  rate_1000_cents?: number | null;
  monthly_bill_1000?: number | null;
  special_features?: string | null;
}

const PlanList: React.FC = () => {
  const [providerFilter, setProviderFilter] = useState<string | undefined>(undefined);
  const [planTypeFilter, setPlanTypeFilter] = useState<string | undefined>(undefined);
  const [contractFilter, setContractFilter] = useState<number | undefined>(undefined);
  const [selectedPlans, setSelectedPlans] = useState<Plan[]>([]);

  const { data: providers } = useQuery(['providers'], fetchProviders);
  const { data: plans, refetch } = useQuery([
    'plans',
    providerFilter,
    planTypeFilter,
    contractFilter,
  ], () => fetchPlans(providerFilter, planTypeFilter, contractFilter));

  const handleSelect = (plan: Plan) => {
    setSelectedPlans((prev) => {
      if (prev.some((p) => p.id === plan.id)) {
        return prev.filter((p) => p.id !== plan.id);
      }
      return [...prev, plan];
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <label>
          Provider:
          <select
            value={providerFilter ?? ''}
            onChange={(e) => setProviderFilter(e.target.value || undefined)}
          >
            <option value="">All</option>
            {providers?.map((provider) => (
              <option key={provider.id} value={provider.name}>{provider.name}</option>
            ))}
          </select>
        </label>
        <label>
          Plan type:
          <select
            value={planTypeFilter ?? ''}
            onChange={(e) => setPlanTypeFilter(e.target.value || undefined)}
          >
            <option value="">All</option>
            <option value="Fixed">Fixed</option>
            <option value="Variable">Variable</option>
            <option value="Solar">Solar</option>
            <option value="Free Nights/Weekends">Free Nights/Weekends</option>
          </select>
        </label>
        <label>
          Term (months):
          <input
            type="number"
            value={contractFilter ?? ''}
            onChange={(e) => setContractFilter(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="e.g. 12"
            style={{ width: '5rem' }}
          />
        </label>
        <button onClick={() => refetch()}>Apply Filters</button>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Select</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Provider</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Plan</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Type</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Term (mo)</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Rate @1,000 kWh (¢)</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Estimated Bill ($)</th>
            <th style={{ borderBottom: '1px solid #ccc', textAlign: 'left' }}>Features</th>
          </tr>
        </thead>
        <tbody>
          {plans?.map((plan) => (
            <tr key={plan.id} style={{ borderBottom: '1px solid #eee' }}>
              <td>
                <input
                  type="checkbox"
                  checked={selectedPlans.some((p) => p.id === plan.id)}
                  onChange={() => handleSelect(plan)}
                />
              </td>
              <td>{providers?.find((p) => p.id === plan.provider_id)?.name}</td>
              <td>{plan.plan_name}</td>
              <td>{plan.plan_type ?? '-'}</td>
              <td>{plan.contract_months ?? '-'}</td>
              <td>{plan.rate_1000_cents ?? '-'}</td>
              <td>{plan.monthly_bill_1000 ?? '-'}</td>
              <td>{plan.special_features ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {selectedPlans.length > 0 && (
        <PlanComparison plans={selectedPlans} />
      )}
    </div>
  );
};

export default PlanList;