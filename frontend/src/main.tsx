import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'

import App from './App'
import './index.css'

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''
const container = document.getElementById('root')

if (!container) {
  throw new Error('Root element not found')
}

createRoot(container).render(
  <StrictMode>
    {clientId ? (
      <GoogleOAuthProvider clientId={clientId}>
        <App />
      </GoogleOAuthProvider>
    ) : (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6">
        <div className="max-w-md rounded-2xl border border-amber-500/30 bg-amber-500/5 p-6 text-slate-200">
          <h1 className="text-lg font-semibold text-amber-300">Konfigurasi belum lengkap</h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-400">
            Isi <code className="rounded bg-slate-900 px-1.5 py-0.5">VITE_GOOGLE_CLIENT_ID</code>{' '}
            di file <code className="rounded bg-slate-900 px-1.5 py-0.5">.env</code> pada root
            proyek, lalu jalankan ulang <code className="rounded bg-slate-900 px-1.5 py-0.5">npm run dev</code>.
          </p>
        </div>
      </main>
    )}
  </StrictMode>,
)
