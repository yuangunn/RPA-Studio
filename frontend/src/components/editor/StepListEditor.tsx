import { useTranslation } from 'react-i18next'
import { GripVertical, Trash2 } from 'lucide-react'
import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent, DragOverlay, type DragStartEvent,
} from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useState } from 'react'
import { useProjectStore } from '../../stores/projectStore'
import { useExecutionStore } from '../../stores/executionStore'
import type { Step } from '../../types/models'

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

function StepCard({ step, index, indent = 0, isDragging = false }: {
  step: Step; index: string; indent?: number; isDragging?: boolean
}) {
  const { selectedStepId, selectStep, removeStep } = useProjectStore()
  const { currentStepId } = useExecutionStore()
  const isSelected = selectedStepId === step.id
  const isRunning = currentStepId === step.id
  const accent = getAccentColor(step.type)

  return (
    <div
      onClick={() => selectStep(step.id)}
      className={`group flex items-center gap-0 rounded-xl overflow-hidden cursor-pointer transition-all ${
        isSelected ? 'ring-1 ring-blue' : ''
      } ${isRunning ? 'ring-2 ring-blue animate-pulse' : ''} ${
        isDragging ? 'opacity-50 ring-2 ring-mauve' : ''
      }`}
      style={{ marginLeft: indent * 24 }}
    >
      <div className="w-1 self-stretch shrink-0 rounded-l-xl" style={{ backgroundColor: accent }} />
      <div className="flex-1 flex items-center gap-3 px-3 py-2.5 bg-mantle hover:bg-surface0 transition-colors">
        <GripVertical size={14} className="text-surface1 opacity-0 group-hover:opacity-100 cursor-grab shrink-0" />
        <span
          className="w-6 h-6 flex items-center justify-center rounded-full text-[10px] font-bold shrink-0"
          style={{ backgroundColor: accent + '22', color: accent }}
        >
          {index}
        </span>
        <div className="flex-1 min-w-0">
          <div className="text-text text-[13px] font-semibold truncate">{step.label}</div>
          <div className="text-overlay0 text-[11px] truncate"><StepSummary step={step} /></div>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); removeStep(step.id) }}
          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red/20 text-overlay0 hover:text-red transition-all shrink-0"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  )
}

function SortableStepItem({ step, index }: { step: Step; index: number }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: step.id })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <StepCard step={step} index={String(index + 1)} isDragging={isDragging} />
      {step.children.map((child, ci) => (
        <StepCard key={child.id} step={child} index={`${index + 1}-${ci + 1}`} indent={1} />
      ))}
    </div>
  )
}

export function StepListEditor() {
  const { t } = useTranslation()
  const { project, projectName, addStep, reorderSteps } = useProjectStore()
  const steps = project?.steps || []
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
  )

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(String(event.active.id))
  }

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveId(null)
    const { active, over } = event
    if (!over || active.id === over.id) return

    const oldIndex = steps.findIndex(s => s.id === active.id)
    const newIndex = steps.findIndex(s => s.id === over.id)
    if (oldIndex === -1 || newIndex === -1) return

    reorderSteps(String(active.id), newIndex)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const actionType = e.dataTransfer.getData('action_type')
    if (actionType) addStep(actionType)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }

  const activeStep = activeId ? steps.find(s => s.id === activeId) : null

  return (
    <div
      className="flex-1 flex flex-col bg-base overflow-hidden"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <div className="flex items-center justify-between px-4 py-2 border-b border-surface0">
        <h2 className="text-text text-sm font-bold">
          📋 {projectName || t('project.new_name')}
        </h2>
        <span className="text-overlay0 text-xs">
          {t('editor.step_count', { count: steps.length })}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {steps.length === 0 ? (
          <div className="flex items-center justify-center h-full text-overlay0 text-sm">
            {t('editor.empty')}
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <SortableContext items={steps.map(s => s.id)} strategy={verticalListSortingStrategy}>
              {steps.map((step, i) => (
                <SortableStepItem key={step.id} step={step} index={i} />
              ))}
            </SortableContext>

            <DragOverlay>
              {activeStep && (
                <div className="opacity-80">
                  <StepCard step={activeStep} index="↕" />
                </div>
              )}
            </DragOverlay>
          </DndContext>
        )}
      </div>
    </div>
  )
}
