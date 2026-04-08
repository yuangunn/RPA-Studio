import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Trash2, Package } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'

export function VariablePanel() {
  const { t } = useTranslation()
  const { project, setVariables } = useProjectStore()
  const variables = project?.variables || {}
  const [editKey, setEditKey] = useState('')
  const [editVal, setEditVal] = useState('')

  const handleAdd = () => {
    if (!editKey.trim()) return
    const newVars = { ...variables, [editKey.trim()]: editVal }
    setVariables(newVars)
    setEditKey('')
    setEditVal('')
  }

  const handleDelete = (key: string) => {
    const newVars = { ...variables }
    delete newVars[key]
    setVariables(newVars)
  }

  const entries = Object.entries(variables)

  return (
    <div className="border-t border-surface0 bg-crust">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-surface0">
        <span className="text-subtext text-xs font-semibold flex items-center gap-1.5">
          <Package size={12} /> {t('variables.title')}
        </span>
        <span className="text-overlay0 text-[10px]">{entries.length}개</span>
      </div>

      <div className="max-h-32 overflow-y-auto">
        {entries.length === 0 ? (
          <div className="text-overlay0 text-[11px] text-center py-3">저장값이 없습니다</div>
        ) : (
          <table className="w-full text-[11px]">
            <thead>
              <tr className="text-overlay0 border-b border-surface0">
                <th className="text-left px-3 py-1 font-semibold">{t('variables.name')}</th>
                <th className="text-left px-3 py-1 font-semibold">{t('variables.value')}</th>
                <th className="w-8"></th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([key, val]) => (
                <tr key={key} className="border-b border-surface0 hover:bg-surface0/50 group">
                  <td className="px-3 py-1.5 text-text font-medium">{key}</td>
                  <td className="px-3 py-1.5 text-subtext">{String(val)}</td>
                  <td>
                    <button
                      onClick={() => handleDelete(key)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 text-overlay0 hover:text-red"
                    >
                      <Trash2 size={11} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add row */}
      <div className="flex gap-1.5 px-3 py-2 border-t border-surface0">
        <input
          type="text"
          value={editKey}
          onChange={(e) => setEditKey(e.target.value)}
          placeholder="이름"
          className="flex-1 bg-surface0 border border-surface1 rounded px-2 py-1 text-[11px] text-text focus:border-blue outline-none"
        />
        <input
          type="text"
          value={editVal}
          onChange={(e) => setEditVal(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          placeholder="값"
          className="flex-1 bg-surface0 border border-surface1 rounded px-2 py-1 text-[11px] text-text focus:border-blue outline-none"
        />
        <button
          onClick={handleAdd}
          className="px-2 py-1 bg-green/20 text-green rounded text-[10px] font-semibold hover:bg-green/30"
        >
          <Plus size={12} />
        </button>
      </div>
    </div>
  )
}
