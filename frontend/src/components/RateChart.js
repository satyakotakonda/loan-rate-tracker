import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './RateChart.css';

function RateChart({ rates, loanType }) {
  const filtered = rates.filter((r) => !loanType || r.loan_type === loanType);

  const bankMap = {};
  filtered.forEach((r) => {
    if (!bankMap[r.bank_name]) {
      bankMap[r.bank_name] = { bank: r.bank_name.replace(' Bank', '').replace(' Mahindra', '') };
    }
    if (r.loan_type === 'personal') {
      bankMap[r.bank_name].personal_min = r.interest_rate_min;
      bankMap[r.bank_name].personal_max = r.interest_rate_max;
    } else if (r.loan_type === 'home') {
      bankMap[r.bank_name].home_min = r.interest_rate_min;
      bankMap[r.bank_name].home_max = r.interest_rate_max;
    }
  });

  const data = Object.values(bankMap);

  const showPersonal = !loanType || loanType === 'personal';
  const showHome = !loanType || loanType === 'home';

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((p) => (
            <p key={p.name} style={{ color: p.color }}>
              {p.name}: <strong>{p.value?.toFixed(2)}%</strong>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (!data.length) return null;

  return (
    <div className="chart-wrapper">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="bank" tick={{ fontSize: 11 }} />
          <YAxis
            domain={[6, 'auto']}
            tick={{ fontSize: 11 }}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {showPersonal && (
            <Bar dataKey="personal_min" name="Personal (Min %)" fill="#3949ab" radius={[3, 3, 0, 0]} />
          )}
          {showPersonal && (
            <Bar dataKey="personal_max" name="Personal (Max %)" fill="#7986cb" radius={[3, 3, 0, 0]} />
          )}
          {showHome && (
            <Bar dataKey="home_min" name="Home (Min %)" fill="#2e7d32" radius={[3, 3, 0, 0]} />
          )}
          {showHome && (
            <Bar dataKey="home_max" name="Home (Max %)" fill="#81c784" radius={[3, 3, 0, 0]} />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RateChart;
