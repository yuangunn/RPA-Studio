import { create } from 'zustand'
import type { Step, Project, ActionInfo } from '../types/models'
import * as api from '../api/client'

interface ProjectState {
  // Data
  project: Project | null
  projectName: string
  actions: ActionInfo[]
  dirty: boolean

  // Selection
  selectedStepId: string | null

  // Actions
  loadActions: () => Promise<void>
  newProject: (name: string) => Promise<void>
  loadProject: (name: string) => Promise<void>
  saveProject: () => Promise<void>
  addStep: (actionType: string, params?: Record<string, any>, index?: number, parentId?: string) => Promise<void>
  removeStep: (stepId: string) => Promise<void>
  updateStep: (stepId: string, params?: Record<string, any>, waitAfter?: number) => Promise<void>
  reorderSteps: (stepId: string, newIndex: number) => Promise<void>
  selectStep: (stepId: string | null) => void
  setVariables: (variables: Record<string, any>) => Promise<void>

  // Helpers
  getSelectedStep: () => Step | null
}

function findStep(steps: Step[], id: string): Step | null {
  for (const s of steps) {
    if (s.id === id) return s
    const found = findStep(s.children, id)
    if (found) return found
  }
  return null
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  project: null,
  projectName: '',
  actions: [],
  dirty: false,
  selectedStepId: null,

  loadActions: async () => {
    const actions = await api.getActions()
    set({ actions })
  },

  newProject: async (name: string) => {
    await api.createProject(name)
    const data = await api.getProject(name)
    set({ project: data, projectName: name, dirty: false, selectedStepId: null })
  },

  loadProject: async (name: string) => {
    const data = await api.getProject(name)
    set({ project: data, projectName: name, dirty: false, selectedStepId: null })
  },

  saveProject: async () => {
    const { project, projectName } = get()
    if (!project || !projectName) return
    await api.saveProject(projectName, project)
    set({ dirty: false })
  },

  addStep: async (actionType, params, index, parentId) => {
    const { projectName } = get()
    if (!projectName) return
    const newStep = await api.addStep(projectName, actionType, params, index, parentId)
    // Reload project to get updated steps
    const data = await api.getProject(projectName)
    set({ project: data, dirty: true })
  },

  removeStep: async (stepId) => {
    const { projectName } = get()
    if (!projectName) return
    await api.deleteStep(projectName, stepId)
    const data = await api.getProject(projectName)
    set({ project: data, dirty: true, selectedStepId: null })
  },

  updateStep: async (stepId, params, waitAfter) => {
    const { projectName } = get()
    if (!projectName) return
    await api.updateStep(projectName, stepId, {
      ...(params !== undefined && { params }),
      ...(waitAfter !== undefined && { wait_after: waitAfter }),
    })
    const data = await api.getProject(projectName)
    set({ project: data, dirty: true })
  },

  reorderSteps: async (stepId, newIndex) => {
    const { projectName } = get()
    if (!projectName) return
    await api.reorderSteps(projectName, stepId, newIndex)
    const data = await api.getProject(projectName)
    set({ project: data, dirty: true })
  },

  selectStep: (stepId) => set({ selectedStepId: stepId }),

  setVariables: async (variables) => {
    const { projectName } = get()
    if (!projectName) return
    await api.setVariables(projectName, variables)
    const data = await api.getProject(projectName)
    set({ project: data, dirty: true })
  },

  getSelectedStep: () => {
    const { project, selectedStepId } = get()
    if (!project || !selectedStepId) return null
    return findStep(project.steps, selectedStepId)
  },
}))
