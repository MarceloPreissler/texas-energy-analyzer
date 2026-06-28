// Vercel serverless function: ERCOT grid summary proxy.
//
// Why this exists: ERCOT's public dashboard JSON APIs only allow CORS from
// mis.ercot.com, so the browser cannot fetch them directly. This function runs
// server-side (no CORS restriction) and reshapes the live ERCOT feeds into the
// { grid_status, fuel_mix, zone_prices } payload the dashboard expects.
//
// It deliberately does NOT depend on the Render backend, so live grid data keeps
// working regardless of the backend's deploy state.

const ERCOT_HEADERS = { 'User-Agent': 'TexasEnergyAnalyzer/1.0' };
const SUPPLY_DEMAND_URL =
  'https://www.ercot.com/api/1/services/read/dashboards/supply-demand.json';
const FUEL_MIX_URL =
  'https://www.ercot.com/api/1/services/read/dashboards/fuel-mix.json';
const PRICES_URL =
  'https://www.ercot.com/api/1/services/read/dashboards/system-wide-prices.json';

const round = (n, d = 1) => {
  const f = Math.pow(10, d);
  return Math.round((Number(n) || 0) * f) / f;
};

async function fetchJson(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const res = await fetch(url, { headers: ERCOT_HEADERS, signal: controller.signal });
    if (!res.ok) throw new Error(`ERCOT ${url} -> ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

function parseSupplyDemand(data) {
  const records = (data && data.data) || [];
  // Prefer the most recent actual (non-forecast) reading.
  let current = null;
  for (let i = records.length - 1; i >= 0; i--) {
    if ((records[i].forecast || 0) === 0) {
      current = records[i];
      break;
    }
  }
  if (!current) current = records[records.length - 1] || {};

  const capacity = Number(current.capacity || 0);
  const demand = Number(current.demand || 0);
  const available = capacity - demand;
  const margin = capacity > 0 ? (available / capacity) * 100 : 0;

  return {
    timestamp: String(current.timestamp || new Date().toISOString()),
    current_demand_mw: round(demand),
    total_capacity_mw: round(capacity),
    available_reserve_mw: round(available),
    reserve_margin_percent: round(margin),
  };
}

function parseFuelMix(data) {
  // Structure: data.data[YYYY-MM-DD][timestamp][FuelName] = { gen: MW }
  const byDate = (data && data.data) || {};
  const dateKeys = Object.keys(byDate).sort();
  const latestDate = dateKeys[dateKeys.length - 1];
  const dayData = (latestDate && byDate[latestDate]) || {};
  const tsKeys = Object.keys(dayData).sort();
  const latestTs = tsKeys[tsKeys.length - 1];
  const fuels = (latestTs && dayData[latestTs]) || {};

  const gen = (name) => Number((fuels[name] && fuels[name].gen) || 0);

  const wind = gen('Wind');
  const solar = gen('Solar');
  const gas = gen('Natural Gas');
  const coal = gen('Coal and Lignite');
  const nuclear = gen('Nuclear');
  const hydro = gen('Hydro');
  const storage = gen('Power Storage');
  const other = gen('Other');

  const total = wind + solar + gas + coal + nuclear + hydro + Math.max(0, storage) + other;
  const renewable = wind + solar + hydro;
  const renewablePct = total > 0 ? (renewable / total) * 100 : 0;

  return {
    timestamp: new Date().toISOString(),
    wind_mw: round(wind),
    solar_mw: round(solar),
    natural_gas_mw: round(gas),
    coal_mw: round(coal),
    nuclear_mw: round(nuclear),
    hydro_mw: round(hydro),
    storage_mw: round(storage),
    other_mw: round(other),
    total_mw: round(total),
    renewable_percent: round(renewablePct),
  };
}

function parsePrices(data) {
  const rt = (data && data.rtSppData) || [];
  const latest = rt[rt.length - 1] || {};
  const p = (v) => round(v, 2);
  return {
    timestamp: String(latest.timestamp || new Date().toISOString()),
    lz_houston: p(latest.lzHouston),
    lz_north: p(latest.lzNorth),
    lz_south: p(latest.lzSouth),
    lz_west: p(latest.lzWest),
    hub_houston: p(latest.hbHouston),
    hub_north: p(latest.hbNorth),
    hub_west: p(latest.hbWest),
    hub_average: p(latest.hbHubAvg),
  };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');

  try {
    const [supplyDemand, fuelMix, prices] = await Promise.all([
      fetchJson(SUPPLY_DEMAND_URL),
      fetchJson(FUEL_MIX_URL),
      fetchJson(PRICES_URL),
    ]);

    return res.status(200).json({
      grid_status: parseSupplyDemand(supplyDemand),
      fuel_mix: parseFuelMix(fuelMix),
      zone_prices: parsePrices(prices),
      last_updated: new Date().toISOString(),
      data_source: 'ERCOT Public API (ercot.com)',
    });
  } catch (err) {
    return res.status(502).json({ error: String(err && err.message ? err.message : err) });
  }
}
