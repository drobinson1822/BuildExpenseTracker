// src/api.js
// API utility for backend interaction with authentication

// Prefer Vite env var, fallback to local dev default
const API_BASE = import.meta.env?.VITE_API_BASE || 'http://localhost:8000/api/v1';

// Helper function to get auth headers
function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

// Helper function to handle API responses
async function handleResponse(response) {
  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('Authentication required');
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

// Create or update an ActualExpense
export async function createOrUpdateExpense(expense, id) {
  const method = id ? 'PUT' : 'POST';
  const url = id ? `${API_BASE}/expenses/${id}` : `${API_BASE}/expenses/`;
  const res = await fetch(url, {
    method,
    headers: getAuthHeaders(),
    body: JSON.stringify(expense),
  });
  return handleResponse(res);
}

export async function createProject(project) {
  const res = await fetch(`${API_BASE}/projects/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(project),
  });
  return handleResponse(res);
}

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/projects/`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(res);
}

export async function fetchProject(id) {
  const res = await fetch(`${API_BASE}/projects/${id}`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(res);
}

export async function fetchForecastItems() {
  const res = await fetch(`${API_BASE}/forecast-items/`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(res);
}

export async function fetchExpenses() {
  const res = await fetch(`${API_BASE}/expenses/`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(res);
}

// ---------- Auth ----------
export async function authLogin(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(res);
}

export async function authRegister(email, password, full_name, user_metadata = {}) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, user_metadata: { full_name, ...user_metadata } }),
  });
  return handleResponse(res);
}

// ---------- Forecast Items ----------
export async function createForecastItem(item) {
  const res = await fetch(`${API_BASE}/forecast-items/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(item),
  });
  return handleResponse(res);
}

export async function updateForecastItem(id, item) {
  const res = await fetch(`${API_BASE}/forecast-items/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(item),
  });
  return handleResponse(res);
}

// ---------- Projects ----------
export async function updateProject(projectId, payload) {
  const res = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}
