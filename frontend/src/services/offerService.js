import api from './api';

const offerService = {
  async getAllOffers() {
    const response = await api.get('/offers');
    return response.data;
  },

  async getActiveOffers() {
    const response = await api.get('/offers/active');
    return response.data;
  },

  async getGlobalOffers() {
    const response = await api.get('/offers/global');
    return response.data;
  },

  async getOffer(id) {
    const response = await api.get(`/offers/${id}`);
    return response.data;
  },

  async createOffer(offerData) {
    const response = await api.post('/offers', offerData);
    return response.data;
  },

  async updateOffer(id, offerData) {
    const response = await api.put(`/offers/${id}`, offerData);
    return response.data;
  },

  async deleteOffer(id) {
    await api.delete(`/offers/${id}`);
  },
};

export default offerService;
