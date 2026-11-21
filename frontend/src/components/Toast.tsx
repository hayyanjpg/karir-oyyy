import { useEffect } from 'react'
import { AlertCircle, CheckCircle2, X } from 'lucide-react'

export type ToastType = 'success' | 'error'

interface ToastProps {
  message: string
  type: ToastType
  onClose: () => void
}

export default function Toast({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = window.setTimeout(onClose, 4500)
    return () => window.clearTimeout(timer)
  }, [message, onClose])

  const isSuccess = type === 'success'

  return (
    <div
      className={`fixed bottom-5 right-5 z-[60] flex max-w-sm items-start gap-3 rounded-xl border px-4 py-3 shadow-2xl ${
        isSuccess
          ? 'border-emerald-500/30 bg-emerald-950/90 text-emerald-100'
          : 'border-rose-500/30 bg-rose-950/90 text-rose-100'
      }`}
      role="status"
    >
      {isSuccess ? (
        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      ) : (
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      )}
      <p className="text-sm leading-relaxed">{message}</p>
      <button
        type="button"
        onClick={onClose}
        className="rounded-md p-1 opacity-70 transition hover:bg-white/10 hover:opacity-100"
        aria-label="Tutup notifikasi"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  )
}
