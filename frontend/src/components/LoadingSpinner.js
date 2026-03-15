import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner({ message = 'Fetching rates from all banks...' }) {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p className="spinner-message">{message}</p>
    </div>
  );
}

export default LoadingSpinner;
