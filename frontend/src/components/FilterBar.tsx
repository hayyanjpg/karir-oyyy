import { RotateCcw, Search } from 'lucide-react'

import {
  PORTAL_OPTIONS,
  STATUS_OPTIONS,
  WORK_MODEL_OPTIONS,
  type ApplicationFilters,
  type ApplicationStatus,
  type JobPortal,
  type WorkModel,
} from '../types'

interface FilterBarProps {
  search: string
  filters: ApplicationFilters
  onSearchChange: (value: string) => void
  onFiltersChange: (patch: Partial<ApplicationFilters>) => void
  onReset: () => void
}

export default function FilterBar({
  search,
  filters,
  onSearchChange,
  onFiltersChange,
  onReset,
}: FilterBarProps) {
  return (
    <section className="card p-4" aria-label="Filter lamaran">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
        <div className="sm:col-span-2">
          <label className="label" htmlFor="filter-search">
            Cari
          </label>
          <div className="relative">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500"
              aria-hidden="true"
            />
            <input
              id="filter-search"
              type="search"
              className="input pl-9"
              placeholder="Perusahaan atau posisi..."
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label" htmlFor="filter-status">
            Status
          </label>
          <select
            id="filter-status"
            className="input"
            value={filters.status ?? ''}
            onChange={(event) =>
              onFiltersChange({
                status: (event.target.value || undefined) as ApplicationStatus | undefined,
              })
            }
          >
            <option value="">Semua status</option>
            {STATUS_OPTIONS.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label" htmlFor="filter-work-model">
            Model Kerja
          </label>
          <select
            id="filter-work-model"
            className="input"
            value={filters.work_model ?? ''}
            onChange={(event) =>
              onFiltersChange({
                work_model: (event.target.value || undefined) as WorkModel | undefined,
              })
            }
          >
            <option value="">Semua model</option>
            {WORK_MODEL_OPTIONS.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label" htmlFor="filter-portal">
            Portal
          </label>
          <select
            id="filter-portal"
            className="input"
            value={filters.job_portal ?? ''}
            onChange={(event) =>
              onFiltersChange({
                job_portal: (event.target.value || undefined) as JobPortal | undefined,
              })
            }
          >
            <option value="">Semua portal</option>
            {PORTAL_OPTIONS.map((portal) => (
              <option key={portal} value={portal}>
                {portal}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label" htmlFor="filter-start-date">
            Dari Tanggal
          </label>
          <input
            id="filter-start-date"
            type="date"
            className="input"
            value={filters.start_date ?? ''}
            onChange={(event) =>
              onFiltersChange({ start_date: event.target.value || undefined })
            }
          />
        </div>

        <div>
          <label className="label" htmlFor="filter-end-date">
            Sampai Tanggal
          </label>
          <input
            id="filter-end-date"
            type="date"
            className="input"
            value={filters.end_date ?? ''}
            onChange={(event) =>
              onFiltersChange({ end_date: event.target.value || undefined })
            }
          />
        </div>

        <div className="flex items-end sm:col-span-2 lg:col-span-6">
          <button type="button" className="btn-secondary w-full sm:w-auto" onClick={onReset}>
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
            Reset filter
          </button>
        </div>
      </div>
    </section>
  )
}
