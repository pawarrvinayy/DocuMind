import { useRef, useState } from 'react'
import { uploadDocument } from '../services/documents'
import type { Document } from '../types'

interface Props {
  onUploaded: (doc: Document) => void
}

export default function PdfUploader({ onUploaded }: Props) {
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState<number | null>(null)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported')
      return
    }
    setError('')
    setProgress(0)
    try {
      const doc = await uploadDocument(file, setProgress)
      onUploaded(doc)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Upload failed')
    } finally {
      setProgress(null)
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <div className="p-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors ${
          dragging
            ? 'border-indigo-500 bg-indigo-500/10'
            : 'border-zinc-700 hover:border-zinc-500 hover:bg-zinc-800/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
        <svg className="w-6 h-6 mx-auto text-zinc-500 mb-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        <p className="text-xs text-zinc-400">
          {progress !== null ? 'Uploading…' : 'Drop PDF or click'}
        </p>
      </div>

      {progress !== null && (
        <div className="mt-2">
          <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-zinc-500 mt-1 text-right">{progress}%</p>
        </div>
      )}

      {error && (
        <p className="text-xs text-red-400 mt-2 bg-red-400/10 rounded-lg px-2 py-1.5">{error}</p>
      )}
    </div>
  )
}
