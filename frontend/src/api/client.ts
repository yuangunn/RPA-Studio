/** HTTP client for the Python backend API. */

// In Electron, get port from preload bridge. In browser dev, use Vite proxy.
let _baseUrl = '/api'

export async function initApiClient() {
  if ((window as any).electronAPI) {
    try {
      const port = await (window as any).electronAPI.getBackendPort()
      if (port) {
        _baseUrl = `http://127.0.0.1:${port}/api`
        console.log(`[API] Using Electron backend at port ${port}`)
      }
    } catch {
      console.log('[API] No Electron API, using Vite proxy')
    }
  }
}

function getBaseUrl(): string {
  return _baseUrl
}

const BASE_URL_GETTER = () => getBaseUrl()

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${getBaseUrl()}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

// --- Health ---
export const getHealth = () => request<{ status: string; version: string }>('/health')

// --- Actions ---
export const getActions = () => request<any[]>('/actions')
export const getActionSchema = (type: string) => request<any>(`/actions/${type}/schema`)
export const getWindows = () => request<string[]>('/actions/windows')

// --- Projects ---
export const listProjects = () => request<any[]>('/projects')
export const createProject = (name: string) =>
  request<any>('/projects', { method: 'POST', body: JSON.stringify({ name }) })
export const getProject = (name: string) => request<any>(`/projects/${encodeURIComponent(name)}`)
export const saveProject = (name: string, data: any) =>
  request<any>(`/projects/${encodeURIComponent(name)}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteProject = (name: string) =>
  request<any>(`/projects/${encodeURIComponent(name)}`, { method: 'DELETE' })

// --- Steps ---
export const getSteps = (projectName: string) =>
  request<any[]>(`/projects/${encodeURIComponent(projectName)}/steps`)
export const addStep = (projectName: string, type: string, params?: any, index?: number, parentId?: string) =>
  request<any>(`/projects/${encodeURIComponent(projectName)}/steps`, {
    method: 'POST',
    body: JSON.stringify({ type, params: params || {}, index, parent_id: parentId }),
  })
export const updateStep = (projectName: string, stepId: string, data: any) =>
  request<any>(`/projects/${encodeURIComponent(projectName)}/steps/${stepId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
export const deleteStep = (projectName: string, stepId: string) =>
  request<any>(`/projects/${encodeURIComponent(projectName)}/steps/${stepId}`, { method: 'DELETE' })
export const reorderSteps = (projectName: string, stepId: string, newIndex: number) =>
  request<any[]>(`/projects/${encodeURIComponent(projectName)}/steps/reorder`, {
    method: 'POST',
    body: JSON.stringify({ step_id: stepId, new_index: newIndex }),
  })

// --- Variables ---
export const getVariables = (projectName: string) =>
  request<Record<string, any>>(`/projects/${encodeURIComponent(projectName)}/variables`)
export const setVariables = (projectName: string, variables: Record<string, any>) =>
  request<any>(`/projects/${encodeURIComponent(projectName)}/variables`, {
    method: 'PUT',
    body: JSON.stringify(variables),
  })

// --- Execution ---
export const startExecution = (projectName: string) =>
  request<{ execution_id: string }>('/execution/run', {
    method: 'POST',
    body: JSON.stringify({ project_name: projectName }),
  })
export const stopExecution = (execId: string) =>
  request<any>(`/execution/stop/${execId}`, { method: 'POST' })
export const getExecutionStatus = (execId: string) => request<any>(`/execution/status/${execId}`)

// --- Recorder ---
export const startRecording = () => request<any>('/recorder/start', { method: 'POST' })
export const stopRecording = () => request<any>('/recorder/stop', { method: 'POST' })
export const getRecorderStatus = () => request<any>('/recorder/status')

// --- Element Picker ---
export const pickElementAtCursor = () => request<any>('/element-picker/pick', { method: 'POST' })
export const getElementAt = (x: number, y: number) => request<any>(`/element-picker/at/${x}/${y}`)

// --- Locale ---
export const getLocale = () => request<any>('/locale')
