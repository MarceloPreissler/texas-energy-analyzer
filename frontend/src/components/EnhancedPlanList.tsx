import React, { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchPlans, fetchProviders, triggerScrape, scrapePowerToChoose } from '../services/api';
import PlanComparison from './PlanComparison';
import PriceAnalytics from './PriceAnalytics';

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
  renewable_percent?: number | null;
  special_features?: string | null;
}

interface Provider {
  id: number;
  name: string;
  website?: string | null;
}

const PAGE_SIZE_OPTIONS = [25, 50, 100];
const SORT_FIELDS = [
  { value: 'rate_1000_cents', label: 'Rate (1,000 kWh)' },
  { value: 'provider', label: 'Provider Name' },
  { value: 'plan_name', label: 'Plan Name' },
  { value: 'contract_months', label: 'Contract Length' },
  { value: 'renewable_percent', label: 'Renewable %' }
] as const;

type SortField = (typeof SORT_FIELDS)[number]['value'];

type SortDirection = 'asc' | 'desc';

const EnhancedPlanList: React.FC = () => {
  const queryClient = useQueryClient();

  const [tempProviderFilter, setTempProviderFilter] = useState('');
  const [tempPlanTypeFilter, setTempPlanTypeFilter] = useState('');
  const [tempServiceTypeFilter, setTempServiceTypeFilter] = useState('Residential');
  const [tempZipCodeFilter, setTempZipCodeFilter] = useState('');
  const [tempContractFilter, setTempContractFilter] = useState('');

  const [providerFilter, setProviderFilter] = useState<string | undefined>(undefined);
  const [planTypeFilter, setPlanTypeFilter] = useState<string | undefined>(undefined);
  const [serviceTypeFilter, setServiceTypeFilter] = useState<string | undefined>('Residential');
  const [zipCodeFilter, setZipCodeFilter] = useState<string | undefined>(undefined);
  const [contractFilter, setContractFilter] = useState<number | undefined>(undefined);

  const [selectedPlans, setSelectedPlans] = useState<Plan[]>([]);
  const [usage, setUsage] = useState(1000);
  const [baseFee, setBaseFee] = useState(9.95);
  const [useCustomBaseFee, setUseCustomBaseFee] = useState(false);

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [zipInput, setZipInput] = useState('75214');
  const [scrapeError, setScrapeError] = useState<string | null>(null);

  const [planNameSearch, setPlanNameSearch] = useState('');
  const [providerSearch, setProviderSearch] = useState('');
  const [minRenewable, setMinRenewable] = useState(0);
  const [sortField, setSortField] = useState<SortField>('rate_1000_cents');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[0]);

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: fetchProviders,
  });

  const { data: plans, isLoading, isError } = useQuery({
    queryKey: ['plans', providerFilter, planTypeFilter, serviceTypeFilter, zipCodeFilter, contractFilter],
    queryFn: () => fetchPlans(providerFilter, planTypeFilter, serviceTypeFilter, zipCodeFilter, contractFilter),
  });

  const handleSearch = () => {
    setProviderFilter(tempProviderFilter || undefined);
    setPlanTypeFilter(tempPlanTypeFilter || undefined);
    setServiceTypeFilter(tempServiceTypeFilter || undefined);
    setZipCodeFilter(tempZipCodeFilter || undefined);
    setContractFilter(tempContractFilter ? Number(tempContractFilter) : undefined);
    setCurrentPage(1);
  };

  const handleReset = () => {
    setTempProviderFilter('');
    setTempPlanTypeFilter('');
    setTempServiceTypeFilter('Residential');
    setTempZipCodeFilter('');
    setTempContractFilter('');
    setProviderFilter(undefined);
    setPlanTypeFilter(undefined);
    setServiceTypeFilter('Residential');
    setZipCodeFilter(undefined);
    setContractFilter(undefined);
    setPlanNameSearch('');
    setProviderSearch('');
    setMinRenewable(0);
    setCurrentPage(1);
  };

  const handleRefreshData = async () => {
    setIsRefreshing(true);
    try {
      await triggerScrape(serviceTypeFilter || 'Residential', zipCodeFilter);
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      alert('Data refresh scheduled.');
    } catch (error) {
      console.error('Error refreshing data:', error);
      alert('Unable to refresh data. Check logs for details.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleViewAllPlans = async () => {
    if (!zipInput || zipInput.length !== 5) {
      setScrapeError('Enter a valid 5-digit Texas ZIP code.');
      return;
    }

    setScrapeError(null);
    setIsScraping(true);
    try {
      await scrapePowerToChoose(zipInput);
      setTempZipCodeFilter(zipInput);
      setZipCodeFilter(zipInput);
      setServiceTypeFilter('Residential');
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      setCurrentPage(1);
    } catch (error) {
      console.error('PowerToChoose scrape failed:', error);
      setScrapeError('Unable to retrieve plans from PowerToChoose. Try again in a few minutes.');
    } finally {
      setIsScraping(false);
    }
  };

  const handleSelect = (plan: Plan) => {
    setSelectedPlans((prev) => {
      if (prev.some((p) => p.id === plan.id)) {
        return prev.filter((p) => p.id !== plan.id);
      }
      if (prev.length >= 5) {
        alert('Select up to 5 plans for comparison.');
        return prev;
      }
      return [...prev, plan];
    });
  };

  const getProviderName = (plan: Plan) => {
    return providers?.find((p) => p.id === plan.provider_id)?.name || 'Unknown';
  };

  const getRateClass = (rate: number | null | undefined) => {
    if (!rate) return '';
    if (rate < 12) return 'rate-good';
    if (rate < 15) return 'rate-warning';
    return 'rate-high';
  };

  const calculateMonthlyCost = (rate: number | null | undefined) => {
    if (!rate) return 0;
    return (usage * rate) / 100 + (useCustomBaseFee ? baseFee : 9.95);
  };

  const processedPlans = useMemo(() => {
    if (!plans) return [];

    const filtered = plans
      .filter((plan) =>
        plan.plan_name.toLowerCase().includes(planNameSearch.toLowerCase())
      )
      .filter((plan) =>
        getProviderName(plan).toLowerCase().includes(providerSearch.toLowerCase())
      )
      .filter((plan) => (minRenewable ? (plan.renewable_percent || 0) >= minRenewable : true));

    const sorted = [...filtered].sort((a, b) => {
      const direction = sortDirection === 'asc' ? 1 : -1;
      switch (sortField) {
        case 'provider':
          return direction * getProviderName(a).localeCompare(getProviderName(b));
        case 'plan_name':
          return direction * a.plan_name.localeCompare(b.plan_name);
        case 'contract_months':
          return direction * ((a.contract_months || 0) - (b.contract_months || 0));
        case 'renewable_percent':
          return direction * ((a.renewable_percent || 0) - (b.renewable_percent || 0));
        default:
          return direction * (((a.rate_1000_cents || 0) - (b.rate_1000_cents || 0)));
      }
    });

    return sorted;
  }, [plans, planNameSearch, providerSearch, minRenewable, sortField, sortDirection, providers]);

  const totalPages = Math.max(1, Math.ceil(processedPlans.length / pageSize));
  const pageStart = (currentPage - 1) * pageSize;
  const paginatedPlans = processedPlans.slice(pageStart, pageStart + pageSize);

  const summaryStats = useMemo(() => {
    if (!processedPlans.length) return null;

    const plansWithRates = processedPlans.filter((p) => p.rate_1000_cents);
    if (!plansWithRates.length) return null;

    const rates = plansWithRates.map((p) => p.rate_1000_cents || 0);
    const lowestRate = Math.min(...rates);
    const highestRate = Math.max(...rates);
    const avgRate = rates.reduce((a, b) => a + b, 0) / rates.length;

    const bestPlan = plansWithRates.find((p) => p.rate_1000_cents === lowestRate);
    const worstPlan = plansWithRates.find((p) => p.rate_1000_cents === highestRate);

    return {
      lowestRate,
      highestRate,
      avgRate: avgRate.toFixed(2),
      bestPlan,
      worstPlan,
      totalPlans: processedPlans.length,
      potentialSavings: calculateMonthlyCost(highestRate) - calculateMonthlyCost(lowestRate),
    };
  }, [processedPlans, usage]);

  const getRecommendations = () => {
    if (!summaryStats) return '';
    const { lowestRate, avgRate, bestPlan, potentialSavings } = summaryStats;
    const providerName = bestPlan ? getProviderName(bestPlan) : 'Unknown provider';

    return `Based on ${summaryStats.totalPlans} plans, the best rate is ${lowestRate.toFixed(1)}¢/kWh from ${providerName} (${bestPlan?.plan_name || 'N/A'}). The market average is ${avgRate}¢/kWh. Switching from the highest-rate plan could save up to $${(potentialSavings * 12).toFixed(0)} per year.`;
  };

  const tableRows = paginatedPlans.map((plan) => {
    const providerName = getProviderName(plan);
    const rowClass = [
      plan.plan_type?.toLowerCase().includes('time') ? 'plan-row time-of-use' : '',
      (plan.renewable_percent || 0) >= 90 ? 'plan-row renewable' : '',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <tr key={plan.id} className={rowClass}>
        <td>
          <input
            type="checkbox"
            checked={selectedPlans.some((p) => p.id === plan.id)}
            onChange={() => handleSelect(plan)}
          />
        </td>
        <td>
          {providers?.find((p) => p.id === plan.provider_id)?.website ? (
            <a
              href={providers?.find((p) => p.id === plan.provider_id)?.website || '#'}
              target="_blank"
              rel="noopener noreferrer"
            >
              {providerName} 🔗
            </a>
          ) : (
            <strong>{providerName}</strong>
          )}
        </td>
        <td>
          {plan.plan_url ? (
            <a href={plan.plan_url} target="_blank" rel="noopener noreferrer">
              {plan.plan_name} 🔗
            </a>
          ) : (
            plan.plan_name
          )}
          {plan.plan_type?.toLowerCase().includes('time') && (
            <span className="tag time">Time-of-Use</span>
          )}
          {(plan.renewable_percent || 0) >= 90 && (
            <span className="tag renewable">High Renewable</span>
          )}
        </td>
        <td>{plan.plan_type || '-'}</td>
        <td>{plan.contract_months ?? '-'}</td>
        <td className={getRateClass(plan.rate_500_cents)}>{plan.rate_500_cents ? `${plan.rate_500_cents.toFixed(2)}¢` : '-'}</td>
        <td className={getRateClass(plan.rate_1000_cents)}>{plan.rate_1000_cents ? `${plan.rate_1000_cents.toFixed(2)}¢` : '-'}</td>
        <td className={getRateClass(plan.rate_2000_cents)}>{plan.rate_2000_cents ? `${plan.rate_2000_cents.toFixed(2)}¢` : '-'}</td>
        <td>{plan.renewable_percent != null ? `${plan.renewable_percent}%` : '-'}</td>
        <td>{plan.cancellation_fee != null ? `$${plan.cancellation_fee.toFixed(0)}` : '-'}</td>
        <td>
          {plan.rate_1000_cents ? `$${calculateMonthlyCost(plan.rate_1000_cents).toFixed(2)}` : '-'}
        </td>
        <td style={{ fontSize: '0.85em' }}>{plan.special_features || '-'}</td>
      </tr>
    );
  });

  if (isLoading) {
    return <div className="card"><div className="loading">Loading plans...</div></div>;
  }

  if (isError) {
    return <div className="card"><div className="error">Unable to load plans.</div></div>;
  }

  const noResultsMessage = processedPlans.length === 0 ? (
    <div className="card warning-card">
      <h3>⚠️ No Plans Found</h3>
      <p>No plans match your filters. Try clearing filters or scraping a fresh ZIP.</p>
    </div>
  ) : null;

  return (
    <>
      {noResultsMessage}

      <div className="dashboard">
        {summaryStats && (
          <>
            <div className="card">
              <h2 className="card-title">📊 Market Overview</h2>
              <div className="summary-stat">
                <div>Lowest Rate</div>
                <strong>{summaryStats.lowestRate.toFixed(1)}¢/kWh</strong>
              </div>
              <div className="summary-stat">
                <div>Average Rate</div>
                <strong>{summaryStats.avgRate}¢/kWh</strong>
              </div>
              <div className="summary-stat">
                <div>Plans Available</div>
                <strong>{summaryStats.totalPlans}</strong>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">💰 Savings Potential</h2>
              <div className="summary-stat">
                <div>Monthly Savings</div>
                <strong>${summaryStats.potentialSavings.toFixed(0)}</strong>
              </div>
              <div className="summary-stat">
                <div>Annual Savings</div>
                <strong>${(summaryStats.potentialSavings * 12).toFixed(0)}</strong>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">🔍 Best Plan</h2>
              <p><strong>Provider:</strong> {summaryStats.bestPlan ? getProviderName(summaryStats.bestPlan) : 'Unknown'}</p>
              <p><strong>Plan:</strong> {summaryStats.bestPlan?.plan_name}</p>
              <p><strong>Rate:</strong> {summaryStats.lowestRate.toFixed(1)}¢/kWh</p>
            </div>
          </>
        )}
      </div>

      <div className="card zip-card">
        <h2 className="card-title">⚡ PowerToChoose Live Import</h2>
        <div className="zip-actions">
          <input
            type="text"
            value={zipInput}
            maxLength={5}
            onChange={(e) => setZipInput(e.target.value)}
            placeholder="Enter Texas ZIP"
          />
          <button onClick={handleViewAllPlans} disabled={isScraping}>
            {isScraping ? 'Importing…' : 'View All Plans'}
          </button>
        </div>
        {scrapeError && <p className="error-text">{scrapeError}</p>}
        <p className="helper-text">
          We use the official PowerToChoose API with a 99,999 plan page size. If the API is unavailable we fall back to HTML scraping and automatically paginate through every result.
        </p>
      </div>

      <div className="card">
        <h2 className="card-title">🔍 Filter Plans</h2>
        <div className="filter-controls">
          <div className="filter-group">
            <label>Service Type</label>
            <select value={tempServiceTypeFilter} onChange={(e) => setTempServiceTypeFilter(e.target.value)}>
              <option value="Residential">Residential</option>
              <option value="Commercial">Commercial</option>
            </select>
          </div>
          <div className="filter-group">
            <label>ZIP Code</label>
            <input value={tempZipCodeFilter} maxLength={5} onChange={(e) => setTempZipCodeFilter(e.target.value)} />
          </div>
          <div className="filter-group">
            <label>Provider</label>
            <select value={tempProviderFilter} onChange={(e) => setTempProviderFilter(e.target.value)}>
              <option value="">All Providers</option>
              {providers?.map((provider) => (
                <option key={provider.id} value={provider.name}>
                  {provider.name}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Plan Type</label>
            <select value={tempPlanTypeFilter} onChange={(e) => setTempPlanTypeFilter(e.target.value)}>
              <option value="">All Types</option>
              <option value="Fixed">Fixed</option>
              <option value="Variable">Variable</option>
              <option value="Time of Use">Time-of-Use</option>
              <option value="Renewable">Renewable</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Contract (months)</label>
            <input type="number" value={tempContractFilter} onChange={(e) => setTempContractFilter(e.target.value)} />
          </div>
        </div>
        <div className="filter-controls">
          <div className="filter-group">
            <label>Search Plan Name</label>
            <input value={planNameSearch} onChange={(e) => setPlanNameSearch(e.target.value)} placeholder="e.g. Saver" />
          </div>
          <div className="filter-group">
            <label>Search Provider</label>
            <input value={providerSearch} onChange={(e) => setProviderSearch(e.target.value)} placeholder="e.g. Reliant" />
          </div>
          <div className="filter-group">
            <label>Minimum Renewable %</label>
            <input type="number" min={0} max={100} value={minRenewable} onChange={(e) => setMinRenewable(Number(e.target.value) || 0)} />
          </div>
          <div className="filter-group">
            <label>Sort By</label>
            <select value={sortField} onChange={(e) => setSortField(e.target.value as SortField)}>
              {SORT_FIELDS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label>Direction</label>
            <select value={sortDirection} onChange={(e) => setSortDirection(e.target.value as SortDirection)}>
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </div>
        </div>
        <div className="filter-buttons">
          <button onClick={handleSearch}>🔍 Apply Filters</button>
          <button onClick={handleReset}>🔄 Reset</button>
          <button onClick={handleRefreshData} disabled={isRefreshing}>
            {isRefreshing ? 'Refreshing…' : '🔄 Refresh Data'}
          </button>
        </div>
        <p className="helper-text">
          Client-side search refines the results returned by the API. After scraping a ZIP you can sort and paginate through every plan (147+ entries in our testing).
        </p>
      </div>

      <div className="card">
        <h2 className="card-title">📋 Available Plans ({processedPlans.length})</h2>
        <div className="pagination-controls">
          <div>
            Page {currentPage} of {totalPages}
          </div>
          <div>
            <button onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage === 1}>
              Prev
            </button>
            <button onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
              Next
            </button>
          </div>
          <div>
            <label>Rows per page</label>
            <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="plans-table">
            <thead>
              <tr>
                <th>Select</th>
                <th>Provider</th>
                <th>Plan</th>
                <th>Type</th>
                <th>Term</th>
                <th>500 kWh</th>
                <th>1,000 kWh</th>
                <th>2,000 kWh</th>
                <th>Renewable</th>
                <th>Cancellation</th>
                <th>Est. Bill</th>
                <th>Features</th>
              </tr>
            </thead>
            <tbody>{tableRows}</tbody>
          </table>
        </div>
        <p className="helper-text">
          *Estimated bill assumes {usage} kWh/month and a base charge of {useCustomBaseFee ? `$${baseFee.toFixed(2)}` : '$9.95'}.
        </p>
      </div>

      {selectedPlans.length > 0 && <PlanComparison plans={selectedPlans} />}

      <div className="card calculator-section">
        <h2 className="card-title">🧮 Cost Calculator</h2>
        <div className="input-group">
          <label>Monthly Usage (kWh)</label>
          <input type="number" value={usage} onChange={(e) => setUsage(Number(e.target.value))} min="0" max="5000" />
        </div>
        <div className="input-group">
          <label>Base Fee Calculation</label>
          <select value={useCustomBaseFee ? 'custom' : 'estimated'} onChange={(e) => setUseCustomBaseFee(e.target.value === 'custom')}>
            <option value="estimated">Estimated ($9.95/month)</option>
            <option value="custom">Custom Base Fee</option>
          </select>
        </div>
        {useCustomBaseFee && (
          <div className="input-group">
            <label>Custom Base Fee ($/month)</label>
            <input type="number" value={baseFee} onChange={(e) => setBaseFee(Number(e.target.value))} min="0" max="50" step="0.01" />
          </div>
        )}
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
              <p className="summary-value">{summaryStats.lowestRate.toFixed(1)}¢</p>
            </div>
            <div className="summary-item">
              <p className="summary-label">Market Average</p>
              <p className="summary-value">{summaryStats.avgRate}¢</p>
            </div>
            <div className="summary-item">
              <p className="summary-label">Potential Savings</p>
              <p className="summary-value">${(summaryStats.potentialSavings * 12).toFixed(0)}/yr</p>
            </div>
          </div>
          <div className="recommendations">
            <h3>💡 Recommendations</h3>
            <p>{getRecommendations()}</p>
          </div>
        </div>
      )}

      {plans && plans.length > 0 && providers && <PriceAnalytics plans={plans} providers={providers} />}
    </>
  );
};

export default EnhancedPlanList;
