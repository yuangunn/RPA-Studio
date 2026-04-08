import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, ChevronDown, ChevronRight, Lock } from 'lucide-react'
import { useProjectStore } from '../../stores/projectStore'
import type { ActionInfo } from '../../types/models'

export function ActionPalette() {
  const { t } = useTranslation()
  const { actions, loadActions, addStep } = useProjectStore()
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  useEffect(() => {
    loadActions()
  }, [])

  // Group by category
  const categories = actions.reduce<Record<string, ActionInfo[]>>((acc, a) => {
    const key = a.category_full
    if (!acc[key]) acc[key] = []
    acc[key].push(a)
    return acc
  }, {})

  // Filter by search
  const filtered = search
    ? Object.fromEntries(
        Object.entries(categories).map(([cat, items]) => [
          cat,
          items.filter(
            (a) =>
              a.label.includes(search) ||
              a.type.includes(search.toLowerCase())
          ),
        ]).filter(([, items]) => (items as any[]).length > 0)
      )
    : categories

  const toggleCategory = (cat: string) => {
    setExpanded((prev) => ({ ...prev, [cat]: !prev[cat] }))
  }

  const handleDoubleClick = (action: ActionInfo) => {
    if (action.locked) return
    addStep(action.type)
  }

  const handleDragStart = (e: React.DragEvent, action: ActionInfo) => {
    if (action.locked) {
      e.preventDefault()
      return
    }
    e.dataTransfer.setData('action_type', action.type)
    e.dataTransfer.effectAllowed = 'copy'
  }

  return (
    <div className="w-56 bg-mantle border-r border-surface0 flex flex-col shrink-0 overflow-hidden">
      <div className="px-3 py-2 border-b border-surface0">
        <h3 className="text-subtext text-xs font-semibold uppercase mb-2">{t('palette.title')}</h3>
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-overlay0" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('palette.search')}
            className="w-full pl-8 pr-3 py-1.5 bg-surface0 rounded-lg text-xs text-text placeholder:text-overlay0 border border-surface1 focus:border-blue outline-none"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-1">
        {Object.entries(filtered).map(([cat, items]) => {
          const isExpanded = expanded[cat] !== false // default open
          return (
            <div key={cat} className="mb-0.5">
              <button
                onClick={() => toggleCategory(cat)}
                className="w-full flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-text hover:bg-surface0 transition-colors"
              >
                {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                {cat}
              </button>

              {isExpanded && (
                <div className="ml-2">
                  {(items as ActionInfo[]).map((action) => (
                    <div
                      key={action.type}
                      draggable={!action.locked}
                      onDragStart={(e) => handleDragStart(e, action)}
                      onDoubleClick={() => handleDoubleClick(action)}
                      className={`flex items-center gap-2 px-4 py-1.5 mx-1 rounded-md text-xs cursor-pointer transition-colors ${
                        action.locked
                          ? 'text-overlay0 cursor-not-allowed opacity-50'
                          : 'text-subtext hover:bg-surface0 hover:text-text'
                      }`}
                    >
                      <span>{action.label}</span>
                      {action.locked && <Lock size={10} className="text-overlay0" />}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
