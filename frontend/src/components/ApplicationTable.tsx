import { AlertTriangle, ArrowUpDown, ExternalLink, Pencil, Trash2 } from 'lucide-react'

import type { Application, SortField, SortOrder } from '../types'
import { formatDate, relativeDays } from '../utils/format'
import StatusBadge from './StatusBadge'

interface ApplicationTableProps {
  applications: Application[]
  sort: SortField
  order: SortOrder
  onSortChange: (field: SortField) => void
  onEdit: (application: Application) => void
  onDelete: (application: Application) => void
}

function SortButton({
  field,
  label,
  sort,
  order,
  onSortChange,
}: {
  field: SortField
  label: string
  sort: SortField
  order: SortOrder
  onSortChange: (field: SortField) => void
}) {
  const active = sort === field
  return (
    <button
      type="button"
      className={`inline-flex items-center gap-1 transition hover:text-slate-200 ${
        active ? 'text-sky-300' : ''
      }`}
      onClick={() => onSortChange(field)}
    >
      {label}
      <ArrowUpDown className="h-3 w-3" aria-hidden="true" />
      <span className="sr-only">
        {active ? `Urutkan ${order === 'asc' ? 'menurun' : 'menaik'}` : 'Urutkan'}
      </span>
    </button>
  )
}

export default function ApplicationTable({
  applications,
  sort,
  order,
  onSortChange,
  onEdit,
  onDelete,
}: ApplicationTableProps) {
  return (
    <div className="card hidden overflow-hidden md:block">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[880px] text-left text-sm">
          <thead className="border-b border-slate-800 bg-slate-950/60 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">
                <SortButton
                  field="company_name"
                  label="Perusahaan / Posisi"
                  sort={sort}
                  order={order}
                  onSortChange={onSortChange}
                />
              </th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Portal</th>
              <th className="px-4 py-3 font-medium">Model</th>
              <th className="px-4 py-3 font-medium">
                <SortButton
                  field="applied_date"
                  label="Tanggal"
                  sort={sort}
                  order={order}
                  onSortChange={onSortChange}
                />
              </th>
              <th className="px-4 py-3 font-medium">Gaji</th>
              <th className="px-4 py-3 text-right font-medium">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/70">
            {applications.map((application) => (
              <tr key={application.id} className="align-top transition hover:bg-slate-800/30">
                <td className="px-4 py-3.5">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-slate-100">{application.company_name}</span>
                    <span className="text-xs text-slate-500">{application.position_title}</span>
                    {application.needs_follow_up && (
                      <span className="mt-1 inline-flex w-fit items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-300">
                        <AlertTriangle className="h-3 w-3" aria-hidden="true" />
                        Follow up · {relativeDays(application.days_since_update)}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3.5">
                  <StatusBadge status={application.status} />
                </td>
                <td className="px-4 py-3.5 text-slate-400">{application.job_portal}</td>
                <td className="px-4 py-3.5 text-slate-400">{application.work_model}</td>
                <td className="px-4 py-3.5 text-slate-400">{formatDate(application.applied_date)}</td>
                <td className="px-4 py-3.5 text-slate-400">
                  {application.salary_range || '—'}
                </td>
                <td className="px-4 py-3.5">
                  <div className="flex items-center justify-end gap-1">
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
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
