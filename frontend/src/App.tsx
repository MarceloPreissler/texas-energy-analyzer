import React, { useState, useEffect } from 'react';
import EnhancedPlanList from './components/EnhancedPlanList';
import './App.css';

const App: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    });
  };

  return (
    <div className="app-container">
      <div className="app-header">
        <h1>⚡ Texas Commercial Energy Market Analyzer</h1>
        <p>Compare ERCOT Retail Electricity Providers & Find the Best Rates</p>
      </div>

      <div className="timestamp">
        Last Updated: {formatTime(currentTime)}
        <span className="status-indicator"></span>
      </div>

      <div className="info-box">
        <h3>📊 About This Data</h3>
        <p>
          <strong>Data Source:</strong> Plans are scraped from public comparison websites including PowerChoiceTexas.org.
          Rates shown are for informational purposes and represent snapshot data from recent scraping runs.
        </p>
        <p style={{ marginTop: '10px' }}>
          <strong>⚠️ Important:</strong> This is NOT live real-time pricing. For the most current rates,
          always verify directly with providers or visit{' '}
          <a href="https://www.powertochoose.org" target="_blank" rel="noopener noreferrer" style={{ color: '#2c5364' }}>
            PowerToChoose.org
          </a>
          {' '}(the official PUCT comparison site).
        </p>
      </div>

      <EnhancedPlanList />
    </div>
  );
};

export default App;