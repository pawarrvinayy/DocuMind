import type { Source } from '../types'

interface Props {
  sources: Source[]
  onClose: () => void
}

export default function SourcePanel({ sources, onClose }: Props) {
  return (
    <aside className="w-72 bg-zinc-900 border-l border-zinc-800 flex flex-col shrink-0">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Sources</h2>
        <button
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-300 transition-colors"
          aria-label="Close sources"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {sources.map((source, i) => (
          <div key={i} className="bg-zinc-800 rounded-xl p-3 border border-zinc-700">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1 bg-indigo-600/20 text-indigo-400 text-xs font-medium px-2 py-0.5 rounded-full border border-indigo-500/30">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Page {source.page}
              </span>
              <span className="text-zinc-500 text-xs">#{i + 1}</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed line-clamp-4">{source.excerpt}</p>
          </div>
        ))}
      </div>
    </aside>
  )
}
