import { useEffect } from 'react'
import './i18n'
import { Toolbar } from './components/layout/Toolbar'
import { ActionPalette } from './components/palette/ActionPalette'
import { StepListEditor } from './components/editor/StepListEditor'
import { PropertyPanel } from './components/properties/PropertyPanel'
import { LogViewer } from './components/log/LogViewer'
import { useProjectStore } from './stores/projectStore'

export default function App() {
  const { newProject, projectName } = useProjectStore()

  useEffect(() => {
    if (!projectName) {
      newProject('새 프로젝트').catch(console.error)
    }
  }, [])

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
