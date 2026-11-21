import type { ApplicationStatus } from '../types'

const STYLES: Record<ApplicationStatus, string> = {
  Applied: 'border-sky-500/30 bg-sky-500/10 text-sky-300',
  Screening: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-300',
  'Technical Test': 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  'HR Interview': 'border-orange-500/30 bg-orange-500/10 text-orange-300',
  'User Interview': 'border-yellow-500/30 bg-yellow-500/10 text-yellow-300',
  Offering: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  Rejected: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
  Ghosted: 'border-slate-500/30 bg-slate-500/10 text-slate-300',
}

export default function StatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-medium ${STYLES[status]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {status}
    </span>
  )
}
