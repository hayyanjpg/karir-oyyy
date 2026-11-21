import { AlertTriangle, ExternalLink, Pencil, Trash2 } from 'lucide-react'

import type { Application } from '../types'
import { formatDate, relativeDays } from '../utils/format'
import StatusBadge from './StatusBadge'

interface ApplicationCardProps {
  application: Application
  onEdit: (application: Application) => void
  onDelete: (application: Application) => void
}

export default function ApplicationCard({
  application,
  onEdit,
  onDelete,
}: ApplicationCardProps) {
  return (
    <article className="card p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-medium text-slate-100">{application.company_name}</h3>
          <p className="mt-0.5 text-sm text-slate-400">{application.position_title}</p>
        </div>
        <StatusBadge status={application.status} />
      </div>

      {application.needs_follow_up && (
        <p className="mt-3 inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300">
          <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
          Follow up · {relativeDays(application.days_since_update)}
        </p>
      )}

      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-slate-500">Portal</dt>
          <dd className="mt-0.5 text-slate-300">{application.job_portal}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Model kerja</dt>
          <dd className="mt-0.5 text-slate-300">{application.work_model}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Tanggal melamar</dt>
          <dd className="mt-0.5 text-slate-300">{formatDate(application.applied_date)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Gaji</dt>
          <dd className="mt-0.5 text-slate-300">{application.salary_range || '—'}</dd>
        </div>
      </dl>

      {application.notes && (
        <p className="mt-3 line-clamp-2 text-xs leading-relaxed text-slate-500">
          {application.notes}
        </p>
      )}

      <div className="mt-4 flex items-center justify-end gap-1 border-t border-slate-800 pt-3">
        {application.job_url && (
          <a
            href={application.job_url}
            target="_blank"
            rel="noreferrer noopener"
            className="btn-ghost"
            aria-label={`Buka lowongan ${application.company_name}`}
          >
            <ExternalLink className="h-4 w-4" aria-hidden="true" />
          </a>
        )}
        <button
          type="button"
          className="btn-ghost"
          onClick={() => onEdit(application)}
          aria-label={`Edit lamaran ${application.company_name}`}
        >
          <Pencil className="h-4 w-4" aria-hidden="true" />
        </button>
        <button
          type="button"
          className="btn-ghost hover:bg-rose-500/10 hover:text-rose-300"
          onClick={() => onDelete(application)}
          aria-label={`Hapus lamaran ${application.company_name}`}
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </article>
  )
}
