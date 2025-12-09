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

  async getRevenueGraph(period = 'month', days = 30) {
    const response = await api.get('/statistics/graphs/revenue', {
      params: { period, days }
    });
    return response.data;
  },

  async getOccupancyGraph(period = 'month', days = 30) {
    const response = await api.get('/statistics/graphs/occupancy', {
      params: { period, days }
    });
    return response.data;
  },

  async getBookingsStatusGraph(period = 'month', days = 30) {
    const response = await api.get('/statistics/graphs/bookings-status', {
      params: { period, days }
    });
    return response.data;
  },
};

export default statisticsService;
