import React, { useState } from 'react';
import { formatCurrency, formatRate, formatTenure } from '../utils/formatters';
import './RateTable.css';

const COLUMNS = [
  { key: 'bank_name', label: 'Bank' },
  { key: 'loan_type', label: 'Type' },
  { key: 'interest_rate_min', label: 'Rate (Min)' },
  { key: 'interest_rate_max', label: 'Rate (Max)' },
  { key: 'processing_fee', label: 'Processing Fee' },
  { key: 'loan_amount_min', label: 'Amount Range' },
  { key: 'tenure_min', label: 'Tenure Range' },
  { key: 'rate_type', label: 'Rate Type' },
];

function RateTable({ rates }) {
  const [sortKey, setSortKey] = useState('interest_rate_min');
  const [sortDir, setSortDir] = useState('asc');

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sorted = [...rates].sort((a, b) => {
    const aVal = a[sortKey] ?? '';
    const bVal = b[sortKey] ?? '';
    if (typeof aVal === 'number') {
      return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
    }
    return sortDir === 'asc'
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal));
  });

  if (!rates || rates.length === 0) {
    return <p className="no-data">No rates found for the selected filters.</p>;
  }

  return (
    <div className="table-wrapper">
      <table className="rate-table">
        <thead>
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                className={`sortable ${sortKey === col.key ? 'active' : ''}`}
              >
                {col.label}
                <span className="sort-icon">
                  {sortKey === col.key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : ' ↕'}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((rate, idx) => (
            <tr key={idx} className={rate.loan_type}>
              <td className="bank-cell">
                <strong>{rate.bank_name}</strong>
              </td>
              <td>
                <span className={`type-pill ${rate.loan_type}`}>
                  {rate.loan_type === 'home' ? '🏠 Home' : '💼 Personal'}
                </span>
              </td>
              <td className="rate-cell green">{formatRate(rate.interest_rate_min)}</td>
              <td className="rate-cell">{formatRate(rate.interest_rate_max)}</td>
              <td className="fee-cell">{rate.processing_fee || 'N/A'}</td>
              <td>
                {formatCurrency(rate.loan_amount_min)} – {formatCurrency(rate.loan_amount_max)}
              </td>
              <td>
                {formatTenure(rate.tenure_min)} – {formatTenure(rate.tenure_max)}
              </td>
              <td>
                <span className={`type-pill rate-type ${rate.rate_type}`}>{rate.rate_type}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default RateTable;
