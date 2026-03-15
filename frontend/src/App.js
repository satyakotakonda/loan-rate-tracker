import React from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Footer from './components/Footer';
import { useLoanRates } from './hooks/useLoanRates';
import './App.css';

function App() {
  const { rates, rbiData, bestRates, loading, error, lastRefreshed, reload } = useLoanRates();

  return (
    <div className="app">
      <Header onRefresh={reload} loading={loading} />
      <Dashboard
        rates={rates}
        rbiData={rbiData}
        bestRates={bestRates}
        loading={loading}
        error={error}
        lastRefreshed={lastRefreshed}
      />
      <Footer />
    </div>
  );
}

export default App;
