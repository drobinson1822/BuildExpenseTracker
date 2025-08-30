import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useProjects } from '../useProjects'
import { projectService } from '../../services'

// Mock the project service
vi.mock('../../services', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn()
  }
}))

describe('useProjects', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads projects on mount', async () => {
    const mockProjects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ]
    projectService.getProjects.mockResolvedValueOnce(mockProjects)

    const { result } = renderHook(() => useProjects())

    expect(result.current.loading).toBe(true)
    expect(result.current.projects).toEqual([])

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.projects).toEqual(mockProjects)
    expect(result.current.error).toBeNull()
    expect(projectService.getProjects).toHaveBeenCalledTimes(1)
  })

  it('handles loading error', async () => {
    const errorMessage = 'Failed to load projects'
    projectService.getProjects.mockRejectedValueOnce(new Error(errorMessage))

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe(errorMessage)
    expect(result.current.projects).toEqual([])
  })

  it('creates new project', async () => {
    const existingProjects = [{ id: 1, name: 'Project 1' }]
    const newProject = { id: 2, name: 'New Project' }
    
    projectService.getProjects.mockResolvedValueOnce(existingProjects)
    projectService.createProject.mockResolvedValueOnce(newProject)

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    const projectData = { name: 'New Project' }
    await result.current.createProject(projectData)

    expect(projectService.createProject).toHaveBeenCalledWith(projectData)
    expect(result.current.projects).toHaveLength(2)
    expect(result.current.projects[1]).toEqual(newProject)
  })

  it('handles create project error', async () => {
    projectService.getProjects.mockResolvedValueOnce([])
    projectService.createProject.mockRejectedValueOnce(new Error('Create failed'))

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    await expect(result.current.createProject({})).rejects.toThrow('Create failed')
    expect(result.current.error).toBe('Create failed')
  })

  it('updates existing project', async () => {
    const projects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ]
    const updatedProject = { id: 1, name: 'Updated Project 1' }
    
    projectService.getProjects.mockResolvedValueOnce(projects)
    projectService.updateProject.mockResolvedValueOnce(updatedProject)

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    await result.current.updateProject(1, { name: 'Updated Project 1' })

    expect(projectService.updateProject).toHaveBeenCalledWith(1, { name: 'Updated Project 1' })
    expect(result.current.projects[0]).toEqual(updatedProject)
    expect(result.current.projects[1].name).toBe('Project 2') // Other project unchanged
  })

  it('deletes project', async () => {
    const projects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ]
    
    projectService.getProjects.mockResolvedValueOnce(projects)
    projectService.deleteProject.mockResolvedValueOnce()

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    await result.current.deleteProject(1)

    expect(projectService.deleteProject).toHaveBeenCalledWith(1)
    expect(result.current.projects).toHaveLength(1)
    expect(result.current.projects[0].id).toBe(2)
  })

  it('reloads projects', async () => {
    const initialProjects = [{ id: 1, name: 'Project 1' }]
    const reloadedProjects = [
      { id: 1, name: 'Project 1' },
      { id: 2, name: 'Project 2' }
    ]
    
    projectService.getProjects
      .mockResolvedValueOnce(initialProjects)
      .mockResolvedValueOnce(reloadedProjects)

    const { result } = renderHook(() => useProjects())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.projects).toHaveLength(1)

    await result.current.loadProjects()

    expect(result.current.projects).toHaveLength(2)
    expect(projectService.getProjects).toHaveBeenCalledTimes(2)
  })
})
