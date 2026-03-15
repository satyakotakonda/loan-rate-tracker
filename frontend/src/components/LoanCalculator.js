import React, { useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { calculateEMI } from '../services/api';
import { formatCurrency, formatRate } from '../utils/formatters';
import './LoanCalculator.css';

const COLORS = ['#1a237e', '#e53935'];

function LoanCalculator({ rates }) {
  const [principal, setPrincipal] = useState('');
  const [rate, setRate] = useState('');
  const [tenure, setTenure] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedBank, setSelectedBank] = useState('');

  const uniqueBanks = rates
    ? [...new Set(rates.map((r) => `${r.bank_name} (${r.loan_type === 'home' ? '🏠' : '💼'} ${r.interest_rate_min}%)`))]
    : [];

  const handleBankSelect = (e) => {
    const val = e.target.value;
    setSelectedBank(val);
    if (val) {
      const idx = rates.findIndex(
        (r) => `${r.bank_name} (${r.loan_type === 'home' ? '🏠' : '💼'} ${r.interest_rate_min}%)` === val
      );
      if (idx !== -1) setRate(String(rates[idx].interest_rate_min));
    }
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!principal || !rate || !tenure) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    try {
      const data = await calculateEMI({
        principal: parseFloat(principal),
        rate: parseFloat(rate),
        tenure: parseInt(tenure, 10),
      });
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Calculation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const pieData = result
    ? [
        { name: 'Principal', value: result.principal },
        { name: 'Total Interest', value: result.total_interest },
      ]
    : [];

  return (
    <div className="calculator-container">
      <form className="calculator-form" onSubmit={handleCalculate}>
        <div className="calc-field">
          <label>Select Bank & Rate (optional)</label>
          <select value={selectedBank} onChange={handleBankSelect} className="calc-select">
            <option value="">— Pick a bank to auto-fill rate —</option>
            {uniqueBanks.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        <div className="calc-row">
          <div className="calc-field">
            <label>Loan Amount (₹)</label>
            <input
              type="number"
              placeholder="e.g. 1000000"
              value={principal}
              onChange={(e) => setPrincipal(e.target.value)}
              min="1"
              className="calc-input"
            />
          </div>
          <div className="calc-field">
            <label>Annual Interest Rate (%)</label>
            <input
              type="number"
              step="0.01"
              placeholder="e.g. 8.50"
              value={rate}
              onChange={(e) => setRate(e.target.value)}
              min="0.01"
              className="calc-input"
            />
          </div>
          <div className="calc-field">
            <label>Tenure (Months)</label>
            <input
              type="number"
              placeholder="e.g. 240"
              value={tenure}
              onChange={(e) => setTenure(e.target.value)}
              min="1"
              className="calc-input"
            />
          </div>
        </div>

        {error && <p className="calc-error">{error}</p>}

        <button type="submit" className="calc-btn" disabled={loading}>
          {loading ? 'Calculating...' : '📊 Calculate EMI'}
        </button>
      </form>

      {result && (
        <div className="calc-result">
          <div className="result-cards">
            <div className="result-card highlight">
              <div className="result-label">Monthly EMI</div>
              <div className="result-value">{formatCurrency(result.emi)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">Total Interest</div>
              <div className="result-value interest">{formatCurrency(result.total_interest)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">Total Payment</div>
              <div className="result-value">{formatCurrency(result.total_payment)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">Interest Rate</div>
              <div className="result-value">{formatRate(result.rate)} p.a.</div>
            </div>
          </div>

          <div className="pie-section">
            <h4 className="pie-title">Payment Breakdown</h4>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={95}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                  labelLine={false}
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => formatCurrency(val)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export default LoanCalculator;
