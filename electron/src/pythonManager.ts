import { spawn, ChildProcess } from 'child_process'
import { app } from 'electron'
import * as path from 'path'
import * as net from 'net'
import * as http from 'http'

export class PythonManager {
  private process: ChildProcess | null = null
  private port: number = 0
  private restarting = false

  async start(): Promise<number> {
    this.port = await this.findFreePort()

    const pythonPath = this.getPythonPath()
    const backendDir = this.getBackendDir()

    console.log(`[PythonManager] Starting backend on port ${this.port}`)
    console.log(`[PythonManager] Python: ${pythonPath}`)
    console.log(`[PythonManager] Backend: ${backendDir}`)

    this.process = spawn(pythonPath, [
      '-m', 'uvicorn',
      'rpa_studio.api.server:app',
      '--host', '127.0.0.1',
      '--port', String(this.port),
    ], {
      cwd: backendDir,
      env: {
        ...process.env,
        PYTHONPATH: backendDir,
        PYTHONUNBUFFERED: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    this.process.stdout?.on('data', (data: Buffer) => {
      console.log(`[Backend] ${data.toString().trim()}`)
    })

    this.process.stderr?.on('data', (data: Buffer) => {
      console.error(`[Backend] ${data.toString().trim()}`)
    })

    this.process.on('exit', (code) => {
      console.log(`[PythonManager] Backend exited with code ${code}`)
      if (!this.restarting && code !== 0) {
        console.error('[PythonManager] Backend crashed, attempting restart...')
        setTimeout(() => this.start(), 2000)
      }
    })

    // Wait for server to be ready
    await this.waitForReady()
    console.log(`[PythonManager] Backend ready on port ${this.port}`)
    return this.port
  }

  async stop(): Promise<void> {
    this.restarting = true

    // Try graceful shutdown via API
    try {
      await this.httpPost(`http://127.0.0.1:${this.port}/api/shutdown`)
    } catch {
      // Ignore — server may already be down
    }

    // Wait a bit, then force kill
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        if (this.process && !this.process.killed) {
          this.process.kill('SIGTERM')
        }
        resolve()
      }, 3000)

      if (this.process) {
        this.process.on('exit', () => {
          clearTimeout(timeout)
          resolve()
        })
      } else {
        clearTimeout(timeout)
        resolve()
      }
    })
  }

  getPort(): number {
    return this.port
  }

  private getPythonPath(): string {
    if (app.isPackaged) {
      return path.join(process.resourcesPath, 'python', 'python.exe')
    }
    // Development: use system Python
    return process.env.RPA_PYTHON_PATH ||
      'C:\\Users\\Helios_Neo_18\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
  }

  private getBackendDir(): string {
    if (app.isPackaged) {
      return path.join(process.resourcesPath, 'backend')
    }
    return path.join(__dirname, '..', '..', 'backend')
  }

  private async findFreePort(): Promise<number> {
    return new Promise((resolve, reject) => {
      const server = net.createServer()
      server.listen(0, '127.0.0.1', () => {
        const addr = server.address()
        if (addr && typeof addr === 'object') {
          const port = addr.port
          server.close(() => resolve(port))
        } else {
          reject(new Error('Failed to get address'))
        }
      })
      server.on('error', reject)
    })
  }

  private async waitForReady(maxRetries = 30, interval = 500): Promise<void> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await this.httpGet(`http://127.0.0.1:${this.port}/api/health`)
        return
      } catch {
        await new Promise(r => setTimeout(r, interval))
      }
    }
    throw new Error('Backend failed to start within timeout')
  }

  private httpGet(url: string): Promise<string> {
    return new Promise((resolve, reject) => {
      http.get(url, (res) => {
        let data = ''
        res.on('data', (chunk) => { data += chunk })
        res.on('end', () => resolve(data))
      }).on('error', reject)
    })
  }

  private httpPost(url: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const req = http.request(url, { method: 'POST' }, (res) => {
        let data = ''
        res.on('data', (chunk) => { data += chunk })
        res.on('end', () => resolve(data))
      })
      req.on('error', reject)
      req.end()
    })
  }
}
