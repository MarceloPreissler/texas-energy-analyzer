import React, { useState, useEffect } from 'react';
import EnhancedPlanList from './components/EnhancedPlanList';
import './App.css';

const App: React.FC = () => {
  const [lastRefresh] = useState(new Date());

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
          <strong>Data Sources:</strong> Plans are aggregated from multiple trusted sources including{' '}
          <a href="https://www.powerchoicetexas.org" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
            PowerChoiceTexas.org
          </a>
          {' '}comparison sites for residential plans and{' '}
          <a href="https://www.energybot.com" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
            EnergyBot.com
          </a>
          {' '}for commercial plans. Data is automatically refreshed daily at 2:00 AM,
          and you can manually refresh anytime using the "Refresh Data" button.
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

      <EnhancedPlanList />
    </div>
  );
};

export default App;