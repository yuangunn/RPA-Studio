import { useTranslation } from 'react-i18next'
import { GripVertical, Trash2 } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'
import { useExecutionStore } from '../../stores/executionStore'
import type { Step } from '../../types/models'

/** Color for the left accent bar based on action type */
function getAccentColor(type: string): string {
  if (type.startsWith('app_') || type.startsWith('window_')) return '#5c6bc0'
  if (type.startsWith('ui_') || type === 'hotkey' || type.startsWith('mouse_')) return '#ef6c00'
  if (type.startsWith('if_') || type === 'loop' || type === 'wait' || type === 'stop') return '#ab47bc'
  if (type.startsWith('excel_') || type.startsWith('file_') || type.startsWith('folder_')) return '#26a69a'
  if (type.startsWith('browser_')) return '#42a5f5'
  if (type.startsWith('image_') || type.startsWith('ocr_')) return '#66bb6a'
  return '#78909c'
}

function StepSummary({ step }: { step: Step }) {
  const p = step.params
  switch (step.type) {
    case 'app_open': return <span>{p.app_name || ''}</span>
    case 'ui_click': return <span>{p.element_path || ''}</span>
    case 'hotkey': return <span>{p.keys || ''}</span>
    case 'wait': return <span>{p.seconds || 1}초 대기</span>
    case 'loop': return <span>{p.count || 1}회 반복</span>
    case 'notify': return <span>{(p.message || '').slice(0, 30)}</span>
    case 'browser_url': return <span>{p.url || ''}</span>
    case 'excel_write': return <span>{p.file_path || ''}</span>
    default: return null
  }
}

function StepItem({ step, index, indent = 0 }: { step: Step; index: string; indent?: number }) {
  const { selectedStepId, selectStep, removeStep } = useProjectStore()
  const { currentStepId } = useExecutionStore()
  const isSelected = selectedStepId === step.id
  const isRunning = currentStepId === step.id
  const accent = getAccentColor(step.type)

  return (
    <>
      <div
        onClick={() => selectStep(step.id)}
        className={`group flex items-center gap-0 rounded-xl overflow-hidden cursor-pointer transition-all ${
          isSelected ? 'ring-1 ring-blue' : ''
        } ${isRunning ? 'ring-2 ring-blue animate-pulse' : ''}`}
        style={{ marginLeft: indent * 24 }}
      >
        {/* Left accent bar */}
        <div className="w-1 self-stretch shrink-0 rounded-l-xl" style={{ backgroundColor: accent }} />

        {/* Content */}
        <div className="flex-1 flex items-center gap-3 px-3 py-2.5 bg-mantle hover:bg-surface0 transition-colors">
          {/* Drag handle */}
          <GripVertical size={14} className="text-surface1 opacity-0 group-hover:opacity-100 cursor-grab" />

          {/* Number badge */}
          <span
            className="w-6 h-6 flex items-center justify-center rounded-full text-[10px] font-bold shrink-0"
            style={{ backgroundColor: accent + '22', color: accent }}
          >
            {index}
          </span>

          {/* Label + summary */}
          <div className="flex-1 min-w-0">
            <div className="text-text text-[13px] font-semibold truncate">{step.label}</div>
            <div className="text-overlay0 text-[11px] truncate">
              <StepSummary step={step} />
            </div>
          </div>

          {/* Delete */}
          <button
            onClick={(e) => { e.stopPropagation(); removeStep(step.id) }}
            className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red/20 text-overlay0 hover:text-red transition-all"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Children (loop/if-else) */}
      {step.children.map((child, ci) => (
        <StepItem key={child.id} step={child} index={`${index}-${ci + 1}`} indent={indent + 1} />
      ))}
    </>
  )
}

export function StepListEditor() {
  const { t } = useTranslation()
  const { project, projectName, addStep } = useProjectStore()
  const steps = project?.steps || []

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const actionType = e.dataTransfer.getData('action_type')
    if (actionType) addStep(actionType)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }

  return (
    <div
      className="flex-1 flex flex-col bg-base overflow-hidden"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-surface0">
        <h2 className="text-text text-sm font-bold">
          📋 {projectName || t('project.new_name')}
        </h2>
        <span className="text-overlay0 text-xs">
          {t('editor.step_count', { count: steps.length })}
        </span>
      </div>

      {/* Step list */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {steps.length === 0 ? (
          <div className="flex items-center justify-center h-full text-overlay0 text-sm">
            {t('editor.empty')}
          </div>
        ) : (
          steps.map((step, i) => (
            <StepItem key={step.id} step={step} index={String(i + 1)} />
          ))
        )}
      </div>
    </div>
  )
}
