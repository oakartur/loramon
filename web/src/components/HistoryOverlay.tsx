'use client'
import { useEffect } from 'react'

interface Props {
  open: boolean
  title?: string
  onClose: () => void
  children?: React.ReactNode
}

export default function HistoryOverlay({ open, title = 'Histórico', onClose, children }: Props) {
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-40 bg-black/40">
      <div
        className="absolute right-0 top-0 h-full w-full sm:w-[640px] bg-white shadow-2xl p-4 overflow-auto"
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold">{title}</h2>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200 text-sm"
          >
            Fechar (Esc)
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  )
}
