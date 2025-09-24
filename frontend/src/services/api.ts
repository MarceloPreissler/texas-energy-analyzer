import axios from 'axios';

interface Provider {
  id: number;
  name: string;
}

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

export async function fetchProviders(): Promise<Provider[]> {
  const res = await axios.get<Provider[]>('/plans/providers');
  return res.data;
}

export async function fetchPlans(
  provider?: string,
  planType?: string,
  contractMonths?: number
): Promise<Plan[]> {
  const params: Record<string, string | number> = {};
  if (provider) params.provider = provider;
  if (planType) params.plan_type = planType;
  if (contractMonths) params.contract_months = contractMonths;
  const res = await axios.get<Plan[]>('/plans', { params });
  return res.data;
}