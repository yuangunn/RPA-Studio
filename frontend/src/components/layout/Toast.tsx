import { useEffect, useState } from 'react'
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react'
import { useExecutionStore } from '../../stores/executionStore'

interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

let toastId = 0

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const logs = useExecutionStore((s) => s.logs)

  useEffect(() => {
    if (logs.length === 0) return
    const last = logs[logs.length - 1]

    // Show toast for notable log entries
    if (last.message.includes('완료!') || last.message.includes('성공')) {
      addToast(last.message, 'success')
    } else if (last.type === 'error') {
      addToast(last.message, 'error')
    } else if (last.message.includes('알림:')) {
      addToast(last.message.replace('알림: ', ''), 'info')
    }
  }, [logs.length])

  const addToast = (message: string, type: ToastItem['type']) => {
    const id = ++toastId
    setToasts((prev) => [...prev.slice(-2), { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }

  const removeToast = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => {
        const Icon = toast.type === 'success' ? CheckCircle
          : toast.type === 'error' ? AlertCircle
          : Info
        const colors = toast.type === 'success' ? 'bg-green/10 border-green/30 text-green'
          : toast.type === 'error' ? 'bg-red/10 border-red/30 text-red'
          : 'bg-blue/10 border-blue/30 text-blue'

        return (
          <div
            key={toast.id}
            className={`flex items-start gap-2.5 px-4 py-3 rounded-xl border backdrop-blur-sm shadow-lg animate-slide-in ${colors}`}
          >
            <Icon size={16} className="shrink-0 mt-0.5" />
            <span className="text-xs font-medium flex-1">{toast.message}</span>
            <button onClick={() => removeToast(toast.id)} className="shrink-0 opacity-60 hover:opacity-100">
              <X size={12} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
