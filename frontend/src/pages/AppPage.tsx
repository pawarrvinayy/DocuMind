import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Sidebar from '../components/Sidebar'
import ChatInterface from '../components/ChatInterface'
import SourcePanel from '../components/SourcePanel'
import type { Source } from '../types'

export default function AppPage() {
  const [activeDocId, setActiveDocId] = useState<number | null>(null)
  const [sources, setSources] = useState<Source[]>([])

  const logout = useAuth((s) => s.logout)
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/auth')
  }

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100">
      {/* Header */}
      <header className="h-14 border-b border-zinc-800 flex items-center px-4 shrink-0 bg-zinc-900">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-semibold text-zinc-100">DocuMind</span>
        </div>

        <div className="ml-auto flex items-center gap-3">
          {sources.length > 0 && (
            <span className="text-xs text-indigo-400 bg-indigo-600/10 border border-indigo-500/20 px-2.5 py-1 rounded-full">
              {sources.length} source{sources.length !== 1 ? 's' : ''} cited
            </span>
          )}
          <button
            onClick={handleLogout}
            className="text-sm text-zinc-400 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Sign out
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeDocId={activeDocId} onSelect={setActiveDocId} />
        <ChatInterface activeDocId={activeDocId} onSourcesUpdate={setSources} />
        {sources.length > 0 && (
          <SourcePanel sources={sources} onClose={() => setSources([])} />
        )}
      </div>
    </div>
  )
}
