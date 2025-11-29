import React, { useState } from 'react';
import EnhancedPlanList from './components/EnhancedPlanList';
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
        <h1>⚡ Texas Energy Market Analyzer</h1>
        <p>Internal Tool for Tracking, Comparing, and Analyzing Electricity Rates from ERCOT Energy Providers</p>
      </div>

      <div className="timestamp">
        Data Last Refreshed: {formatTime(lastRefresh)}
        <span className="status-indicator"></span>
      </div>

      <div className="info-box">
        <h3>📊 About This Data</h3>
        <p>
          <strong>Data Sources:</strong>
        </p>
        <ul className="data-source-list">
          <li>
            <a href="https://www.powertochoose.org" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
              PowerToChoose.org (PUCT official feed)
            </a>
            {' '}via the public API + HTML fallback so every plan listed for a ZIP comes directly from the regulator's disclosure site.
          </li>
          <li>
            <a href="https://www.energybot.com" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
              EnergyBot.com
            </a>
            {' '}for additional commercial comparison data used to cross-check offer details.
          </li>
        </ul>
        <p className="data-integrity-note">
          Every field displayed is scraped straight from these live sources—no placeholder, assumed, or fabricated values are inserted by the tool.
        </p>
        <p style={{ marginTop: '10px' }}>
          <strong>✅ Data Freshness:</strong> Plans shown reflect current offerings from multiple Texas electricity comparison sites.
          However, rates can change frequently.
        </p>
        <p style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #e0e0e0' }}>
          <strong>📋 Disclosure:</strong> This tool was created for analysis and informational purposes to assess
          the most current information in the energy market efficiently and effectively. For enrollment and final
          rate verification, please contact providers directly or visit their official websites.
        </p>
        <p style={{ marginTop: '15px', fontSize: '0.75em', color: '#999', fontStyle: 'italic' }}>
          Created by Marcelo Preissler and Claude Code
        </p>
      </div>

      <EnhancedPlanList onRefresh={handleRefresh} />
    </div>
  );
};

export default App;