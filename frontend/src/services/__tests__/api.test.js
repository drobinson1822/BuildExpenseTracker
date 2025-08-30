import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api } from '../api'

// Mock fetch
global.fetch = vi.fn()

describe('ApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('request method', () => {
    it('makes GET request with correct headers', async () => {
      const mockResponse = { data: 'test' }
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Map([['content-type', 'application/json']]),
        json: () => Promise.resolve(mockResponse)
      })

      const result = await api.get('/test')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
      expect(result.data).toEqual(mockResponse)
    })

    it('includes authorization header when token exists', async () => {
      localStorage.setItem('token', 'test-token')
      
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Map([['content-type', 'application/json']]),
        json: () => Promise.resolve({})
      })

      await api.get('/test')

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      )
    })

    it('handles 401 responses by clearing token and redirecting', async () => {
      localStorage.setItem('token', 'invalid-token')
      const originalLocation = window.location
      delete window.location
      window.location = { href: '' }

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      })

      await expect(api.get('/test')).rejects.toThrow('Authentication failed')
      expect(localStorage.getItem('token')).toBeNull()
      expect(window.location.href).toBe('/login')

      window.location = originalLocation
    })

    it('handles non-JSON responses', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Map([['content-type', 'text/plain']])
      })

      const result = await api.get('/test')
      expect(result.data).toBeNull()
      expect(result.status).toBe(204)
    })

    it('handles network errors', async () => {
      fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'))

      await expect(api.get('/test')).rejects.toThrow('Network error - please check your connection')
    })

    it('handles HTTP error responses', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server error' })
      })

      await expect(api.get('/test')).rejects.toThrow('Server error')
    })
  })

  describe('HTTP methods', () => {
    beforeEach(() => {
      fetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Map([['content-type', 'application/json']]),
        json: () => Promise.resolve({})
      })
    })

    it('makes POST request with body', async () => {
      const data = { name: 'test' }
      await api.post('/test', data)

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(data)
        })
      )
    })

    it('makes PUT request with body', async () => {
      const data = { name: 'updated' }
      await api.put('/test/1', data)

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(data)
        })
      )
    })

    it('makes DELETE request', async () => {
      await api.delete('/test/1')

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test/1'),
        expect.objectContaining({
          method: 'DELETE'
        })
      )
    })

    it('handles query parameters in GET requests', async () => {
      await api.get('/test', { page: 1, limit: 10 })

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/test?page=1&limit=10',
        expect.any(Object)
      )
    })
  })
})
