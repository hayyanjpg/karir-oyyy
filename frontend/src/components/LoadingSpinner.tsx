import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

const SIZES = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-9 w-9',
}

export default function LoadingSpinner({ label = 'Memuat...', size = 'md' }: LoadingSpinnerProps) {
  return (
    <div className="flex items-center justify-center gap-3 text-slate-400" role="status">
      <Loader2 className={`${SIZES[size]} animate-spin text-sky-400`} aria-hidden="true" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
