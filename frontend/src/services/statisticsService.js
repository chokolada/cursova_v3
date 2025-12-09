import api from './api';

const statisticsService = {
  async getDashboardSummary() {
    const response = await api.get('/statistics/dashboard');
    return response.data;
  },

  async getRoomOccupancy() {
    const response = await api.get('/statistics/room-occupancy');
    return response.data;
  },

  async getFinancialMetrics() {
    const response = await api.get('/statistics/financial');
    return response.data;
  },

  async getRegularCustomers() {
    const response = await api.get('/statistics/regular-customers');
    return response.data;
  },
};

export default statisticsService;
