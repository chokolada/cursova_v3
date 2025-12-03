import api from './api';

const roomService = {
  async getAllRooms(params = {}) {
    const response = await api.get('/rooms', { params });
    return response.data;
  },

  async getRoom(id) {
    const response = await api.get(`/rooms/${id}`);
    return response.data;
  },

  async createRoom(roomData) {
    const response = await api.post('/rooms', roomData);
    return response.data;
  },

  async updateRoom(id, roomData) {
    const response = await api.put(`/rooms/${id}`, roomData);
    return response.data;
  },

  async deleteRoom(id) {
    await api.delete(`/rooms/${id}`);
  },
};

export default roomService;
