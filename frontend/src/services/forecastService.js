import { api } from './api';

export const forecastService = {
  async getForecastItems(projectId) {
    const response = await api.get('/forecast-items/', { project_id: projectId });
    return response.data;
  },

  async createForecastItem(itemData) {
    const response = await api.post('/forecast-items/', itemData);
    return response.data;
  },

  async updateForecastItem(id, itemData) {
    const response = await api.put(`/forecast-items/${id}`, itemData);
    return response.data;
  },

  async deleteForecastItem(id) {
    await api.delete(`/forecast-items/${id}`);
  }
};
