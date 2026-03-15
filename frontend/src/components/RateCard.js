import React from 'react';
import { formatCurrency, formatRate, formatTenure } from '../utils/formatters';
import './RateCard.css';

const RATE_LABELS = { personal: 'Personal Loan', home: 'Home Loan' };
const RATE_ICONS = { personal: '💼', home: '🏠' };

function RateCard({ rate, rateClass }) {
  return (
    <div className={`rate-card ${rateClass || ''}`}>
      <div className="rate-card-header">
        <div className="bank-info">
          <span className="loan-icon">{RATE_ICONS[rate.loan_type] || '🏦'}</span>
          <div>
            <h3 className="bank-name">{rate.bank_name}</h3>
            <span className="loan-type-badge">{RATE_LABELS[rate.loan_type] || rate.loan_type}</span>
          </div>
        </div>
        <div className="rate-display">
          <span className="rate-min">{formatRate(rate.interest_rate_min)}</span>
          <span className="rate-sep"> – </span>
          <span className="rate-max">{formatRate(rate.interest_rate_max)}</span>
          <div className="rate-label">p.a.</div>
        </div>
      </div>

      <div className="rate-card-body">
        <div className="detail-row">
          <span className="detail-label">Processing Fee</span>
          <span className="detail-value">{rate.processing_fee || 'N/A'}</span>
        </div>
        <div className="detail-grid">
          <div className="detail-item">
            <span className="detail-label">Min Amount</span>
            <span className="detail-value">{formatCurrency(rate.loan_amount_min)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Max Amount</span>
            <span className="detail-value">{formatCurrency(rate.loan_amount_max)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Min Tenure</span>
            <span className="detail-value">{formatTenure(rate.tenure_min)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Max Tenure</span>
            <span className="detail-value">{formatTenure(rate.tenure_max)}</span>
          </div>
        </div>
        <div className="rate-footer">
          <span className={`rate-type-badge ${rate.rate_type}`}>{rate.rate_type}</span>
          {rate.source_url && (
            <a
              href={rate.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
            >
              View Details ↗
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default RateCard;
