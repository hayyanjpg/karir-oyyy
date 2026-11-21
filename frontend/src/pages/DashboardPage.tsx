import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  Award,
  Briefcase,
  Plus,
  RefreshCw,
  TrendingUp,
} from 'lucide-react'

import ApplicationCard from '../components/ApplicationCard'
import ApplicationModal from '../components/ApplicationModal'
import ApplicationTable from '../components/ApplicationTable'
import ConfirmDialog from '../components/ConfirmDialog'
import EmptyState from '../components/EmptyState'
import ExportMenu from '../components/ExportMenu'
import FilterBar from '../components/FilterBar'
import KpiCard from '../components/KpiCard'
import LoadingSpinner from '../components/LoadingSpinner'
import Navbar from '../components/Navbar'
import PortalChart from '../components/PortalChart'
import StatusChart from '../components/StatusChart'
import Toast, { type ToastType } from '../components/Toast'
import { useAuth } from '../context/AuthContext'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import {
  createApplication,
  deleteApplication,
  fetchAnalytics,
  fetchApplications,
  updateApplication,
} from '../services/applications'
import { getErrorMessage } from '../services/api'
import { downloadReport } from '../services/reports'
import type {
  AnalyticsSummary,
  Application,
  ApplicationFilters,
  ApplicationInput,
  ApplicationPage,
  SortField,
  SortOrder,
} from '../types'

const PAGE_SIZE = 10

export default function DashboardPage() {
  const { user, logout } = useAuth()

  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [pageData, setPageData] = useState<ApplicationPage | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [search, setSearch] = useState('')
  const debouncedSearch = useDebouncedValue(search)
  const [filters, setFilters] = useState<ApplicationFilters>({})
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState<SortField>('applied_date')
  const [order, setOrder] = useState<SortOrder>('desc')

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Application | null>(null)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<Application | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [exporting, setExporting] = useState<'xlsx' | 'pdf' | null>(null)
  const [loggingOut, setLoggingOut] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null)

  const effectiveFilters = useMemo<ApplicationFilters>(
    () => ({ ...filters, search: debouncedSearch.trim() || undefined }),
    [filters, debouncedSearch],
  )

  const load = useCallback(
    async (showSpinner = true) => {
      if (showSpinner) setLoading(true)
      try {
        const [summaryData, applications] = await Promise.all([
          fetchAnalytics(),
          fetchApplications(effectiveFilters, page, PAGE_SIZE, sort, order),
        ])
        setSummary(summaryData)
        setPageData(applications)
        setError(null)
      } catch (loadError) {
        setError(getErrorMessage(loadError))
      } finally {
        if (showSpinner) setLoading(false)
      }
    },
    [effectiveFilters, page, sort, order],
  )

  useEffect(() => {
    void load()
  }, [load])

  const closeToast = useCallback(() => setToast(null), [])

  function handleFiltersChange(patch: Partial<ApplicationFilters>) {
    setFilters((current) => {
      const next: ApplicationFilters = { ...current, ...patch }
      for (const key of Object.keys(next) as Array<keyof ApplicationFilters>) {
        if (next[key] === undefined) delete next[key]
      }
      return next
    })
    setPage(1)
  }

  function handleReset() {
    setSearch('')
    setFilters({})
    setPage(1)
  }

  function handleSortChange(field: SortField) {
    if (sort === field) {
      setOrder((current) => (current === 'asc' ? 'desc' : 'asc'))
    } else {
      setSort(field)
      setOrder(field === 'company_name' ? 'asc' : 'desc')
    }
    setPage(1)
  }

  async function handleRefresh() {
    setRefreshing(true)
    await load(false)
    setRefreshing(false)
  }

  function openCreate() {
    setEditing(null)
    setModalOpen(true)
  }

  function openEdit(application: Application) {
    setEditing(application)
    setModalOpen(true)
  }

  async function handleSubmit(payload: ApplicationInput) {
    setSaving(true)
    try {
      if (editing) {
        await updateApplication(editing.id, payload)
        setToast({ message: 'Lamaran berhasil diperbarui.', type: 'success' })
      } else {
        await createApplication(payload)
        setToast({ message: 'Lamaran baru berhasil ditambahkan.', type: 'success' })
      }
      setModalOpen(false)
      setEditing(null)
      await load(false)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!deleting) return
    setDeleteLoading(true)
    try {
      await deleteApplication(deleting.id)
      setToast({ message: 'Lamaran berhasil dihapus.', type: 'success' })
      setDeleting(null)
      await load(false)
    } catch (deleteError) {
      setToast({ message: getErrorMessage(deleteError), type: 'error' })
    } finally {
      setDeleteLoading(false)
    }
  }

  async function handleExport(format: 'xlsx' | 'pdf') {
    setExporting(format)
    try {
      await downloadReport(format, effectiveFilters)
      setToast({
        message: `Laporan ${format.toUpperCase()} berhasil diunduh.`,
        type: 'success',
      })
    } catch (exportError) {
      setToast({ message: getErrorMessage(exportError), type: 'error' })
    } finally {
      setExporting(null)
    }
  }

  async function handleLogout() {
    setLoggingOut(true)
    try {
      await logout()
    } finally {
      setLoggingOut(false)
    }
  }

  if (!user) return null

  if (loading && !summary) {
    return (
      <div className="min-h-screen bg-slate-950">
        <Navbar user={user} loggingOut={loggingOut} onLogout={handleLogout} />
        <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6">
          <LoadingSpinner label="Memuat dashboard..." size="lg" />
        </div>
      </div>
    )
  }

  const applications = pageData?.items ?? []
  const kpi = summary?.kpi

  return (
    <div className="min-h-screen">
      <Navbar user={user} loggingOut={loggingOut} onLogout={handleLogout} />

      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6 sm:py-8">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-sky-400">
              Dashboard
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
              Halo, {user.full_name.split(' ')[0]} 👋
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Ringkasan progres lamaran dan aktivitas terbaru.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => void handleRefresh()}
              disabled={refreshing}
            >
              <RefreshCw
                className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`}
                aria-hidden="true"
              />
              {refreshing ? 'Memuat...' : 'Refresh'}
            </button>
            <ExportMenu loading={exporting} onExport={(format) => void handleExport(format)} />
            <button type="button" className="btn-primary" onClick={openCreate}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Tambah Lamaran
            </button>
          </div>
        </header>

        {error && (
          <div className="flex flex-col gap-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-100 sm:flex-row sm:items-center sm:justify-between">
            <p>{error}</p>
            <button type="button" className="btn-secondary" onClick={() => void load()}>
              Coba lagi
            </button>
          </div>
        )}

        {summary && summary.follow_up.length > 0 && (
          <div className="flex items-start gap-3 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-amber-100">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
            <div>
              <p className="text-sm font-medium">
                {summary.follow_up.length} lamaran perlu ditindaklanjuti
              </p>
              <p className="mt-0.5 text-xs leading-relaxed text-amber-200/80">
                Status Applied/Screening tanpa update lebih dari 14 hari. Cek kembali
                progresnya.
              </p>
            </div>
          </div>
        )}

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="KPI">
          <KpiCard
            label="Total Lamaran"
            value={kpi?.total ?? 0}
            hint="Semua lamaran yang tercatat"
            icon={<Briefcase className="h-5 w-5" aria-hidden="true" />}
            accent="sky"
          />
          <KpiCard
            label="Active Pipeline"
            value={kpi?.active_pipeline ?? 0}
            hint="Belum Offering, Rejected, atau Ghosted"
            icon={<Activity className="h-5 w-5" aria-hidden="true" />}
            accent="violet"
          />
          <KpiCard
            label="Interview Rate"
            value={`${kpi?.interview_rate ?? 0}%`}
            hint={`${kpi?.interview_count ?? 0} lamaran pernah masuk tahap interview`}
            icon={<TrendingUp className="h-5 w-5" aria-hidden="true" />}
            accent="amber"
          />
          <KpiCard
            label="Offering"
            value={kpi?.offerings ?? 0}
            hint={`${kpi?.rejected ?? 0} rejected · ${kpi?.ghosted ?? 0} ghosted`}
            icon={<Award className="h-5 w-5" aria-hidden="true" />}
            accent="emerald"
          />
        </section>

        <section className="grid gap-4 lg:grid-cols-2" aria-label="Grafik">
          <div className="card p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold text-slate-200">Distribusi Status</h2>
              <p className="text-xs text-slate-500">Jumlah lamaran pada setiap tahap saat ini.</p>
            </div>
            <StatusChart data={summary?.by_status ?? []} />
          </div>
          <div className="card p-5">
            <div className="mb-3">
              <h2 className="text-sm font-semibold text-slate-200">Sumber Lowongan</h2>
              <p className="text-xs text-slate-500">Proporsi lamaran berdasarkan portal.</p>
            </div>
            <PortalChart data={summary?.by_portal ?? []} />
          </div>
        </section>

        <FilterBar
          search={search}
          filters={filters}
          onSearchChange={(value) => {
            setSearch(value)
            setPage(1)
          }}
          onFiltersChange={handleFiltersChange}
          onReset={handleReset}
        />

        <section className="space-y-4" aria-label="Daftar lamaran">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-white">Daftar Lamaran</h2>
              <p className="text-xs text-slate-500">
                {pageData?.total ?? 0} lamaran ditemukan
                {effectiveFilters.search ? ` untuk "${effectiveFilters.search}"` : ''}.
              </p>
            </div>
          </div>

          {loading ? (
            <div className="card py-16">
              <LoadingSpinner label="Memuat lamaran..." />
            </div>
          ) : applications.length === 0 ? (
            <EmptyState
              title="Belum ada lamaran"
              description="Mulai catat lamaran pertamamu, atau ubah filter jika data sebenarnya ada."
              action={
                <button type="button" className="btn-primary mt-2" onClick={openCreate}>
                  <Plus className="h-4 w-4" aria-hidden="true" />
                  Tambah Lamaran
                </button>
              }
            />
          ) : (
            <>
              <ApplicationTable
                applications={applications}
                sort={sort}
                order={order}
                onSortChange={handleSortChange}
                onEdit={openEdit}
                onDelete={setDeleting}
              />
              <div className="space-y-3 md:hidden">
                {applications.map((application) => (
                  <ApplicationCard
                    key={application.id}
                    application={application}
                    onEdit={openEdit}
                    onDelete={setDeleting}
                  />
                ))}
              </div>
            </>
          )}

          {pageData && pageData.pages > 1 && (
            <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
              <p className="text-xs text-slate-500">
                Halaman {pageData.page} dari {pageData.pages}
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                  disabled={pageData.page <= 1}
                >
                  Sebelumnya
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setPage((current) => current + 1)}
                  disabled={pageData.page >= pageData.pages}
                >
                  Berikutnya
                </button>
              </div>
            </div>
          )}
        </section>
      </main>

      <ApplicationModal
        open={modalOpen}
        initial={editing}
        saving={saving}
        onClose={() => {
          if (!saving) {
            setModalOpen(false)
            setEditing(null)
          }
        }}
        onSubmit={handleSubmit}
      />

      <ConfirmDialog
        open={deleting !== null}
        title="Hapus lamaran?"
        message={
          deleting
            ? `Lamaran di ${deleting.company_name} akan dihapus permanen. Tindakan ini tidak bisa dibatalkan.`
            : ''
        }
        loading={deleteLoading}
        onCancel={() => setDeleting(null)}
        onConfirm={() => void handleDelete()}
      />

      {toast && <Toast message={toast.message} type={toast.type} onClose={closeToast} />}
    </div>
  )
}
