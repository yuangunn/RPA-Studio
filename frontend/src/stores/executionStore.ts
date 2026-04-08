import { create } from 'zustand'
import type { LogEntry, ExecutionMessage } from '../types/models'
import * as api from '../api/client'

interface ExecutionState {
  isRunning: boolean
  executionId: string | null
  currentStepId: string | null
  logs: LogEntry[]
  error: string | null
  ws: WebSocket | null

  startExecution: (projectName: string) => Promise<void>
  stopExecution: () => Promise<void>
  addLog: (message: string, type?: LogEntry['type']) => void
  clearLogs: () => void
}

function timestamp(): string {
  return new Date().toLocaleTimeString('ko-KR', { hour12: false })
}

export const useExecutionStore = create<ExecutionState>((set, get) => ({
  isRunning: false,
  executionId: null,
  currentStepId: null,
  logs: [],
  error: null,
  ws: null,

  startExecution: async (projectName) => {
    const { addLog } = get()
    try {
      addLog('--- 실행 시작 ---')
      const { execution_id } = await api.startExecution(projectName)
      set({ isRunning: true, executionId: execution_id, error: null })

      // Connect WebSocket — use backend port if in Electron
      let wsHost = window.location.host
      if ((window as any).electronAPI) {
        try {
          const port = await (window as any).electronAPI.getBackendPort()
          if (port) wsHost = `127.0.0.1:${port}`
        } catch {}
      }
      const wsUrl = `ws://${wsHost}/ws/execution/${execution_id}`
      const ws = new WebSocket(wsUrl)

      ws.onmessage = (event) => {
        const msg: ExecutionMessage = JSON.parse(event.data)
        const { addLog } = get()

        switch (msg.type) {
          case 'step_enter':
            set({ currentStepId: msg.step_id })
            addLog(`▶ ${msg.step_label}`, 'step')
            break
          case 'step_exit':
            addLog(`✔ 완료`, 'step')
            break
          case 'log':
            addLog(msg.message || '', 'info')
            break
          case 'error':
            addLog(`❌ ${msg.message}`, 'error')
            set({ error: msg.message || null })
            break
          case 'execution_complete':
            addLog(msg.success ? '--- 완료! ---' : '--- 실행 실패 ---')
            set({ isRunning: false, currentStepId: null })
            ws.close()
            break
        }
      }

      ws.onerror = () => {
        addLog('WebSocket 연결 오류', 'error')
      }

      ws.onclose = () => {
        set({ isRunning: false, ws: null })
      }

      set({ ws })
    } catch (err: any) {
      addLog(`실행 실패: ${err.message}`, 'error')
      set({ isRunning: false })
    }
  },

  stopExecution: async () => {
    const { executionId, ws, addLog } = get()
    if (executionId) {
      await api.stopExecution(executionId)
      addLog('--- 중지됨 ---')
    }
    ws?.close()
    set({ isRunning: false, currentStepId: null, ws: null })
  },

  addLog: (message, type = 'info') => {
    set((state) => ({
      logs: [...state.logs, { timestamp: timestamp(), message, type: type }],
    }))
  },

  clearLogs: () => set({ logs: [] }),
}))
