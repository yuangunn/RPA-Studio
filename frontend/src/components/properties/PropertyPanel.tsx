import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useProjectStore } from '../../stores/projectStore'
import * as api from '../../api/client'
import type { ParamField } from '../../types/models'

export function PropertyPanel() {
  const { t } = useTranslation()
  const { selectedStepId, project, actions, updateStep } = useProjectStore()
  const [windows, setWindows] = useState<string[]>([])

  // Find selected step
  const step = selectedStepId && project
    ? findStep(project.steps, selectedStepId)
    : null

  // Find action schema
  const actionInfo = step ? actions.find(a => a.type === step.type) : null
  const schema = actionInfo?.params_schema || []

  // Load window list when needed
  useEffect(() => {
    if (schema.some(f => f.type === 'window_list')) {
      api.getWindows().then(setWindows).catch(() => {})
    }
  }, [step?.type])

  const handleParamChange = (key: string, value: any) => {
    if (!step) return
    const newParams = { ...step.params, [key]: value }
    updateStep(step.id, newParams)
  }

  const handleWaitChange = (value: number) => {
    if (!step) return
    updateStep(step.id, undefined, value)
  }

  if (!step) {
    return (
      <div className="w-64 bg-mantle border-l border-surface0 flex items-center justify-center shrink-0">
        <span className="text-overlay0 text-xs">{t('properties.no_selection')}</span>
      </div>
    )
  }

  return (
    <div className="w-64 bg-mantle border-l border-surface0 flex flex-col shrink-0 overflow-hidden">
      <div className="px-3 py-2 border-b border-surface0">
        <h3 className="text-subtext text-xs font-semibold uppercase">{t('properties.title')}</h3>
        <p className="text-text text-sm font-bold mt-1">{step.label}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Action type (read-only) */}
        <div>
          <label className="text-overlay0 text-[11px] font-semibold block mb-1">작업 유형</label>
          <div className="bg-surface0 px-3 py-2 rounded-lg text-xs text-text">{step.label}</div>
        </div>

        {/* Dynamic fields from schema */}
        {schema.map((field: ParamField) => {
          if (field.key.startsWith('_')) {
            // Special: element picker button
            if (field.type === 'element_picker') {
              return (
                <button
                  key={field.key}
                  className="w-full py-2.5 bg-blue/10 text-blue border border-blue/30 rounded-lg text-xs font-semibold hover:bg-blue/20 transition-colors"
                >
                  {field.label}
                </button>
              )
            }
            return null
          }

          const value = step.params[field.key] ?? ''

          return (
            <div key={field.key}>
              <label className="text-overlay0 text-[11px] font-semibold block mb-1">{field.label}</label>

              {field.type === 'text' && (
                <input
                  type="text"
                  value={value}
                  onChange={(e) => handleParamChange(field.key, e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                />
              )}

              {field.type === 'int' && (
                <input
                  type="number"
                  value={value}
                  min={field.min ?? 0}
                  max={field.max ?? 99999}
                  onChange={(e) => handleParamChange(field.key, parseInt(e.target.value) || 0)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                />
              )}

              {field.type === 'float' && (
                <input
                  type="number"
                  value={value}
                  min={field.min ?? 0}
                  max={field.max ?? 3600}
                  step={0.1}
                  onChange={(e) => handleParamChange(field.key, parseFloat(e.target.value) || 0)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                />
              )}

              {field.type === 'combo' && field.choices && (
                <select
                  value={value}
                  onChange={(e) => handleParamChange(field.key, e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                >
                  {Object.entries(field.choices).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              )}

              {field.type === 'file' && (
                <input
                  type="text"
                  value={value}
                  placeholder="파일 경로를 입력하세요"
                  onChange={(e) => handleParamChange(field.key, e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                />
              )}

              {field.type === 'window_list' && (
                <div className="space-y-1">
                  <select
                    value={value}
                    onChange={(e) => handleParamChange(field.key, e.target.value)}
                    className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
                  >
                    <option value="">창을 선택하세요</option>
                    {windows.map((w) => (
                      <option key={w} value={w}>{w}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => api.getWindows().then(setWindows)}
                    className="text-[10px] text-blue hover:underline"
                  >
                    🔄 새로고침
                  </button>
                </div>
              )}
            </div>
          )
        })}

        {/* Wait after */}
        <div>
          <label className="text-overlay0 text-[11px] font-semibold block mb-1">{t('properties.wait_after')}</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={step.wait_after}
              min={0}
              max={300}
              step={0.1}
              onChange={(e) => handleWaitChange(parseFloat(e.target.value) || 0)}
              className="flex-1 bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
            />
            <span className="text-overlay0 text-xs">초</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function findStep(steps: any[], id: string): any {
  for (const s of steps) {
    if (s.id === id) return s
    const found = findStep(s.children || [], id)
    if (found) return found
  }
  return null
}
