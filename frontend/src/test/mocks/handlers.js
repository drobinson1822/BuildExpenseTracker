import { http, HttpResponse } from 'msw'

const API_BASE = 'http://localhost:8000/api/v1'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE}/auth/login`, () => {
    return HttpResponse.json({
      access_token: 'mock-token',
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User'
      }
    })
  }),

  http.post(`${API_BASE}/auth/register`, () => {
    return HttpResponse.json({
      access_token: 'mock-token',
      user: {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User'
      }
    })
  }),

  // Projects endpoints
  http.get(`${API_BASE}/projects/`, () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Test Project',
        address: '123 Test St',
        status: 'in_progress',
        start_date: '2024-01-01',
        target_completion_date: '2024-12-31',
        total_sqft: 2000
      }
    ])
  }),

  http.get(`${API_BASE}/projects/1`, () => {
    return HttpResponse.json({
      id: 1,
      name: 'Test Project',
      address: '123 Test St',
      status: 'in_progress',
      start_date: '2024-01-01',
      target_completion_date: '2024-12-31',
      total_sqft: 2000
    })
  }),

  http.post(`${API_BASE}/projects/`, () => {
    return HttpResponse.json({
      id: 2,
      name: 'New Project',
      address: '456 New St',
      status: 'not_started',
      start_date: null,
      target_completion_date: null,
      total_sqft: null
    })
  }),

  // Forecast endpoints
  http.get(`${API_BASE}/forecast-items/`, () => {
    return HttpResponse.json([
      {
        id: 1,
        project_id: 1,
        category: 'Foundation',
        estimated_cost: 10000,
        notes: 'Concrete foundation',
        progress_percent: 50,
        status: 'In Progress',
        start_date: '2024-01-01',
        end_date: '2024-02-01'
      }
    ])
  }),

  http.post(`${API_BASE}/forecast-items/`, () => {
    return HttpResponse.json({
      id: 2,
      project_id: 1,
      category: 'Framing',
      estimated_cost: 15000,
      notes: 'Wood framing',
      progress_percent: 0,
      status: 'Not Started',
      start_date: null,
      end_date: null
    })
  }),

  // Expenses endpoints
  http.get(`${API_BASE}/expenses/`, () => {
    return HttpResponse.json([
      {
        id: 1,
        project_id: 1,
        forecast_line_item_id: 1,
        vendor: 'Test Vendor',
        amount_spent: 5000,
        date: '2024-01-15'
      }
    ])
  })
]
