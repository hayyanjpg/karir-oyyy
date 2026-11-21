import { useEffect, useRef, useState } from 'react'
import { ChevronDown, Download, FileSpreadsheet, FileText } from 'lucide-react'

import LoadingSpinner from './LoadingSpinner'

interface ExportMenuProps {
  loading: 'xlsx' | 'pdf' | null
  onExport: (format: 'xlsx' | 'pdf') => void
}

export default function ExportMenu({ loading, onExport }: ExportMenuProps) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function trigger(format: 'xlsx' | 'pdf') {
    setOpen(false)
    onExport(format)
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        className="btn-secondary"
        onClick={() => setOpen((current) => !current)}
        aria-haspopup="menu"
        aria-expanded={open}
        disabled={loading !== null}
      >
        {loading ? <LoadingSpinner label="Menyiapkan..." size="sm" /> : <Download className="h-4 w-4" aria-hidden="true" />}
        <span>{loading ? 'Menyiapkan...' : 'Download Laporan'}</span>
        <ChevronDown className="h-4 w-4" aria-hidden="true" />
      </button>

      {open && (
        <div
          className="absolute right-0 z-20 mt-2 w-56 overflow-hidden rounded-xl border border-slate-800 bg-slate-900 p-1.5 shadow-2xl"
          role="menu"
        >
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-slate-200 transition hover:bg-slate-800"
            onClick={() => trigger('xlsx')}
            role="menuitem"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-400" aria-hidden="true" />
            <span>
              <span className="block font-medium">Excel (.xlsx)</span>
              <span className="block text-xs text-slate-500">Data + ringkasan statistik</span>
            </span>
          </button>
          <button
            type="button"
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-slate-200 transition hover:bg-slate-800"
            onClick={() => trigger('pdf')}
            role="menuitem"
          >
            <FileText className="h-4 w-4 text-rose-400" aria-hidden="true" />
            <span>
              <span className="block font-medium">PDF (.pdf)</span>
              <span className="block text-xs text-slate-500">Layout landscape siap cetak</span>
            </span>
          </button>
        </div>
      )}
    </div>
  )
}
