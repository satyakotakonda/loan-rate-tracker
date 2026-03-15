import React from 'react';
import './LoanTypeFilter.css';

function LoanTypeFilter({ value, onChange }) {
  const options = [
    { label: 'All Loans', value: '' },
    { label: '🏠 Home Loan', value: 'home' },
    { label: '💼 Personal Loan', value: 'personal' },
  ];

  return (
    <div className="loan-type-filter">
      {options.map((opt) => (
        <button
          key={opt.value}
          className={`filter-btn ${value === opt.value ? 'active' : ''}`}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default LoanTypeFilter;
