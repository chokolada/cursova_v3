import api from './api';

const bookingService = {
  async getMyBookings() {
    const response = await api.get('/bookings/my');
    return response.data;
  },

  async getAllBookings() {
    const response = await api.get('/bookings/all');
    return response.data;
  },

  async getBooking(id) {
    const response = await api.get(`/bookings/${id}`);
    return response.data;
  },

  async createBooking(bookingData) {
    const response = await api.post('/bookings', bookingData);
    return response.data;
  },

  async updateBooking(id, bookingData) {
    const response = await api.put(`/bookings/${id}`, bookingData);
    return response.data;
  },

  async cancelBooking(id) {
    const response = await api.post(`/bookings/${id}/cancel`);
    return response.data;
  },

  async deleteBooking(id) {
    await api.delete(`/bookings/${id}`);
  },

  async getRoomBookedDates(roomId, startDate, endDate) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get(`/bookings/room/${roomId}/booked-dates`, { params });
    return response.data;
  },
};

export default bookingService;
