import axios from 'axios';

// Detect environment and set appropriate API base URL
const hostname = window.location.hostname;

// Use environment variable if available (Vite replaces this at build time)
// Fallback to Render backend if not set
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://texas-energy-backend.onrender.com').trim();

console.log('API Base URL:', API_BASE_URL); // Debug log

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Secondary safety: Ensure HTTPS in case CSP doesn't apply
// CSP upgrade-insecure-requests (in index.html) handles this at browser level
api.interceptors.request.use((config) => {
  // Force HTTPS for any HTTP URLs (backup to CSP)
  if (config.baseURL && config.baseURL.startsWith('http://') && !config.baseURL.includes('localhost')) {
    config.baseURL = config.baseURL.replace('http://', 'https://');
  }
  if (config.url && config.url.startsWith('http://') && !config.url.includes('localhost')) {
    config.url = config.url.replace('http://', 'https://');
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

interface Provider {
  id: number;
  name: string;
  website?: string | null;
}

interface Plan {
  id: number;
  provider_id: number;
  plan_name: string;
  plan_url?: string | null;
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
  const res = await api.get<Plan[]>('/plans/', { params });
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

  const apiKey = import.meta.env.VITE_API_KEY;

  const headers: Record<string, string> = {
    'X-API-Key': apiKey,
  };

  const res = await api.post('/plans/scrape', null, { params, headers });
  return res.data;
}