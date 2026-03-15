import React from 'react';
import './BankFilter.css';

function BankFilter({ banks, value, onChange }) {
  return (
    <div className="bank-filter">
      <select
        className="bank-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All Banks</option>
        {banks.map((bank) => (
          <option key={bank} value={bank}>
            {bank}
          </option>
        ))}
      </select>
    </div>
  );
}

export default BankFilter;
