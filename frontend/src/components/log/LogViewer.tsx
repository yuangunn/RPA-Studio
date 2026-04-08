import { useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Trash2 } from 'lucide-react'
import { useExecutionStore } from '../../stores/executionStore'

export function LogViewer() {
  const { t } = useTranslation()
  const { logs, clearLogs } = useExecutionStore()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs.length])

  return (
    <div className="h-40 bg-crust border-t border-surface0 flex flex-col shrink-0">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-surface0">
        <span className="text-subtext text-xs font-semibold">{t('log.title')}</span>
        <button
          onClick={clearLogs}
          className="text-overlay0 hover:text-red p-1 rounded transition-colors"
        >
          <Trash2 size={12} />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-3 py-1 font-mono text-[11px]">
        {logs.length === 0 ? (
          <div className="text-overlay0 text-center py-4">{t('log.empty')}</div>
        ) : (
          logs.map((log, i) => (
            <div
              key={i}
              className={`py-0.5 ${
                log.type === 'error' ? 'text-red' :
                log.type === 'step' ? 'text-blue' :
                'text-subtext'
              }`}
            >
              <span className="text-overlay0 mr-2">[{log.timestamp}]</span>
              {log.message}
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>
    </div>
  )
}
