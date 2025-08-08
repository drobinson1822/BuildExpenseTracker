// src/api.js
// Basic API utility for backend interaction

const API_BASE = 'http://localhost:8000/api';

// Create or update an ActualExpense
export async function createOrUpdateExpense(expense, id) {
  const method = id ? 'PUT' : 'POST';
  const url = id ? `${API_BASE}/expenses/${id}` : `${API_BASE}/expenses/`;
  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(expense),
  });
  if (!res.ok) throw new Error('Failed to save expense');
  return res.json();
}

export async function createProject(project) {
  const res = await fetch(`${API_BASE}/projects/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(project),
  });
  if (!res.ok) throw new Error('Failed to create project');
  return res.json();
}

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/projects/`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchProject(id) {
  const res = await fetch(`${API_BASE}/projects/${id}`);
  if (!res.ok) throw new Error('Failed to fetch project');
  return res.json();
}

export async function fetchForecastItems() {
  const res = await fetch(`${API_BASE}/forecast-items/`);
  if (!res.ok) throw new Error('Failed to fetch forecast items');
  return res.json();
}

export async function fetchExpenses() {
  const res = await fetch(`${API_BASE}/expenses/`);
  if (!res.ok) throw new Error('Failed to fetch expenses');
  return res.json();
}
