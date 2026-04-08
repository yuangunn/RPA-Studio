import { Tray, Menu, nativeImage, BrowserWindow, app } from 'electron'
import * as path from 'path'

export function createTray(mainWindow: BrowserWindow): Tray {
  // Create a simple 16x16 icon programmatically
  const icon = nativeImage.createFromBuffer(
    createIconBuffer(),
    { width: 16, height: 16 }
  )

  const tray = new Tray(icon)
  tray.setToolTip('RPA Studio')

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '열기',
      click: () => {
        mainWindow.show()
        mainWindow.focus()
      },
    },
    {
      label: '스케줄 관리',
      click: () => {
        mainWindow.show()
        mainWindow.webContents.send('tray-action', 'schedules')
      },
    },
    { type: 'separator' },
    {
      label: '종료',
      click: () => {
        (app as any)._forceQuit = true
        app.quit()
      },
    },
  ])

  tray.setContextMenu(contextMenu)

  tray.on('double-click', () => {
    mainWindow.show()
    mainWindow.focus()
  })

  return tray
}

function createIconBuffer(): Buffer {
  // Create a simple 16x16 blue circle PNG-like RGBA buffer
  const size = 16
  const buf = Buffer.alloc(size * size * 4)
  const cx = size / 2
  const cy = size / 2
  const r = 6

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (y * size + x) * 4
      const dist = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
      if (dist <= r) {
        buf[idx] = 0x89     // R
        buf[idx + 1] = 0xB4 // G
        buf[idx + 2] = 0xFA // B
        buf[idx + 3] = 0xFF // A
      } else {
        buf[idx + 3] = 0x00 // transparent
      }
    }
  }
  return buf
}
