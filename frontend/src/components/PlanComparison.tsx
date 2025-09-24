import React from 'react';

// TODO: implement plan comparison with charts.  This component will receive
// an array of plans and render a bar chart (using react-chartjs-2) showing
// effective rates at different usage levels and highlight differences
// against TXU plans.
const PlanComparison: React.FC<{ plans: any[] }> = ({ plans }) => {
  return (
    <div>
      <h2>Comparison</h2>
      <p>Comparison charts will appear here.</p>
    </div>
  );
};

export default PlanComparison;