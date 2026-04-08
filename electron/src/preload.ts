import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendPort: (): Promise<number> =>
    ipcRenderer.invoke('get-backend-port'),

  showOpenDialog: (options: any): Promise<any> =>
    ipcRenderer.invoke('show-open-dialog', options),

  showSaveDialog: (options: any): Promise<any> =>
    ipcRenderer.invoke('show-save-dialog', options),

  minimizeToTray: (): void =>
    ipcRenderer.send('minimize-to-tray'),

  onTrayAction: (callback: (action: string) => void): void => {
    ipcRenderer.on('tray-action', (_event, action) => callback(action))
  },

  getPlatformInfo: (): Promise<{ platform: string; arch: string }> =>
    ipcRenderer.invoke('get-platform-info'),
})
