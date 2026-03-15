import React from 'react';
import './Header.css';

function Header({ onRefresh, loading }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <span className="header-icon">🏦</span>
          <div>
            <h1 className="header-title">Loan Rate Tracker</h1>
            <p className="header-subtitle">Indian Bank Loan Interest Rates — Live Comparison</p>
          </div>
        </div>
        <button
          className="refresh-btn"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh rates from all banks"
        >
          {loading ? '⏳ Loading...' : '🔄 Refresh Rates'}
        </button>
      </div>
    </header>
  );
}

export default Header;
