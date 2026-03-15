export const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return 'N/A';
  if (amount >= 10_000_000) return `₹${(amount / 10_000_000).toFixed(1)} Cr`;
  if (amount >= 100_000) return `₹${(amount / 100_000).toFixed(1)} L`;
  return `₹${amount.toLocaleString('en-IN')}`;
};

export const formatRate = (rate) => {
  if (!rate && rate !== 0) return 'N/A';
  return `${rate.toFixed(2)}%`;
};

export const formatTenure = (months) => {
  if (!months) return 'N/A';
  const years = Math.floor(months / 12);
  const rem = months % 12;
  if (years && rem) return `${years}Y ${rem}M`;
  if (years) return `${years} Years`;
  return `${rem} Months`;
};

export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getRateClass = (rate, allRates) => {
  if (!allRates || allRates.length === 0) return 'rate-average';
  const sorted = [...allRates].sort((a, b) => a.interest_rate_min - b.interest_rate_min);
  const third = Math.floor(sorted.length / 3);
  const lowThreshold = sorted[third]?.interest_rate_min;
  const highThreshold = sorted[sorted.length - 1 - third]?.interest_rate_min;
  if (rate <= lowThreshold) return 'rate-best';
  if (rate >= highThreshold) return 'rate-high';
  return 'rate-average';
};
