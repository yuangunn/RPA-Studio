import { useState, useEffect } from 'react'
import { FolderOpen, Trash2, Plus, X } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'
import * as api from '../../api/client'

interface ProjectInfo {
  name: string
  version: string
  created: string
  step_count: number
}

export function ProjectModal({ onClose }: { onClose: () => void }) {
  const { loadProject, newProject } = useProjectStore()
  const [projects, setProjects] = useState<ProjectInfo[]>([])
  const [newName, setNewName] = useState('')

  useEffect(() => {
    api.listProjects().then(setProjects).catch(console.error)
  }, [])

  const handleOpen = async (name: string) => {
    await loadProject(name)
    onClose()
  }

  const handleCreate = async () => {
    if (!newName.trim()) return
    await newProject(newName.trim())
    onClose()
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`"${name}" 프로젝트를 삭제할까요?`)) return
    await api.deleteProject(name)
    setProjects(prev => prev.filter(p => p.name !== name))
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-base border border-surface0 rounded-2xl w-[480px] max-h-[70vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface0">
          <h2 className="text-text font-bold text-sm">프로젝트 관리</h2>
          <button onClick={onClose} className="text-overlay0 hover:text-text p-1 rounded">
            <X size={16} />
          </button>
        </div>

        {/* New project */}
        <div className="px-5 py-3 border-b border-surface0 flex gap-2">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            placeholder="새 프로젝트 이름..."
            className="flex-1 bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text focus:border-blue outline-none"
          />
          <button
            onClick={handleCreate}
            className="flex items-center gap-1.5 px-3 py-2 bg-green/20 text-green rounded-lg text-xs font-semibold hover:bg-green/30"
          >
            <Plus size={14} /> 생성
          </button>
        </div>

        {/* Project list */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {projects.length === 0 ? (
            <div className="text-overlay0 text-xs text-center py-8">저장된 프로젝트가 없습니다</div>
          ) : (
            projects.map((proj) => (
              <div
                key={proj.name}
                className="flex items-center gap-3 px-4 py-3 bg-mantle rounded-xl hover:bg-surface0 transition-colors group"
              >
                <FolderOpen size={16} className="text-blue shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-text text-[13px] font-semibold truncate">{proj.name}</div>
                  <div className="text-overlay0 text-[11px]">
                    {proj.step_count}개 단계 · {proj.created}
                  </div>
                </div>
                <button
                  onClick={() => handleOpen(proj.name)}
                  className="px-3 py-1.5 bg-blue/20 text-blue rounded-lg text-[11px] font-semibold hover:bg-blue/30"
                >
                  열기
                </button>
                <button
                  onClick={() => handleDelete(proj.name)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-red/20 text-overlay0 hover:text-red transition-all"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
