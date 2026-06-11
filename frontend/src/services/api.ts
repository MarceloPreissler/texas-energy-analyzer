import axios from 'axios';

// Detect environment and set appropriate API base URL
const hostname = window.location.hostname;
const protocol = window.location.protocol;

// Allow explicit overrides before running environment heuristics.
// Accept both VITE_API_BASE_URL and VITE_API_URL (the name used in .env.production
// and vercel.json) so a naming mismatch can never silently fall through.
const envApiBaseUrl = (
  (import.meta as any)?.env?.VITE_API_BASE_URL ||
  (import.meta as any)?.env?.VITE_API_URL ||
  ''
).trim();
const windowApiOverride = (window as any)?.__API_BASE_URL;

// More robust environment detection
const isNgrok = hostname.includes('ngrok');
const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '10.0.0.16';
const isVercelPreview = hostname.includes('vercel.app');
const isCustomDomain = hostname === 'texasenergyanalyzer.com' || hostname === 'www.texasenergyanalyzer.com';
const isProduction = isCustomDomain || isVercelPreview || (!isLocalhost && !isNgrok && protocol === 'https:');

// API base URL logic - explicit and clear
let API_BASE_URL: string;
if (envApiBaseUrl) {
  API_BASE_URL = envApiBaseUrl;
} else if (windowApiOverride) {
  API_BASE_URL = windowApiOverride;
} else if (isProduction || isVercelPreview || isCustomDomain) {
  // Production: Use Render backend (Railway deployment is retired)
  API_BASE_URL = 'https://texas-energy-backend.onrender.com';
} else if (isNgrok) {
  // Ngrok tunnel: use local backend
  API_BASE_URL = 'http://10.0.0.16:8000';
} else if (isLocalhost) {
  // Localhost: use Vite proxy
  API_BASE_URL = '';
} else {
  // Fallback: if we can't detect, assume production and use Render
  console.warn('Unable to detect environment, defaulting to production Render backend');
  API_BASE_URL = 'https://texas-energy-backend.onrender.com';
}

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
  rate_500_cents?: number | null;
  rate_1000_cents?: number | null;
  rate_2000_cents?: number | null;
  monthly_bill_1000?: number | null;
  monthly_bill_2000?: number | null;
  early_termination_fee?: number | null;
  cancellation_fee?: number | null;
  base_monthly_fee?: number | null;
  renewable_percent?: number | null;
  special_features?: string | null;
  rate_start_date?: string | null;
  last_updated?: string | null;
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
  contractMonths?: number,
  limit?: number
): Promise<Plan[]> {
  const params: Record<string, string | number> = {};
  if (provider) params.provider = provider;
  if (planType) params.plan_type = planType;
  if (serviceType) params.service_type = serviceType;
  if (zipCode) params.zip_code = zipCode;
  if (contractMonths) params.contract_months = contractMonths;
  if (limit) params.limit = limit;
  const res = await api.get<Plan[]>('/plans/', { params });
  return res.data;
}

export async function triggerScrape(
  serviceType: string = 'Residential',
  zipCode?: string
): Promise<any> {
  // Use the /plans/refresh endpoint which runs scrape and loads data
  // This is a public endpoint that triggers a comprehensive data refresh
  const res = await api.post('/plans/refresh');
  return res.data;
}

export async function scrapePowerToChoose(zipCode: string) {
  const res = await api.post<{ plans_processed: number; zip_code: string }>(
    '/plans/scrape/powertochoose',
    { zip_code: zipCode }
  );
  return res.data;
}