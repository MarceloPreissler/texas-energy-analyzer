import axios from 'axios';

// Detect environment and set appropriate API base URL
const hostname = window.location.hostname;
const protocol = window.location.protocol;

// More robust environment detection
const isNgrok = hostname.includes('ngrok');
const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '10.0.0.16';
const isVercelPreview = hostname.includes('vercel.app');
const isCustomDomain = hostname === 'texasenergyanalyzer.com' || hostname === 'www.texasenergyanalyzer.com';
const isProduction = isCustomDomain || isVercelPreview || (!isLocalhost && !isNgrok && protocol === 'https:');

// API base URL logic - explicit and clear
let API_BASE_URL: string;
if (isProduction || isVercelPreview || isCustomDomain) {
  // Production: Use ngrok tunnel to local backend with REAL DATA
  API_BASE_URL = 'https://joann-granulocytic-decanically.ngrok-free.dev';
} else if (isNgrok) {
  // Ngrok tunnel: use local backend
  API_BASE_URL = 'http://10.0.0.16:8000';
} else if (isLocalhost) {
  // Localhost: use Vite proxy (empty string for relative URLs)
  API_BASE_URL = '';
} else {
  // Fallback: if we can't detect, assume production and use ngrok
  console.warn('Unable to detect environment, defaulting to production ngrok');
  API_BASE_URL = 'https://joann-granulocytic-decanically.ngrok-free.dev';
}

// Environment detection verified - uncomment for debugging if needed
// console.log('API Configuration Debug:', {
//   hostname,
//   protocol,
//   isNgrok,
//   isLocalhost,
//   isVercelPreview,
//   isCustomDomain,
//   isProduction,
//   API_BASE_URL
// });

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Secondary safety: Ensure HTTPS in case CSP doesn't apply
// CSP upgrade-insecure-requests (in index.html) handles this at browser level
api.interceptors.request.use((config) => {
  // Force HTTPS for any HTTP URLs (backup to CSP)
  if (config.baseURL && config.baseURL.startsWith('http://')) {
    config.baseURL = config.baseURL.replace('http://', 'https://');
  }
  if (config.url && config.url.startsWith('http://')) {
    config.url = config.url.replace('http://', 'https://');
  }
  return config;
}, (error) => {
  return Promise.reject(error);
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
  const res = await api.post('/plans/scrape', null, { params });
  return res.data;
}