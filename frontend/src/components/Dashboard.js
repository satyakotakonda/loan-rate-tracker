import React, { useState, useMemo } from 'react';
import { formatRate, formatDate, getRateClass } from '../utils/formatters';
import LoadingSpinner from './LoadingSpinner';
import LoanTypeFilter from './LoanTypeFilter';
import BankFilter from './BankFilter';
import RateCard from './RateCard';
import RateTable from './RateTable';
import RateChart from './RateChart';
import LoanCalculator from './LoanCalculator';
import './Dashboard.css';

function StatCard({ icon, label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-body">
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
        {sub && <div className="stat-sub">{sub}</div>}
      </div>
    </div>
  );
}

function Dashboard({ rates, rbiData, bestRates, loading, error, lastRefreshed }) {
  const [loanType, setLoanType] = useState('');
  const [bankFilter, setBankFilter] = useState('');
  const [view, setView] = useState('cards'); // 'cards' | 'table' | 'chart' | 'calculator'

  const uniqueBanks = useMemo(
    () => [...new Set(rates.map((r) => r.bank_name))].sort(),
    [rates]
  );

  const filtered = useMemo(() => {
    return rates.filter((r) => {
      if (loanType && r.loan_type !== loanType) return false;
      if (bankFilter && r.bank_name !== bankFilter) return false;
      return true;
    });
  }, [rates, loanType, bankFilter]);

  const totalBanks = uniqueBanks.length;

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="error-banner">
        <span>⚠️ {error}</span>
      </div>
    );
  }

  return (
    <main className="dashboard">
      {/* Overview Stats */}
      <section className="stats-row">
        <StatCard
          icon="🏦"
          label="Banks Tracked"
          value={totalBanks}
          sub="Major Indian banks"
        />
        <StatCard
          icon="💼"
          label="Best Personal Loan"
          value={bestRates?.best_personal_loan ? formatRate(bestRates.best_personal_loan.interest_rate_min) : 'N/A'}
          sub={bestRates?.best_personal_loan?.bank_name}
        />
        <StatCard
          icon="🏠"
          label="Best Home Loan"
          value={bestRates?.best_home_loan ? formatRate(bestRates.best_home_loan.interest_rate_min) : 'N/A'}
          sub={bestRates?.best_home_loan?.bank_name}
        />
        {rbiData && (
          <StatCard
            icon="📊"
            label="RBI Repo Rate"
            value={formatRate(rbiData.repo_rate)}
            sub="RBI Benchmark"
          />
        )}
        {lastRefreshed && (
          <StatCard
            icon="🕐"
            label="Last Updated"
            value={formatDate(lastRefreshed).split(',')[0]}
            sub={formatDate(lastRefreshed).split(',').slice(1).join(',')}
          />
        )}
      </section>

      {/* RBI Benchmark */}
      {rbiData && (
        <section className="rbi-section">
          <h2 className="section-title">📊 RBI Benchmark Rates</h2>
          <div className="rbi-grid">
            <div className="rbi-item">
              <div className="rbi-rate">{formatRate(rbiData.repo_rate)}</div>
              <div className="rbi-label">Repo Rate</div>
              <div className="rbi-desc">Rate at which RBI lends to banks</div>
            </div>
            <div className="rbi-item">
              <div className="rbi-rate">{formatRate(rbiData.reverse_repo_rate)}</div>
              <div className="rbi-label">Reverse Repo Rate</div>
              <div className="rbi-desc">Rate at which RBI borrows from banks</div>
            </div>
            <div className="rbi-item">
              <div className="rbi-rate">{formatRate(rbiData.bank_rate)}</div>
              <div className="rbi-label">Bank Rate</div>
              <div className="rbi-desc">Long-term lending rate by RBI</div>
            </div>
            <div className="rbi-item">
              <div className="rbi-rate">{formatRate(rbiData.marginal_standing_facility_rate)}</div>
              <div className="rbi-label">MSF Rate</div>
              <div className="rbi-desc">Marginal Standing Facility Rate</div>
            </div>
          </div>
          <p className="rbi-note">
            💡 <strong>Note:</strong> Home loan rates are typically linked to the Repo Rate (EBLR).
            A lower Repo Rate generally means cheaper home loans.
          </p>
        </section>
      )}

      {/* Filters & View Toggle */}
      <section className="filter-bar">
        <div className="filters">
          <LoanTypeFilter value={loanType} onChange={setLoanType} />
          <BankFilter banks={uniqueBanks} value={bankFilter} onChange={setBankFilter} />
        </div>
        <div className="view-toggle">
          {['cards', 'table', 'chart', 'calculator'].map((v) => (
            <button
              key={v}
              className={`view-btn ${view === v ? 'active' : ''}`}
              onClick={() => setView(v)}
            >
              {v === 'cards' && '🃏 Cards'}
              {v === 'table' && '📋 Table'}
              {v === 'chart' && '📈 Chart'}
              {v === 'calculator' && '🧮 Calculator'}
            </button>
          ))}
        </div>
      </section>

      {/* Main Content */}
      <section className="main-content">
        {view === 'cards' && (
          <>
            <h2 className="section-title">
              Interest Rates — {filtered.length} result{filtered.length !== 1 ? 's' : ''}
            </h2>
            <div className="cards-grid">
              {filtered.map((rate, idx) => (
                <RateCard
                  key={idx}
                  rate={rate}
                  rateClass={getRateClass(rate.interest_rate_min, filtered)}
                />
              ))}
              {filtered.length === 0 && (
                <p className="no-results">No rates found for the selected filters.</p>
              )}
            </div>
          </>
        )}

        {view === 'table' && (
          <>
            <h2 className="section-title">Rate Comparison Table</h2>
            <RateTable rates={filtered} />
          </>
        )}

        {view === 'chart' && (
          <>
            <h2 className="section-title">Rate Comparison Chart</h2>
            <RateChart rates={rates} loanType={loanType} />
          </>
        )}

        {view === 'calculator' && (
          <>
            <h2 className="section-title">EMI Calculator</h2>
            <LoanCalculator rates={rates} />
          </>
        )}
      </section>
    </main>
  );
}

export default Dashboard;
