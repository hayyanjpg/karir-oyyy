import type { ReactNode } from 'react'
import { Inbox } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description: string
  action?: ReactNode
}

export default function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 px-6 py-14 text-center">
      <span className="rounded-2xl border border-slate-800 bg-slate-900 p-3 text-slate-500">
        <Inbox className="h-6 w-6" aria-hidden="true" />
      </span>
      <h3 className="text-base font-semibold text-slate-200">{title}</h3>
      <p className="max-w-md text-sm leading-relaxed text-slate-500">{description}</p>
      {action}
    </div>
  )
}
