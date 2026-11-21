import { useEffect, useState, type FormEvent } from 'react'
import { X } from 'lucide-react'

import { getErrorMessage } from '../services/api'
import {
  PORTAL_OPTIONS,
  STATUS_OPTIONS,
  WORK_MODEL_OPTIONS,
  type Application,
  type ApplicationInput,
  type ApplicationStatus,
  type JobPortal,
  type WorkModel,
} from '../types'
import LoadingSpinner from './LoadingSpinner'

interface ApplicationModalProps {
  open: boolean
  initial: Application | null
  saving: boolean
  onClose: () => void
  onSubmit: (payload: ApplicationInput) => Promise<void>
}

const EMPTY_FORM: ApplicationInput = {
  company_name: '',
  position_title: '',
  status: 'Applied',
  applied_date: new Date().toISOString().slice(0, 10),
  job_portal: 'Lainnya',
  work_model: 'WFO',
  salary_range: '',
  job_url: '',
  notes: '',
}

function toForm(application: Application): ApplicationInput {
  return {
    company_name: application.company_name,
    position_title: application.position_title,
    status: application.status,
    applied_date: application.applied_date,
    job_portal: application.job_portal,
    work_model: application.work_model,
    salary_range: application.salary_range ?? '',
    job_url: application.job_url ?? '',
    notes: application.notes ?? '',
  }
}

export default function ApplicationModal({
  open,
  initial,
  saving,
  onClose,
  onSubmit,
}: ApplicationModalProps) {
  const [form, setForm] = useState<ApplicationInput>(EMPTY_FORM)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    setForm(initial ? toForm(initial) : EMPTY_FORM)
    setError(null)
  }, [open, initial])

  useEffect(() => {
    if (!open) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape' && !saving) onClose()
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [open, saving, onClose])

  if (!open) return null

  function updateField<K extends keyof ApplicationInput>(key: K, value: ApplicationInput[K]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!form.company_name.trim() || !form.position_title.trim()) {
      setError('Nama perusahaan dan posisi wajib diisi.')
      return
    }
    if (form.job_url && !/^https?:\/\//i.test(form.job_url.trim())) {
      setError('URL lowongan harus diawali http:// atau https://')
      return
    }

    setError(null)
    try {
      await onSubmit({
        ...form,
        company_name: form.company_name.trim(),
        position_title: form.position_title.trim(),
        salary_range: form.salary_range?.trim() || null,
        job_url: form.job_url?.trim() || null,
        notes: form.notes?.trim() || null,
      })
    } catch (submitError) {
      setError(getErrorMessage(submitError))
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/80 p-4 backdrop-blur-sm sm:items-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="application-modal-title"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !saving) onClose()
      }}
    >
      <div className="my-6 w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
          <div>
            <h2 id="application-modal-title" className="text-base font-semibold text-white">
              {initial ? 'Edit Lamaran' : 'Tambah Lamaran'}
            </h2>
            <p className="mt-0.5 text-xs text-slate-500">
              Catat detail lowongan dan progresnya.
            </p>
          </div>
          <button
            type="button"
            className="btn-ghost"
            onClick={onClose}
            disabled={saving}
            aria-label="Tutup form"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 px-5 py-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="company_name">
                Nama Perusahaan *
              </label>
              <input
                id="company_name"
                className="input"
                value={form.company_name}
                onChange={(event) => updateField('company_name', event.target.value)}
                placeholder="Contoh: Tokopedia"
                autoFocus
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="position_title">
                Posisi *
              </label>
              <input
                id="position_title"
                className="input"
                value={form.position_title}
                onChange={(event) => updateField('position_title', event.target.value)}
                placeholder="Contoh: Frontend Engineer"
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="status">
                Status
              </label>
              <select
                id="status"
                className="input"
                value={form.status}
                onChange={(event) =>
                  updateField('status', event.target.value as ApplicationStatus)
                }
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="applied_date">
                Tanggal Melamar *
              </label>
              <input
                id="applied_date"
                type="date"
                className="input"
                value={form.applied_date}
                onChange={(event) => updateField('applied_date', event.target.value)}
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="job_portal">
                Portal Lowongan
              </label>
              <select
                id="job_portal"
                className="input"
                value={form.job_portal}
                onChange={(event) => updateField('job_portal', event.target.value as JobPortal)}
              >
                {PORTAL_OPTIONS.map((portal) => (
                  <option key={portal} value={portal}>
                    {portal}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="work_model">
                Model Kerja
              </label>
              <select
                id="work_model"
                className="input"
                value={form.work_model}
                onChange={(event) =>
                  updateField('work_model', event.target.value as WorkModel)
                }
              >
                {WORK_MODEL_OPTIONS.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="salary_range">
                Rentang Gaji
              </label>
              <input
                id="salary_range"
                className="input"
                value={form.salary_range ?? ''}
                onChange={(event) => updateField('salary_range', event.target.value)}
                placeholder="Contoh: IDR 8-12 juta"
              />
            </div>
            <div>
              <label className="label" htmlFor="job_url">
                URL Lowongan
              </label>
              <input
                id="job_url"
                type="url"
                className="input"
                value={form.job_url ?? ''}
                onChange={(event) => updateField('job_url', event.target.value)}
                placeholder="https://..."
              />
            </div>
          </div>

          <div>
            <label className="label" htmlFor="notes">
              Catatan
            </label>
            <textarea
              id="notes"
              className="input min-h-24 resize-y"
              rows={4}
              value={form.notes ?? ''}
              onChange={(event) => updateField('notes', event.target.value)}
              placeholder="Informasi kontak recruiter, jadwal interview, dsb."
            />
          </div>

          {error && (
            <p className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
              {error}
            </p>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-800 pt-4">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={saving}>
              Batal
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? <LoadingSpinner label="Menyimpan..." size="sm" /> : 'Simpan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
