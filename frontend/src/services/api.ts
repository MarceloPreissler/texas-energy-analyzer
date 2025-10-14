import axios from 'axios';

// Detect if accessing via ngrok and use direct backend connection
const isNgrok = window.location.hostname.includes('ngrok');
const isLocalhost = window.location.hostname === 'localhost';

// API base URL logic:
// - localhost: use Vite proxy (empty string)
// - ngrok: use local network IP for backend
// - local network IP: use Vite proxy
const API_BASE_URL = isNgrok ? 'http://10.0.0.16:8000' : '';

const api = axios.create({
  baseURL: API_BASE_URL,
});

interface Provider {
  id: number;
  name: string;
}

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_type?: string | null;
  service_type?: string | null;
  zip_code?: string | null;
  contract_months?: number | null;
  rate_1000_cents?: number | null;
  monthly_bill_1000?: number | null;
  special_features?: string | null;
}

export async function fetchProviders(): Promise<Provider[]> {
  const res = await api.get<Provider[]>('/plans/providers');
  return res.data;
}

export async function fetchPlans(
  provider?: string,
  planType?: string,
  serviceType?: string,
  zipCode?: string,
  contractMonths?: number
): Promise<Plan[]> {
  const params: Record<string, string | number> = {};
  if (provider) params.provider = provider;
  if (planType) params.plan_type = planType;
  if (serviceType) params.service_type = serviceType;
  if (zipCode) params.zip_code = zipCode;
  if (contractMonths) params.contract_months = contractMonths;
  const res = await api.get<Plan[]>('/plans', { params });
  return res.data;
}

export async function triggerScrape(
  serviceType: string = 'Residential',
  zipCode?: string
): Promise<any> {
  const params: Record<string, string> = {
    source: 'powertochoose',
    service_type: serviceType
  };
  if (zipCode) params.zip_code = zipCode;
  const res = await api.post('/plans/scrape', null, { params });
  return res.data;
}