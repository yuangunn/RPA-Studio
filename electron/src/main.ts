import { app, BrowserWindow, ipcMain, dialog, Menu } from 'electron'
import * as path from 'path'
import { PythonManager } from './pythonManager'
import { createTray } from './tray'

const pythonManager = new PythonManager()
let mainWindow: BrowserWindow | null = null
let backendPort: number = 0

// Single instance lock
const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
}

app.on('second-instance', () => {
  if (mainWindow) {
    mainWindow.show()
    mainWindow.focus()
  }
})

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'RPA Studio',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
    backgroundColor: '#1e1e2e',
  })

  // Hide default menu bar
  Menu.setApplicationMenu(null)

  // Load frontend
  if (app.isPackaged) {
    // Production: load from built files
    mainWindow.loadFile(path.join(__dirname, '..', '..', 'frontend', 'dist', 'index.html'))
  } else {
    // Development: load from Vite dev server
    const devUrl = `http://localhost:5173`
    // Override proxy target to use the actual backend port
    mainWindow.loadURL(devUrl)
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  // Minimize to tray on close
  mainWindow.on('close', (event) => {
    if (!(app as any)._forceQuit) {
      event.preventDefault()
      mainWindow?.hide()
    }
  })

  // System tray
  createTray(mainWindow)
}

// IPC handlers
ipcMain.handle('get-backend-port', () => backendPort)

ipcMain.handle('show-open-dialog', async (_event, options) => {
  if (!mainWindow) return { canceled: true }
  return dialog.showOpenDialog(mainWindow, options)
})

ipcMain.handle('show-save-dialog', async (_event, options) => {
  if (!mainWindow) return { canceled: true }
  return dialog.showSaveDialog(mainWindow, options)
})

ipcMain.handle('get-platform-info', () => ({
  platform: process.platform,
  arch: process.arch,
}))

ipcMain.on('minimize-to-tray', () => {
  mainWindow?.hide()
})

// App lifecycle
app.on('ready', async () => {
  try {
    // Start Python backend first
    backendPort = await pythonManager.start()
    console.log(`[Main] Backend running on port ${backendPort}`)

    // Then create window
    await createWindow()
  } catch (err) {
    console.error('[Main] Failed to start:', err)
    dialog.showErrorBox(
      'RPA Studio 시작 실패',
      `백엔드 서버를 시작할 수 없습니다.\n\n${err}`
    )
    app.quit()
  }
})

app.on('before-quit', async () => {
  (app as any)._forceQuit = true
  await pythonManager.stop()
})

app.on('window-all-closed', () => {
  // Don't quit — tray keeps running
})

app.on('activate', () => {
  mainWindow?.show()
})
