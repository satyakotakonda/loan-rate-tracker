import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p className="footer-text">
          🏦 <strong>Loan Rate Tracker</strong> — Data sourced from official bank websites and RBI.
          Rates are indicative and subject to change. Verify with your bank before applying.
        </p>
        <p className="footer-note">
          © {new Date().getFullYear()} Loan Rate Tracker · MIT License · Built with FastAPI & React
        </p>
      </div>
    </footer>
  );
}

export default Footer;
