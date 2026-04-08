import { useTranslation } from 'react-i18next'
import { Play, Square, Circle, Save, FolderOpen, FilePlus } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'
import { useExecutionStore } from '../../stores/executionStore'

export function Toolbar() {
  const { t } = useTranslation()
  const { projectName, dirty, saveProject, newProject } = useProjectStore()
  const { isRunning, startExecution, stopExecution } = useExecutionStore()

  const handleRun = () => {
    if (projectName) startExecution(projectName)
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

      <button className="flex items-center gap-1.5 px-3 py-1.5 bg-peach/20 text-peach rounded-lg text-xs font-semibold hover:bg-peach/30 transition-colors">
        <Circle size={14} /> {t('toolbar.record')}
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
        onClick={saveProject}
        disabled={!projectName}
        className="flex items-center gap-1.5 px-3 py-1.5 text-subtext rounded-lg text-xs hover:bg-surface0 disabled:opacity-30 transition-colors"
      >
        <Save size={14} /> {t('toolbar.save')}
      </button>
    </div>
  )
}
