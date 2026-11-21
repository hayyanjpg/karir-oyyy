import type { ReactNode } from 'react'

interface KpiCardProps {
  label: string
  value: string | number
  hint: string
  icon: ReactNode
  accent: 'sky' | 'emerald' | 'amber' | 'violet'
}

const ACCENTS = {
  sky: 'border-sky-500/20 bg-sky-500/10 text-sky-300',
  emerald: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300',
  amber: 'border-amber-500/20 bg-amber-500/10 text-amber-300',
  violet: 'border-violet-500/20 bg-violet-500/10 text-violet-300',
}

export default function KpiCard({ label, value, hint, icon, accent }: KpiCardProps) {
  return (
    <article className="card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-white">{value}</p>
        </div>
        <span className={`rounded-xl border p-2.5 ${ACCENTS[accent]}`} aria-hidden="true">
          {icon}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-500">{hint}</p>
    </article>
  )
}
