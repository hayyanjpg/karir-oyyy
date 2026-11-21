import { AlertTriangle } from 'lucide-react'

import LoadingSpinner from './LoadingSpinner'

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  loading?: boolean
  onCancel: () => void
  onConfirm: () => void
}

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Hapus',
  loading = false,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !loading) onCancel()
      }}
    >
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-start gap-3">
          <span className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-2.5 text-rose-300">
            <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 id="confirm-dialog-title" className="text-base font-semibold text-white">
              {title}
            </h2>
            <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{message}</p>
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <button type="button" className="btn-secondary" onClick={onCancel} disabled={loading}>
            Batal
          </button>
          <button type="button" className="btn-danger" onClick={onConfirm} disabled={loading}>
            {loading ? <LoadingSpinner label={confirmLabel} size="sm" /> : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
