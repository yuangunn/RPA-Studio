import { useEffect, useState } from 'react'
import './i18n'
import { initApiClient } from './api/client'
import { Toolbar } from './components/layout/Toolbar'
import { ActionPalette } from './components/palette/ActionPalette'
import { StepListEditor } from './components/editor/StepListEditor'
import { PropertyPanel } from './components/properties/PropertyPanel'
import { LogViewer } from './components/log/LogViewer'
import { useProjectStore } from './stores/projectStore'

export default function App() {
  const { newProject, loadProject, projectName } = useProjectStore()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    async function init() {
      await initApiClient()
      if (!projectName) {
        // Try to load existing project, create new if not found
        try {
          await loadProject('새 프로젝트')
        } catch {
          await newProject('새 프로젝트')
        }
      }
      setReady(true)
    }
    init()
  }, [])

  if (!ready) {
    return (
      <div className="h-screen flex items-center justify-center bg-base text-text">
        <div className="text-center">
          <div className="text-4xl mb-4">🤖</div>
          <div className="text-subtext text-sm">RPA Studio 로딩 중...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-base text-text">
      <Toolbar />
      <div className="flex-1 flex overflow-hidden">
        <ActionPalette />
        <StepListEditor />
        <PropertyPanel />
      </div>
      <LogViewer />
    </div>
  )
}
