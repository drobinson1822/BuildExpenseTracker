import { api } from './api';

export const expenseService = {
  async getExpenses(projectId) {
    const response = await api.get('/expenses/', { project_id: projectId });
    return response.data;
  },

  async createExpense(expenseData) {
    const response = await api.post('/expenses/', expenseData);
    return response.data;
  },

  async updateExpense(id, expenseData) {
    const response = await api.put(`/expenses/${id}`, expenseData);
    return response.data;
  },

  async deleteExpense(id) {
    await api.delete(`/expenses/${id}`);
  }
};
