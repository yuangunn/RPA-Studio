import { useState, useEffect } from 'react'
import { X, Clock, Zap, Plus, Trash2 } from 'lucide-react'
import * as api from '../../api/client'

export function ScheduleModal({ onClose }: { onClose: () => void }) {
  const [tab, setTab] = useState<'schedule' | 'trigger'>('schedule')
  const [schedules, setSchedules] = useState<Record<string, any>>({})
  const [triggers, setTriggers] = useState<string[]>([])

  // Schedule form
  const [schedType, setSchedType] = useState('daily')
  const [schedTime, setSchedTime] = useState('09:00')
  const [schedDay, setSchedDay] = useState(1)
  const [schedProject, setSchedProject] = useState('')
  const [projects, setProjects] = useState<string[]>([])

  // Trigger form
  const [trigType, setTrigType] = useState('app')
  const [trigValue, setTrigValue] = useState('')
  const [trigDir, setTrigDir] = useState('')
  const [trigProject, setTrigProject] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [s, t, p] = await Promise.all([
        fetch('/api/schedules').then(r => r.json()),
        fetch('/api/triggers').then(r => r.json()),
        api.listProjects(),
      ])
      setSchedules(s)
      setTriggers(t)
      setProjects(p.map((proj: any) => proj.name))
      if (p.length > 0 && !schedProject) {
        setSchedProject(p[0].name)
        setTrigProject(p[0].name)
      }
    } catch {}
  }

  const addSchedule = async () => {
    if (!schedProject) return
    await fetch('/api/schedules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: schedProject,
        type: schedType,
        time: schedTime,
        day: schedDay,
        enabled: true,
      }),
    })
    loadData()
  }

  const removeSchedule = async (jobId: string) => {
    await fetch(`/api/schedules/${jobId}`, { method: 'DELETE' })
    loadData()
  }

  const addTrigger = async () => {
    if (!trigValue || !trigProject) return
    await fetch('/api/triggers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trigger_type: trigType,
        value: trigValue,
        watch_dir: trigDir || undefined,
        project_name: trigProject,
      }),
    })
    setTrigValue('')
    loadData()
  }

  const removeTrigger = async (id: string) => {
    await fetch(`/api/triggers/${id}`, { method: 'DELETE' })
    loadData()
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-base border border-surface0 rounded-2xl w-[520px] max-h-[70vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface0">
          <h2 className="text-text font-bold text-sm">스케줄 & 트리거 관리</h2>
          <button onClick={onClose} className="text-overlay0 hover:text-text p-1 rounded"><X size={16} /></button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-surface0">
          <button
            onClick={() => setTab('schedule')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold transition-colors ${
              tab === 'schedule' ? 'text-blue border-b-2 border-blue' : 'text-overlay0 hover:text-text'
            }`}
          >
            <Clock size={13} /> 📅 스케줄
          </button>
          <button
            onClick={() => setTab('trigger')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold transition-colors ${
              tab === 'trigger' ? 'text-peach border-b-2 border-peach' : 'text-overlay0 hover:text-text'
            }`}
          >
            <Zap size={13} /> ⚡ 트리거
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {tab === 'schedule' ? (
            <>
              {/* Existing schedules */}
              {Object.entries(schedules).map(([id, config]) => (
                <div key={id} className="flex items-center gap-3 px-3 py-2.5 bg-mantle rounded-xl">
                  <Clock size={14} className="text-blue shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-text text-[12px] font-semibold">{id}</div>
                    <div className="text-overlay0 text-[10px]">{JSON.stringify(config)}</div>
                  </div>
                  <button onClick={() => removeSchedule(id)} className="p-1 text-overlay0 hover:text-red">
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}

              {/* Add form */}
              <div className="bg-mantle rounded-xl p-3 space-y-2">
                <div className="text-subtext text-[11px] font-semibold">새 스케줄 추가</div>
                <select value={schedProject} onChange={e => setSchedProject(e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none">
                  {projects.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
                <div className="flex gap-2">
                  <select value={schedType} onChange={e => setSchedType(e.target.value)}
                    className="flex-1 bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none">
                    <option value="daily">매일</option>
                    <option value="weekly">매주</option>
                    <option value="monthly">매월</option>
                  </select>
                  <input type="time" value={schedTime} onChange={e => setSchedTime(e.target.value)}
                    className="flex-1 bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none" />
                </div>
                {schedType === 'monthly' && (
                  <input type="number" value={schedDay} min={1} max={31} onChange={e => setSchedDay(parseInt(e.target.value))}
                    placeholder="날짜 (1-31)"
                    className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none" />
                )}
                <button onClick={addSchedule}
                  className="w-full flex items-center justify-center gap-1.5 py-2 bg-blue/20 text-blue rounded-lg text-xs font-semibold hover:bg-blue/30">
                  <Plus size={13} /> 추가
                </button>
              </div>
            </>
          ) : (
            <>
              {/* Existing triggers */}
              {triggers.map(id => (
                <div key={id} className="flex items-center gap-3 px-3 py-2.5 bg-mantle rounded-xl">
                  <Zap size={14} className="text-peach shrink-0" />
                  <div className="flex-1 text-text text-[12px] font-semibold">{id}</div>
                  <button onClick={() => removeTrigger(id)} className="p-1 text-overlay0 hover:text-red">
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}

              {/* Add form */}
              <div className="bg-mantle rounded-xl p-3 space-y-2">
                <div className="text-subtext text-[11px] font-semibold">새 트리거 추가</div>
                <select value={trigProject} onChange={e => setTrigProject(e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none">
                  {projects.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
                <select value={trigType} onChange={e => setTrigType(e.target.value)}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none">
                  <option value="app">앱 실행 감지</option>
                  <option value="file">파일 생성 감지</option>
                </select>
                <input type="text" value={trigValue} onChange={e => setTrigValue(e.target.value)}
                  placeholder={trigType === 'app' ? '프로세스 이름 (예: Teams.exe)' : '파일 패턴 (예: .csv)'}
                  className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none" />
                {trigType === 'file' && (
                  <input type="text" value={trigDir} onChange={e => setTrigDir(e.target.value)}
                    placeholder="감시할 폴더 경로"
                    className="w-full bg-surface0 border border-surface1 rounded-lg px-3 py-2 text-xs text-text outline-none" />
                )}
                <button onClick={addTrigger}
                  className="w-full flex items-center justify-center gap-1.5 py-2 bg-peach/20 text-peach rounded-lg text-xs font-semibold hover:bg-peach/30">
                  <Plus size={13} /> 추가
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
