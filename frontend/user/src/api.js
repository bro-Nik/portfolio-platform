import axios from 'axios';

const API_URL = 'http://localhost:8080/portfolios/api';  // Flask-адрес

export const getPortfolios = () => axios.get(`${API_URL}/portfolios`);
export const addPortfolio = (data) => axios.post(`${API_URL}/portfolios`, data);
export const updatePortfolio = (id, data) => axios.put(`${API_URL}/portfolios/${id}`, data);
export const deletePortfolio = (id) => axios.delete(`${API_URL}/portfolios/${id}`);
