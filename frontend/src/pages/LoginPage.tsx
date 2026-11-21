import { useState } from 'react'
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google'
import {
  BarChart3,
  BriefcaseBusiness,
  FileSpreadsheet,
  ShieldCheck,
} from 'lucide-react'
import { Navigate, useNavigate } from 'react-router-dom'

import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../services/api'

const FEATURES = [
  {
    icon: BarChart3,
    title: 'Dashboard analitik',
    description: 'Pantau KPI, funnel status, dan sumber lowongan dalam satu tampilan.',
  },
  {
    icon: FileSpreadsheet,
    title: 'Export Excel & PDF',
    description: 'Unduh laporan rapi sesuai filter yang sedang aktif.',
  },
  {
    icon: ShieldCheck,
    title: 'Data terisolasi',
    description: 'Setiap akun hanya bisa mengakses lamaran miliknya sendiri.',
  },
]

export default function LoginPage() {
  const { user, loading, loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <LoadingSpinner label="Memeriksa sesi..." />
      </div>
    )
  }

  if (user) {
    return <Navigate to="/" replace />
  }

  async function handleSuccess(response: CredentialResponse) {
    if (!response.credential) {
      setError('Google tidak mengembalikan credential. Coba lagi.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await loginWithGoogle(response.credential)
      navigate('/', { replace: true })
    } catch (loginError) {
      setError(getErrorMessage(loginError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10 sm:px-6">
      <div
        className="pointer-events-none absolute -left-32 top-1/4 h-72 w-72 rounded-full bg-sky-500/10 blur-3xl"
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute -right-24 bottom-0 h-80 w-80 rounded-full bg-violet-500/10 blur-3xl"
        aria-hidden="true"
      />

      <div className="relative grid w-full max-w-5xl gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
        <section className="space-y-8">
          <div className="flex items-center gap-3">
            <span className="rounded-2xl border border-sky-500/30 bg-sky-500/10 p-3 text-sky-300">
              <BriefcaseBusiness className="h-6 w-6" aria-hidden="true" />
            </span>
            <div>
              <p className="text-lg font-semibold tracking-tight text-white">KarirTrack</p>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                Job Application Tracker
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h1 className="max-w-xl text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl">
              Kelola proses lamaran kerja tanpa kehilangan jejak.
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-slate-400">
              Catat setiap lamaran, pantau progres interview, dan unduh laporan dalam format
              Excel atau PDF. Semua dalam satu dashboard gelap yang nyaman dipakai.
            </p>
          </div>

          <ul className="grid gap-3 sm:grid-cols-3">
            {FEATURES.map((feature) => (
              <li key={feature.title} className="card p-4">
                <feature.icon className="h-5 w-5 text-sky-400" aria-hidden="true" />
                <p className="mt-3 text-sm font-medium text-slate-200">{feature.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-500">
                  {feature.description}
                </p>
              </li>
            ))}
          </ul>
        </section>

        <section className="card p-6 sm:p-8">
          <div className="space-y-2">
            <h2 className="text-xl font-semibold text-white">Masuk ke KarirTrack</h2>
            <p className="text-sm leading-relaxed text-slate-400">
              Gunakan akun Google. Tidak perlu membuat password baru.
            </p>
          </div>

          <div className="relative mt-7">
            <div className={submitting ? 'pointer-events-none opacity-60' : ''}>
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => setError('Login Google dibatalkan atau gagal.')}
                theme="filled_black"
                size="large"
                shape="pill"
                text="signin_with"
                logo_alignment="left"
                width="320"
              />
            </div>
            {submitting && (
              <div className="absolute inset-0 flex items-center justify-center">
                <LoadingSpinner label="Menghubungkan..." size="sm" />
              </div>
            )}
          </div>

          {error && (
            <p className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">
              {error}
            </p>
          )}

          <p className="mt-6 text-xs leading-relaxed text-slate-500">
            Dengan masuk, kamu menyetujui penggunaan data profil Google (nama, email, foto)
            hanya untuk keperluan autentikasi dan tampilan aplikasi.
          </p>
        </section>
      </div>
    </main>
  )
}
