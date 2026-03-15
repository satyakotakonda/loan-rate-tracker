import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchAllRates = (params = {}) =>
  api.get('/rates', { params }).then((r) => r.data);

export const fetchPersonalLoanRates = () =>
  api.get('/rates/personal-loan').then((r) => r.data);

export const fetchHomeLoanRates = () =>
  api.get('/rates/home-loan').then((r) => r.data);

export const fetchBestRates = () =>
  api.get('/rates/best').then((r) => r.data);

export const fetchBankRates = (bankName) =>
  api.get(`/rates/bank/${encodeURIComponent(bankName)}`).then((r) => r.data);

export const fetchRBIBenchmark = () =>
  api.get('/rbi/benchmark').then((r) => r.data);

export const calculateEMI = (payload) =>
  api.post('/calculator/emi', payload).then((r) => r.data);

export const refreshRates = () =>
  api.post('/rates/refresh').then((r) => r.data);

export default api;
