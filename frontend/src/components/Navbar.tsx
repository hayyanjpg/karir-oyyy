import { BriefcaseBusiness, LogOut } from 'lucide-react'

import type { User } from '../types'

interface NavbarProps {
  user: User
  loggingOut: boolean
  onLogout: () => void
}

function initials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

export default function Navbar({ user, loggingOut, onLogout }: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <span className="rounded-xl border border-sky-500/30 bg-sky-500/10 p-2 text-sky-300">
            <BriefcaseBusiness className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <p className="text-sm font-semibold tracking-tight text-white">KarirTrack</p>
            <p className="hidden text-xs text-slate-500 sm:block">Job Application Tracker</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                referrerPolicy="no-referrer"
                className="h-9 w-9 rounded-full border border-slate-700 object-cover"
              />
            ) : (
              <span className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-200">
                {initials(user.full_name)}
              </span>
            )}
            <div className="hidden sm:block">
              <p className="max-w-[180px] truncate text-sm font-medium text-slate-200">
                {user.full_name}
              </p>
              <p className="max-w-[180px] truncate text-xs text-slate-500">{user.email}</p>
            </div>
          </div>
          <button
            type="button"
            className="btn-ghost"
            onClick={onLogout}
            disabled={loggingOut}
            aria-label="Keluar"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">{loggingOut ? 'Keluar...' : 'Keluar'}</span>
          </button>
        </div>
      </div>
    </header>
  )
}
