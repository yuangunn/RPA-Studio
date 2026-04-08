/** Mirrors Python backend data models exactly. */

export interface Step {
  id: string
  type: string
  label: string
  params: Record<string, any>
  wait_after: number
  children: Step[]
}

export interface Project {
  schema_version: number
  name: string
  version: string
  created: string
  steps: Step[]
  variables: Record<string, any>
  schedule: Record<string, any>
  triggers: Record<string, any>[]
}

export interface ParamField {
  key: string
  label: string
  type: 'text' | 'int' | 'float' | 'combo' | 'file' | 'element_picker' | 'window_list'
  choices?: Record<string, string>
  min?: number
  max?: number
}

export interface ActionInfo {
  type: string
  label: string
  category: string
  category_icon: string
  category_full: string
  locked: boolean
  params_schema: ParamField[]
}

export interface ExecutionMessage {
  type: 'step_enter' | 'step_exit' | 'log' | 'error' | 'execution_complete' | 'heartbeat'
  step_id?: string
  step_label?: string
  message?: string
  result?: string
  success?: boolean
}

export interface LogEntry {
  timestamp: string
  message: string
  type: 'info' | 'error' | 'step'
}
