import { useTranslation } from 'react-i18next'
import { Play, Square, Circle, Save, FolderOpen, FilePlus } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'
import { useExecutionStore } from '../../stores/executionStore'
import * as api from '../../api/client'
import { useState } from 'react'

export function Toolbar({ onOpenProject, onOpenSchedule }: { onOpenProject?: () => void; onOpenSchedule?: () => void }) {
  const { t } = useTranslation()
  const { projectName, dirty, saveProject, newProject, addStep } = useProjectStore()
  const { isRunning, startExecution, stopExecution, addLog } = useExecutionStore()
  const [isRecording, setIsRecording] = useState(false)

  const handleRun = async () => {
    if (!projectName) return
    await saveProject() // 자동 저장 후 실행
    startExecution(projectName)
  }

  const handleNew = async () => {
    const name = prompt('프로젝트 이름을 입력하세요:')
    if (name) await newProject(name)
  }

  return (
    <div className="h-12 bg-mantle border-b border-surface0 flex items-center px-4 gap-2 shrink-0">
      {/* Project name */}
      <span className="text-text font-semibold text-sm mr-4">
        🤖 {projectName || 'RPA Studio'}
        {dirty && <span className="text-peach ml-1">●</span>}
      </span>

      <div className="w-px h-6 bg-surface0" />

      {/* Execution controls */}
      <button
        onClick={handleRun}
        disabled={isRunning || !projectName}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-green/20 text-green rounded-lg text-xs font-semibold hover:bg-green/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <Play size={14} /> {t('toolbar.run')}
      </button>

      <button
        onClick={stopExecution}
        disabled={!isRunning}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-red/20 text-red rounded-lg text-xs font-semibold hover:bg-red/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <Square size={14} /> {t('toolbar.stop')}
      </button>

      <button
        onClick={async () => {
          if (isRecording) {
            const result = await api.stopRecording()
            setIsRecording(false)
            addLog(`녹화 완료: ${result.step_count}개 단계 캡처됨`)
            // 캡처된 스텝들을 프로젝트에 추가
            for (const step of result.steps || []) {
              await addStep(step.type, step.params)
            }
          } else {
            await api.startRecording()
            setIsRecording(true)
            addLog('녹화 시작... 작업을 수행한 후 다시 눌러 중지하세요')
          }
        }}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
          isRecording
            ? 'bg-red text-crust animate-pulse'
            : 'bg-peach/20 text-peach hover:bg-peach/30'
        }`}
      >
        <Circle size={14} /> {isRecording ? '⏹ 녹화 중지' : t('toolbar.record')}
      </button>

      <div className="w-px h-6 bg-surface0" />

      <button
        onClick={onOpenSchedule}
        className="flex items-center gap-1.5 px-3 py-1.5 text-subtext rounded-lg text-xs hover:bg-surface0 transition-colors"
      >
        📅 스케줄
      </button>

      <div className="flex-1" />

      {/* File controls */}
      <button
        onClick={handleNew}
        className="flex items-center gap-1.5 px-3 py-1.5 text-subtext rounded-lg text-xs hover:bg-surface0 transition-colors"
      >
        <FilePlus size={14} /> {t('toolbar.new')}
      </button>

      <button
        onClick={onOpenProject}
        className="flex items-center gap-1.5 px-3 py-1.5 text-subtext rounded-lg text-xs hover:bg-surface0 transition-colors"
      >
        <FolderOpen size={14} /> {t('toolbar.open')}
      </button>

      <button
        onClick={saveProject}
        disabled={!projectName}
        className="flex items-center gap-1.5 px-3 py-1.5 text-subtext rounded-lg text-xs hover:bg-surface0 disabled:opacity-30 transition-colors"
      >
        <Save size={14} /> {t('toolbar.save')}
      </button>
    </div>
  )
}
