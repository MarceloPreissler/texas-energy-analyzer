import React, { useState } from 'react';
import EnhancedPlanList from './components/EnhancedPlanList';
import ErcotDashboard from './components/ErcotDashboard';
import './App.css';

const App: React.FC = () => {
  const [lastRefresh, setLastRefresh] = useState(new Date());

  const handleRefresh = (refreshDate: Date) => {
    setLastRefresh(refreshDate);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  return (
    <div className="app-container">
      <div className="app-header">
        <h1>Texas Energy Market Analyzer</h1>
        <p>Professional Analytics for Texas Electricity Markets - Residential & Commercial</p>
      </div>

      <div className="timestamp">
        Data Last Refreshed: {formatTime(lastRefresh)}
        <span className="status-indicator"></span>
      </div>

      {/* ERCOT Real-Time Grid Dashboard */}
      <ErcotDashboard />

      <div className="info-box">
        <h3>Data Sources & Methodology</h3>
        <p>
          <strong>Live Data Sources:</strong>
        </p>
        <ul className="data-source-list">
          <li>
            <a href="https://www.ercot.com" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
              ERCOT.com
            </a>
            {' '}- Real-time grid status, wholesale prices, fuel mix, and demand/capacity data directly from the Electric Reliability Council of Texas public APIs.
          </li>
          <li>
            <a href="https://www.powertochoose.org" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
              PowerToChoose.org
            </a>
            {' '}- Official PUCT (Public Utility Commission of Texas) retail electricity plan database via public API + HTML fallback.
          </li>
          <li>
            <a href="https://www.electricityplans.com" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
              ElectricityPlans.com
            </a>
            {' '}- Commercial electricity rate data for business customers across Texas TDU service areas.
          </li>
        </ul>
        <p className="data-integrity-note">
          All data is sourced directly from official and verified sources. No estimates, mock data, or fabricated values.
        </p>
        <p style={{ marginTop: '10px' }}>
          <strong>Refresh Rate:</strong> ERCOT grid data updates every 5 minutes. Retail plan data reflects current market offerings.
        </p>
        <p style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e0e0e0' }}>
          <strong>Disclosure:</strong> This tool is for analysis and informational purposes. For enrollment and final
          rate verification, contact providers directly or visit their official websites.
        </p>
        <p style={{ marginTop: '15px', fontSize: '0.75em', color: '#999', fontStyle: 'italic' }}>
          Created by Marcelo Preissler with Claude Code
        </p>
      </div>

      <EnhancedPlanList onRefresh={handleRefresh} />
    </div>
  );
};

export default App;