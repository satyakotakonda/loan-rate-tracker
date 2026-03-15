import { useState, useEffect, useCallback } from 'react';
import { fetchAllRates, fetchRBIBenchmark, fetchBestRates } from '../services/api';

export function useLoanRates() {
  const [rates, setRates] = useState([]);
  const [rbiData, setRbiData] = useState(null);
  const [bestRates, setBestRates] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ratesResp, rbiResp, bestResp] = await Promise.all([
        fetchAllRates(),
        fetchRBIBenchmark(),
        fetchBestRates(),
      ]);
      setRates(ratesResp.data || []);
      setLastRefreshed(ratesResp.last_refreshed);
      setRbiData(rbiResp);
      setBestRates(bestResp);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load loan rates');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return { rates, rbiData, bestRates, loading, error, lastRefreshed, reload: loadData };
}
