import { useEffect, useState } from 'react'
import { listDocuments, deleteDocument } from '../services/documents'
import PdfUploader from './PdfUploader'
import type { Document } from '../types'

interface Props {
  activeDocId: number | null
  onSelect: (id: number | null) => void
}

export default function Sidebar({ activeDocId, onSelect }: Props) {
  const [docs, setDocs] = useState<Document[]>([])
  const [deletingId, setDeletingId] = useState<number | null>(null)

  useEffect(() => {
    listDocuments().then(setDocs).catch(() => {})
  }, [])

  async function handleDelete(e: React.MouseEvent, id: number) {
    e.stopPropagation()
    setDeletingId(id)
    try {
      await deleteDocument(id)
      setDocs((prev) => prev.filter((d) => d.id !== id))
      if (activeDocId === id) onSelect(null)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <aside className="w-64 bg-zinc-900 border-r border-zinc-800 flex flex-col shrink-0">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Documents</h2>
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto py-2">
        {docs.length === 0 ? (
          <p className="text-xs text-zinc-600 text-center mt-8 px-4">
            No documents yet. Upload a PDF to get started.
          </p>
        ) : (
          <>
            {/* "All documents" option */}
            <button
              onClick={() => onSelect(null)}
              className={`w-full flex items-center gap-2 px-3 py-2 text-left text-sm transition-colors group ${
                activeDocId === null
                  ? 'bg-indigo-600/20 text-indigo-400'
                  : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100'
              }`}
            >
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="truncate">All documents</span>
            </button>

            {docs.map((doc) => (
              <button
                key={doc.id}
                onClick={() => onSelect(doc.id)}
                className={`w-full flex items-center gap-2 px-3 py-2 text-left text-sm transition-colors group ${
                  activeDocId === doc.id
                    ? 'bg-indigo-600/20 text-indigo-400'
                    : 'text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100'
                }`}
              >
                <svg className="w-4 h-4 shrink-0 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span className="truncate flex-1">{doc.filename}</span>
                <span
                  role="button"
                  onClick={(e) => handleDelete(e, doc.id)}
                  className={`opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-400 transition-opacity p-0.5 rounded ${
                    deletingId === doc.id ? 'opacity-100 animate-pulse' : ''
                  }`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </span>
              </button>
            ))}
          </>
        )}
      </div>

      {/* Uploader */}
      <div className="border-t border-zinc-800">
        <PdfUploader onUploaded={(doc) => setDocs((prev) => [doc, ...prev])} />
      </div>
    </aside>
  )
}
