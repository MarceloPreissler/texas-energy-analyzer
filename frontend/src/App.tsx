import React from 'react';
import PlanList from './components/PlanList';

const App: React.FC = () => {
  return (
    <div style={{ padding: '1rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Texas Commercial Energy Market Analyzer</h1>
      <p>
        Use the filters below to explore electricity plans for small businesses.  Select plans to
        compare and benchmark against TXU Energy.
      </p>
      <PlanList />
    </div>
  );
};

export default App;